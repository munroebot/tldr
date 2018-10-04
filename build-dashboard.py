import requests, json, os, boto3

from datetime import datetime, date
from html.parser import HTMLParser
from botocore.exceptions import ClientError

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
    assignments_summary = []
    for x in data:
        assignments_summary.append("{} - {}".format(x["DueDate"],x["Title"]))

    return assignments_summary

# Get a long format (for the bottom of email)
def get_assignments_longform(data=None):
    assignments_longform = []
    for x in data:
        assignments_longform.append("{}\n{}\n{}\n\n".format(x["DueDate"], x["Title"], x["Description"]))

    return assignments_longform

# Grab AR Points
def get_ar_points():
    r1 = requests.post(ar_login_url,data=ar_login_data,allow_redirects=False)
    r2 = requests.post(ar_lp_url,cookies=r1.cookies)
    parser = ArHTMLParser()
    parser.feed(r2.text)
    return parser.data

def say_hello():
    return pp_username

def lambda_handler(event, context):
    
    # x = get_assignments()
    # get_assignments_summary(x)
    # get_assignments_longform(x)
    # print("\nAR Points: {}\n\n".format(get_ar_points()))
    
    SENDER = os.environ['SENDER']
    AWS_REGION = "us-east-1"
    CHARSET = "UTF-8"
    SUBJECT = "LVDS - Plus Portals Daily Reminder"
    
    BODY_TEXT = ("Hi")
    BODY_HTML = """
    <HTML><H1>hello</H1></HTML>

    """
    
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
                    'Data': BODY_TEXT,
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