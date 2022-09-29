# Импорт библиотеки requests
import requests
import pandas as pd
from pprint import pprint
import gspread
from datetime import datetime, date, time, timedelta
import time

date_start = '2022-08-01'  # начальная дата
date_end = '2022-08-05' # конечная дата 

login_details = {
    '***': ***, 
    '***': *** 
    }

all_cabinets = {
    '***': {                                 
        '***': ***, 
        '***': ***                   
        },
    
    '***': {                            
        '***': ***,            
        '***': ***        
        }
}

def login(log, password):
    response_login = requests.get(f'https://lk-gnezdo.com/cgi-bin/admin/auth.cgi?json=1&login={log}&password={password}')
    ID = response_login.json()['sid']
    return ID


def get_stat_auth(sid, batch_id, date_start):                #пример даты '2022-08-01'
    param_request = {'json': 1, 'sid': sid, 'date_start': date_start, 'batch_id': batch_id} 
    response_stat = requests.get('http://news.gnezdo.ru/cgi-bin/admin/stat.cgi', params=param_request)
    return response_stat


id_reduxin = login(list(login_details)[0], login_details['reduxin-main'])
id_sm = login(list(login_details)[1], login_details['smartmedia'])


data_date = {}


date_start_datetime = datetime.strptime(date_start, '%Y-%m-%d')
date_end_datetime = datetime.strptime(date_end, '%Y-%m-%d')

delta = date_end_datetime - date_start_datetime     # timedelta
if delta.days<=0:
    print ("Ругаемся и выходим")
for i in range(delta.days + 1):
    key_date = date_start_datetime + timedelta(i)
    data_date[key_date.strftime('%Y-%m-%d')] = ''


dataset = {}
data = {}

for item in list(all_cabinets.items()):
    if item[0] == 'Сервье':
        for i in item[1].items():
            for date in data_date.keys():
                stat = get_stat_auth(id_sm, i[1], date).json()
                data[(date, i[0])] = stat

    else:
        for i in item[1].items():
            for date in data_date.keys():
                stat = get_stat_auth(id_reduxin, i[1], date).json()
                data[(date, i[0])] = stat


df = pd.DataFrame(data)
trans_data = df.transpose().reset_index()
trans_data.rename(columns = {'level_0': 'date', 'level_1':'object'}, inplace = True)


gc = gspread.service_account(filename='/Users/aleksmaaan/Documents/python/media_data/gnezdo/credentials.json')
sh = gc.open('Gnezdo')
worksheet = sh.get_worksheet(0)
worksheet.update([trans_data.columns.values.tolist()] + trans_data.values.tolist())