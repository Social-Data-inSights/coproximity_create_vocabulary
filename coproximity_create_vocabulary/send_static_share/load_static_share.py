'''
Load the main zip for compascience's static share
'''

from coproximity_create_vocabulary.extract_vocabulary.basic_method.util_vocab import download_page
from coproximity_create_vocabulary.data_conf import base_vocab_folder

import os, shutil, requests, textwrap

verify = os.path.dirname(os.path.realpath(__file__)) + '/compascience.crt'
def download_page_from_static_share(page_file, url, verify=verify ) :
    '''
    alternative downloader because requests send ssh errors
    Download an internet page at {url} and save it in file {page_file}

    WARNING : need a valid .crt, if the current one is missing or not available, download all the .crt of https://www.compasciences.ch/ and
    merge them into 1 .crt
    TODOC autre part 
    '''
    dump = requests.get(url, stream=True, verify = verify)
    with open(page_file, 'wb') as f :
        for chunk in dump.raw.stream(1024 * 1024 * 100, decode_content=False):
            if chunk:
                f.write(chunk)

def download_and_unzip (load_url, save_zip_file, extracted_path):
    '''
    Download a zip file from url {load_url} and unzip at path {extracted_path}

    save_zip_file: where to save the file before extracting
    '''
    download_page_from_static_share(save_zip_file, load_url)
    shutil.unpack_archive(save_zip_file, extract_dir=extracted_path)
    os.remove(save_zip_file)

url_static_share = 'https://www.compasciences.ch/voc/'
def download_main_vocab (language_folder, project_server, name_vocab_folder = 'main_vocab' , date = 'latest') :
    '''
    Download the main vocabulary for a Wikipedia project {project_server} and save it into the language folder {language_folder} 
    The main vocabulary is considered the one made with a lexicon of size 1e5, with uppercase and accents

    name_vocab_folder: name of the vocabulary to save
    date: version of the main vocab to get
    '''
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
    '''
    Download what's needed to create vocabularies for a Wikipedia project {project_server} and save it into the language folder {language_folder}
    Load the list of articles sorted by views and the synonyms, those 2 files but with their processed (with the default methods) titles.
        Also contains the dictionary {wiki id: id title}
    
    date: version of the main vocab to get
    '''
    load_url = f'{url_static_share}{project_server}/meta-{date}.zip'
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

def download_wiki_plain(project, nb_keep, data_folder, date = 'latest'):
    plain_base = f"best_avg_{'.'.join(textwrap.wrap(str(nb_keep)[::-1] , 3))[::-1]}"

    load_url = f'https://www.compasciences.ch/datasets/wikipedia/{project}/{plain_base}-{date}.zip'
    wiki_folder = f'{data_folder}/wikipedia_{project}/'
    loaded_file = wiki_folder + plain_base + '.zip'
    extracted_path = wiki_folder 
    
    for folder in [
        base_vocab_folder,
        wiki_folder,
    ]:
        if not os.path.exists(folder) :
            os.mkdir(folder) 
    download_and_unzip (load_url, loaded_file, extracted_path)

if __name__ == '__main__' :
    language_folder = 'french'
    project_server = 'fr'
    
    download_main_vocab (language_folder, project_server, name_vocab_folder = 'test_main_vocab')
    download_needed_to_create_vocab (language_folder, project_server)

    from ade_imi.data_conf import base_data_folder
    download_wiki_plain(project_server, 100, base_data_folder, date = 'latest')

