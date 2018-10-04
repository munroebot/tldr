import requests, json, os, boto3

from datetime import datetime, date
from html.parser import HTMLParser
from botocore.exceptions import ClientError

from local_config import *

pp_username = os.environ['PP_USERNAME']
pp_password = os.environ['PP_PASSWORD']
ar_username = os.environ['AR_USERNAME']
ar_password = os.environ['AR_PASSWORD']
recipients = os.environ['RECIPIENTS'].split(";")

class ArHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.recording = 0
        self.data = None

    def handle_starttag(self, tag, attributes):
        if tag != 'span':
            return
        if self.recording:
            self.recording += 1
            return
        for name, value in attributes:
            if name == 'id' and value == 'ctl00_ContentPlaceHolder_Content_mBox_Progress_mSpan_Points':
                break
            else:
                return

        self.recording = 1

    def handle_endtag(self, tag):
        if tag == 'span' and self.recording:
            self.recording -= 1

    def handle_data(self, data):
        if self.recording:
            self.data = data


# Get Plus Portals Assignments
def get_assignments():
    pp_login_data = {'UserName':pp_username,'Password':pp_password}
    r = requests.post(pp_login_url, data=pp_login_data, allow_redirects=False)
    r2 = requests.get(pp_assignments_url,cookies=r.cookies)
    x = json.loads(r2.text)

    d0 = date.today()

    assignments = []

    for j in x['Data']:
        d1 = datetime.strptime(j['DueDate'], '%m-%d-%Y').date()
        if d1 >= d0:
            assignments.append(j)

    return assignments

# Get a short summary (for top of email)
def get_assignments_summary(data=None):
    assignments_summary = ""
    for x in data:
        assignments_summary += ("{} - {}\n".format(x["DueDate"],x["Title"]))

    return assignments_summary

# Get a long format (for the bottom of email)
def get_assignments_longform(data=None):
    assignments_longform = ""
    for x in data:
        assignments_longform += ("{}\n{}\n{}\n\n".format(x["DueDate"], x["Title"], x["Description"]))

    return assignments_longform

# Grab AR Points
def get_ar_points():

    ar_login_data['mBox_Login$mTextBox_UserName']=ar_username
    ar_login_data['mBox_Login$mTextBox_Password']=ar_password

    r1 = requests.post(ar_login_url,data=ar_login_data,allow_redirects=False)
    r2 = requests.post(ar_lp_url,cookies=r1.cookies)
    parser = ArHTMLParser()
    parser.feed(r2.text)
    return parser.data

def lambda_handler(event, context):
    
    x = get_assignments()
    
    SENDER = os.environ['SENDER']
    AWS_REGION = "us-east-1"
    CHARSET = "UTF-8"
    SUBJECT = "LVDS - Plus Portals Daily Reminder"
    
    BODY_TEXT = """
LVDS Daily Summary
------------------
    
AR Points: {}

Homework Summary:
=================
{}

Homework Long Description:
==========================
{}
    """.format(get_ar_points(),get_assignments_summary(x),get_assignments_longform(x))
    
    BODY_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<title>LVDS Daily Summary</title>

<style type="text/css">
    h4 {{ padding-bottom: 0px; margin-bottom: 0px; border-bottom: 3px solid #A9A9A9; }}
    pre {{ padding-top: 5px; margin-top: 0px; }}
</style>

</head>
<body>
<h3>LVDS Daily Summary</h3>

<h4>AR Points:</h4>
<pre>{}</pre>

<h4>Homework (Summary):</h4>
<pre>{}</pre>

<h4>Homework (Long Description):</h4>
<pre>{}</pre>

</body>
</html>
""".format(get_ar_points(),get_assignments_summary(x),get_assignments_longform(x))
    
    client = boto3.client('ses',region_name=AWS_REGION)
    
    try:
        response = client.send_email(
        Destination={
            'ToAddresses': recipients,
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': CHARSET,
                    'Data': BODY_HTML,
                },
                'Text': {
                    'Charset': CHARSET,
                    'Data': (BODY_TEXT),
                },
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': SUBJECT,
            },
        },
        Source=SENDER,
    )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
