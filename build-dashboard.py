import requests, json
from datetime import datetime, date

# Get Plus Portals Assignments
def get_assignments():

    plus_portals_url="https://www.plusportals.com/LVDS"
    homework_url='https://www.plusportals.com/ParentStudentDetails/ShowSectionHomeWorkInfo?&isGroup=false'
    data = {'UserName':'luke.munroe','Password':'MomIsNice2'}

    r = requests.post(plus_portals_url, data=data, allow_redirects=False)
    r2 = requests.get(homework_url,cookies=r.cookies)
    x = json.loads(r2.text)

    d0 = date.today()

    # print assignments, today and newer
    for j in x['Data']:
        d1 = datetime.strptime(j['DueDate'], '%m-%d-%Y').date()
        if d1 >= d0:
            print("{} - {}".format(j["DueDate"], j["Title"]))

# Grab AR Points
def get_ar_points():
    ar_login_url = 'https://hosted101.renlearn.com/260290/HomeConnect/Login.aspx'
    ar_lp_url='https://hosted101.renlearn.com/260290/HC/Reading/ARReadingPractice.aspx'

    data = {'mBox_Login$mTextBox_UserName':'luke.munroe','mBox_Login$mTextBox_Password':'LM'}
    data['__VIEWSTATE']='/wEPDwUKLTkyMDU5NzIwNA9kFgICAQ9kFgICAQ9kFgICAQ8PFgIeB1Zpc2libGVnZGRkgxa8DgsFgj8Gef7E0nyqMNG4oTsXq+QaDd465kj//nc='
    data['__EVENTVALIDATION']='/wEdAAV911NEnmlz5dto7LmADeF7lU3ax5wVG3nfYXTHNadz5WXM+3WtjHCIr5YiZBbD32AtSTitspZrFBypMFcQCUvzFPOBqWRHCNGau92f78GaLvwt+OQBZ5xsxGmQ8lCRaTWQbqB0gNM5sq0IYKRaqEMn'
    data['mBox_Login$mButton_LogIn']='Log In'
    # data['__EVENTTARGET']=''
    # data['__EVENTARGUMENT']=''

    r1 = requests.post(ar_login_url,data=data,allow_redirects=False)
    r2 = requests.post(ar_lp_url,cookies=r1.cookies)
    print(r2.text)

# get_assignments()
get_ar_points()
