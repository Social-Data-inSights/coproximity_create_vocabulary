'''
Scripts about the date of the latest version of Wikipedia
'''

import requests, os
from bs4 import BeautifulSoup


def get_most_recent_date(project) :
    '''
    Get the date of the most recent dumps update for the wikipedia project {project}
    '''
    list_dates = requests.get(f'https://dumps.wikimedia.org/{project}wiki/')
    soup = BeautifulSoup(list_dates.text, features="html.parser")
    return max([a.get('href').strip('/') for a in soup.find_all('a') if a.get('href') and a['href'].strip('/').isnumeric()])


def delete_old_date(wiki_date, dump_folder):
    '''
    Considers any element of a folder {dump_folder} to be '****-{date}.*' , with date being in the format of the Wikipedia date. Delete all
    files whose date is not {wiki_date}
    '''
    for filename in os.listdir(dump_folder) :
        filepath = f'{dump_folder}/{filename}'
        fildate = filename.split('-')[-1].split('.')[0]
        if fildate.isnumeric() and fildate != wiki_date :
            print('delete', filepath, wiki_date)
            os.remove(filepath)