'''
Download the redirects of Wikipedia articles and the id to title dictionary.

redirects: https://dumps.wikimedia.org/{project}wiki/latest/{project}wiki-latest-redirect.sql.gz    

pages : https://dumps.wikimedia.org/{project}wiki/latest/{project}wiki-latest-page.sql.gz
'''

import os, gzip, json, csv
from coproximity_create_vocabulary.extract_vocabulary.basic_method.util_vocab import download_page

from coproximity_create_vocabulary.data_conf import base_vocab_folder

def get_id2title(project, page_file, id2title_file) :
    '''
    Save the SQL dump of the pages of the project {project} and extract from it a dictionary from the main pages' id to their titles 
    (Only get the id of Wikipedia pages which namespace are "Main" )
    For more details on namespace: https://en.wikipedia.org/wiki/Wikipedia:Namespace

    project: project from which to download the page dump and extract the id -> title dictionary
    id2title_file: save file of the dictionary {wikipedia id: wikipedia title}
    page_file: save file of the SQL dump
    '''
    download_page(page_file, url = f'https://dumps.wikimedia.org/{project}wiki/latest/{project}wiki-latest-page.sql.gz',)
    
    #{project}wiki-latest-page.sql.gz is a SQL table, but it is faster to directly parse it by reading which values were supposed to be inserted.
    id2title = {}
    with gzip.open(page_file)as f  :
        for line in f :
            if line.startswith(b'INSERT INTO `page` VALUES') :
                split_insert = [x.strip('(') for x in line.decode('utf8').strip(');\n)').split('VALUES ')[1].split('),(')]

                for vals in csv.reader(split_insert, delimiter=',', quotechar="'", escapechar ='\\') :
                    #Only get the id of Wikipedia pages which namespace are "Main" 
                    if int(vals[1]) == 0 :
                        id2title[vals[0]] = vals[2]
                        
    with open(id2title_file, 'w', encoding='utf8') as f :
        json.dump(id2title, f)
        
    return id2title


def get_synonyms(project, id2title, redirect_file, synonym_file) :
    '''
    Download the redirect from WIkipedia's project {project} and use it to create a csv file (whose path is {synonym_file}) which contains tuples synonym, main page.
        (the separator of the csv is ";")
    Use {id2title} which is the result of the get_id2title (dictionary {page id: page title}) to get only the synonyms of the main pages.

    project: project from which to download the redirect dump and extract the synonym -> main page dictionary
    id2title: dict {page id -> ...} or set of id, an synonym must have its main page id in this to be added to the result
        it is strongly recommended to use the result of get_id2title for this part.
    redirect_file: save file of the SQL dump
    synonym_file: csv file in which to save the resulting synonyms
    '''
    download_page(redirect_file, url = f'https://dumps.wikimedia.org/{project}wiki/latest/{project}wiki-latest-redirect.sql.gz',)

    #{project}wiki-latest-redirect.sql.gz is a SQL table, but it is faster to directly parse it by reading which values were supposed to be inserted.
    redirect = {}
    with gzip.open(redirect_file)as f  :
        for line in f :
            if line.startswith(b'INSERT INTO `redirect` VALUES') :
                split_insert = [x.strip('(') for x in line.decode('utf8').strip(');\n)').split('VALUES ')[1].split('),(')]

                for vals in csv.reader(split_insert, delimiter=',', quotechar="'", escapechar ='\\') :
                    if vals[0] in id2title :
                        redirect[id2title[vals[0]]] = vals[2]
    
    with open(synonym_file, 'w', encoding='utf8' , newline='') as f :
        writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for from_word, to_word in redirect.items() :
            writer.writerow((from_word, to_word))

def main_download_synonyms(project, language_folder, save_parent_folder=base_vocab_folder) :
    '''
    For a project {project} download the redirects of Wikipedia articles and the id to title dictionary.
    
    language_folder: name of the language to extract, will be used as the name of the language folder. 
    save_parent_folder: parent folder in which all the vocabulary files/folder will be saved/created (vocabulary base folder)
    '''
    vocab_folder = save_parent_folder + language_folder + '/'
    dump_folder = vocab_folder + 'dumps/'
    page_file = dump_folder + f'{project}wiki-latest-page.sql.gz'
    redirect_file = dump_folder + f'{project}wiki-latest-redirect.sql.gz'

    extent_list = dump_folder.split('/')
    folder_to_create = ''
    for new_folder in extent_list :
        folder_to_create += new_folder + '/'
        if not os.path.exists(folder_to_create) :
            os.mkdir(folder_to_create)

    meta_folder = vocab_folder + 'meta/'
    if not os.path.exists(meta_folder) :
        os.mkdir(meta_folder)
    id2title_file = meta_folder + 'id2title.json'
    synonym_file = meta_folder + 'synonyms.csv'

    id2title = get_id2title(project, page_file, id2title_file)
    get_synonyms(project, id2title, redirect_file, synonym_file)

if __name__ == '__main__' :
    main_download_synonyms()