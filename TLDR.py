import requests, json, os, boto3

from datetime import datetime, date
from html.parser import HTMLParser
from botocore.exceptions import ClientError

from local_config import *
from email_templates import BODY_TEXT, BODY_HTML

PP_USERNAME = os.environ['PP_USERNAME']
PP_PASSWORD = os.environ['PP_PASSWORD']
AR_USERNAME = os.environ['AR_USERNAME']
AR_PASSWORD = os.environ['AR_PASSWORD']
RECIPIENTS = os.environ['RECIPIENTS'].split(";")

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
    PP_LOGIN_DATA = {'UserName':PP_USERNAME,'Password':PP_PASSWORD}
    r = requests.post(PP_LOGIN_URL, data=PP_LOGIN_DATA, allow_redirects=False)
    r2 = requests.get(PP_ASSIGNMENTS_URL,cookies=r.cookies)
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

    AR_LOGIN_DATA['mBox_Login$mTextBox_UserName']=AR_USERNAME
    AR_LOGIN_DATA['mBox_Login$mTextBox_Password']=AR_PASSWORD

    r1 = requests.post(AR_LOGIN_URL,data=AR_LOGIN_DATA,allow_redirects=False)
    r2 = requests.post(AR_LP_URL,cookies=r1.cookies)
    parser = ArHTMLParser()
    parser.feed(r2.text)
    return parser.data

def lambda_handler(event, context):
    
    x = get_assignments()
    
    SENDER = os.environ['SENDER']   
    BODY_TEXT.format(get_ar_points(),get_assignments_summary(x),get_assignments_longform(x))
    BODY_HTML.format(get_ar_points(),get_assignments_summary(x),get_assignments_longform(x))
    
    client = boto3.client('ses',region_name=SES_REGION)
    
    try:
        response = client.send_email(
        Destination={
            'ToAddresses': RECIPIENTS,
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': SES_CHARSET,
                    'Data': BODY_HTML,
                },
                'Text': {
                    'Charset': SES_CHARSET,
                    'Data': (BODY_TEXT),
                },
            },
            'Subject': {
                'Charset': SES_CHARSET,
                'Data': SES_SUBJECT,
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
