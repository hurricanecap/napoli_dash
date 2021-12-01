import requests
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import streamlit as st 
import math
from scipy import spatial
import time

nap = '14LNByEqFx2LH7y63C9LbdSCYDY13h1WdWT3PtkBjzHP2ZcjvsD'
nap2 = '13nphzGpMa1TtkBaRCUpw6QpdBbtaEExXSKW35AQqJvZko1qFKb'
time_24_hrs_ago = (dt.datetime.now() - dt.timedelta(hours=24)).isoformat()
time_30_d_ago = (dt.datetime.now() - dt.timedelta(days=30)).isoformat()
user_agent = 'napoli.py/0.0.1'

def sending_request(url, head):
    #time.sleep(10)
    new_headers = {'user-agent':head}
    r = requests.get(url=url, headers=new_headers)
    l = []
    try:
        data = r.json()
    except Exception as e:
        print(url, e)
        return l
    l = data['data']
    while 'cursor' in data.keys():
        r = requests.get(url=url + '?cursor='+ data['cursor'], headers=headers)
        data = r.json()
        l += data['data']
    return l
def get_all_earnings_data(address, timestamp_added, user_agent):
    url = 'https://api.helium.io/v1/hotspots/'+ address+'/rewards/sum?min_time='+timestamp_added+'&bucket=day'
    data = sending_request(url, user_agent)
    return pd.DataFrame(data)
def get_day_earnings(earnings):
    return earnings['total'][0]
def get_month_earnings(earnings):
    if len(earnings) >= 30:
        return earnings['total'][0:31].sum()
    else:
        return earnings['total'].sum()
def get_total_earnings(earnings):
    return earnings['total'].sum()

def stats(city_name, user_agent):
    if city_name == 'ALL':
        cit = new_hotspots
    else:
        cit = new_hotspots[new_hotspots['clntcity'] == city_name]
    witness = []
    for idx, row in cit.iterrows():
        d = {}
        d['name'] = row['name'].replace("-", " ")
        d['location'] = row['clntaddr1']
        d['city'] = row['clntcity']
        d['status'] = row['status']['online']
        d['reward scale'] = row['reward_scale']
        user_agent += '1'
        earnings = get_all_earnings_data(row['address'], row['timestamp_added'], user_agent)
        d['total mined'] = get_total_earnings(earnings)
        d['day earnings'] = get_day_earnings(earnings)
        d['month earnings'] = get_month_earnings(earnings)
        
        d['link'] = 'https://explorer.helium.com/hotspots/'+row['address']
        witness.append(d)
        #time.sleep(10)
        
    df = pd.DataFrame(witness).sort_values(by= 'total mined', ascending = False)
    cols = ['name','location','city', 'status','day earnings', 'month earnings','total mined','reward scale','link']
    return df[cols]
def add_total_avg(df):   
    d_total = dict(df.sum(axis =0, numeric_only = True))
    d_total['name'] = 'TOTAL'
    d_total['location'] = " "
    d_total['status'] = " "
    d_total['city'] = " "
    d_total['link'] = ''
    d_total['reward scale'] = 0

    d = dict(df.mean(axis =0, numeric_only = True))
    d['name'] = 'AVERAGE'
    d['location'] = " "
    d['status'] = "  "
    d['city'] = " "

    df = df.append(d, ignore_index = True)  
    df = df.append(d_total, ignore_index = True)
    return df.loc[:, (df != 0).any(axis=0)]
def make_clickable(url, text):
    return f'<a target="_blank" href="{url}">{text}</a>'
def color_status(val):
    if type(val) == float:
        if val < 300:
            color = 'tomato'
        elif val < 500 and val > 300:
            color = 'yellow'
        else: 
            color = 'white'
        return f'background-color:{color}'
    else:  
        if val == 'online':
            color = 'lightgreen'
        elif val == 'offline':
            color = 'tomato'
        elif val == ' ':
            color = 'lightsteelblue'
        elif val == '  ':
            color = 'white'
        else:
            color = 'white'
        return f'background-color:{color}'
    
url = 'https://api.helium.io/v1/accounts/' + nap +'/hotspots'
url2 = 'https://api.helium.io/v1/accounts/' + nap2 +'/hotspots'
data = sending_request(url, user_agent) + sending_request(url2, user_agent)
new_hotspots = pd.DataFrame(data)

options = []
new_hotspots['clntcity'] = [d.get('short_city') for d in new_hotspots['geocode']]
new_hotspots['clntaddr1'] = [d.get('short_street') for d in new_hotspots['geocode']]
new_hotspots['cityid'] = [d.get('city_id') for d in new_hotspots['geocode']]

options = ['ALL'] + list(set(new_hotspots['clntcity']))



#if check_password():
st.sidebar.write("## Helium Hotspots")
# total_earnings = sending_request('https://api.helium.io/v1/accounts/'+ nap +'/rewards/sum?min_time=2021-01-01T00:00:00', user_agent)['sum']
# helium_price = sending_request('https://api.helium.io/v1/oracle/prices/current', user_agent)['price']/100000000

# earned = pd.DataFrame([{'HNT': str(round(total_earnings/100000000,2)), '$': str(round(total_earnings/100000000*helium_price,2))}, {'HNT': str(round((total_earnings/100000000)/len(new_hotspots),2)), '$': str(round(((total_earnings/100000000)/len(new_hotspots))*helium_price,2))}])
# earned.index = ['total earnings', 'average earnings']
# earned
page = st.sidebar.selectbox("App Navigation", ["Hotspot Data"])

if page == 'Hotspot Data':
    city_name = st.sidebar.selectbox('Choose a city' ,options)
    filt = st.sidebar.selectbox('Filter Online/Offline', ['All', 'Online','Offline'])
    hot_data = stats(city_name, user_agent)
    
    
    #hot_data['name'] = hot_data.apply(lambda x: make_clickable(x['link'],x['name']), axis = 1)
    hot_data = add_total_avg(hot_data)
    hot_data.pop('link')
    hot_data.rename(columns={'name': ' '}, inplace=True)

    hot_data = hot_data.set_index(' ')


    if filt == 'Online':
        hot_data = hot_data[hot_data['status']== 'online']
    elif filt == 'Offline':
        hot_data = hot_data[hot_data['status']== 'offline']
    hot_data = hot_data.round(2)
    hot_data = hot_data.astype('str')

    hot_data = hot_data.style.apply(lambda x: ['background: lightsteelblue' if x.name == 'TOTAL' else '' for i in x], axis=1)
    st.table(hot_data.applymap(color_status, subset=['status']).set_precision(2))
    #st.write(hot_data.to_html(escape = False), unsafe_allow_html = True)

if page == 'Earnings Data':
    cities = compiled().set_index('city')
    st.table(cities.style.apply(lambda x: ['background: lightsteelblue' if x.name == 'TOTAL' else '' for i in x], axis=1).set_precision(2))




