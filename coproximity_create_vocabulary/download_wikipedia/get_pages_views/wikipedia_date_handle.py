'''
TODOC
'''

import requests, os
from bs4 import BeautifulSoup


def get_most_recent_date(project) :
    list_dates = requests.get(f'https://dumps.wikimedia.org/{project}wiki/')
    soup = BeautifulSoup(list_dates.text)
    return max([a.get('href').strip('/') for a in soup.find_all('a') if a.get('href') and a['href'].strip('/').isnumeric()])


def delete_old_date(recent_date, dump_folder):
    for filename in os.listdir(dump_folder) :
        filepath = f'{dump_folder}/{filename}'
        fildate = filename.split('-')[-1].split('.')[0]
        if fildate.isnumeric() and fildate != recent_date :
            print('delete', filepath, recent_date)
            os.remove(filepath)