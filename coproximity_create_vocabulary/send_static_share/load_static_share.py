'''
TODOC
'''

from coproximity_create_vocabulary.extract_vocabulary.basic_method.util_vocab import download_page
from coproximity_create_vocabulary.data_conf import base_vocab_folder

import os, shutil
from urllib.request import urlretrieve

def download_page_from_static_share(page_file, url ) :
    '''
    Download an internet page at {url} and save it in file {page_file}
    '''
    urlretrieve(url, filename=page_file)

def download_and_unzip (load_url, save_zip_file, save_folder):
    download_page_from_static_share(save_zip_file, load_url)
    shutil.unpack_archive(save_zip_file, extract_dir=save_folder)
    os.remove(save_zip_file)

url_static_share = 'https://www.compasciences.ch/voc/'
def download_main_vocab (language_folder, project_server, name_vocab_folder = 'main_vocab' , date = 'latest') :
    load_url = f'{url_static_share}{project_server}/main_vocab-{date}.zip'

    save_folder = base_vocab_folder + language_folder + f'/ngram_title_wiki/{name_vocab_folder}'
    save_zip_file = f'{save_folder}.zip'

    for folder in [
        base_vocab_folder,
        base_vocab_folder + language_folder,
        base_vocab_folder + language_folder + '/ngram_title_wiki/',
        save_folder,
    ]:
        if not os.path.exists(folder) :
            os.mkdir(folder)

    download_and_unzip (load_url, save_zip_file, save_folder)


def download_needed_to_create_vocab (language_folder, project_server, date = 'latest') :
    load_url = f'{url_static_share}{project_server}/main_vocab-{date}.zip'
    save_folder = base_vocab_folder + language_folder + '/meta'
    save_zip_file = f'{save_folder}.zip'

    for folder in [
        base_vocab_folder,
        base_vocab_folder + language_folder,
        save_folder,
    ]:
        if not os.path.exists(folder) :
            os.mkdir(folder) 
            
    download_and_unzip (load_url, save_zip_file, save_folder)

if __name__ == '__main__' :
    language_folder = 'french'
    project_server = 'fr'
    
    download_main_vocab (language_folder, project_server, name_vocab_folder = 'test_main_vocab')
    download_needed_to_create_vocab (language_folder, project_server)