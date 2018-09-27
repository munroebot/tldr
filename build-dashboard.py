import requests, json, os
from datetime import datetime, date
from local_config import *

"""
pp_username = os.environ['PP_USERNAME']
pp_password = os.environ['PP_PASSWORD']
ar_username = os.environ['AR_USERNAME']
ar_username = os.environ['AR_PASSWORD']
"""

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

def get_assignments_summary(data=None):
    assignments_summary = []
    for x in data:
        assignments_summary.append("{} - {}".format(x["DueDate"],x["Title"]))
    
    return assignments_summary

def get_assignments_longform(data=None):
    assignments_longform = []
    for x in data:
        assignments_longform.append("{}\n{}\n{}\n\n".format(x["DueDate"], x["Title"], x["Description"]))

    return assignments_longform

# Grab AR Points
def get_ar_points():
    r1 = requests.post(ar_login_url,data=ar_login_data,allow_redirects=False)
    r2 = requests.post(ar_lp_url,cookies=r1.cookies)
    print(r2.text)

x = get_assignments()
for j in get_assignments_summary(x):
    print(j)

for k in get_assignments_longform(x):
    print(k)