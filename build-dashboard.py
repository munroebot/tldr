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
    r2 = requests.get(pp_homework_url,cookies=r.cookies)
    x = json.loads(r2.text)

    d0 = date.today()

    # print assignments, today and newer
    for j in x['Data']:
        d1 = datetime.strptime(j['DueDate'], '%m-%d-%Y').date()
        if d1 >= d0:
            print("{} - {}".format(j["DueDate"], j["Title"]))

# Grab AR Points
def get_ar_points():

    r1 = requests.post(ar_login_url,data=ar_login_data,allow_redirects=False)
    r2 = requests.post(ar_lp_url,cookies=r1.cookies)
    print(r2.text)

get_assignments()
# get_ar_points()
