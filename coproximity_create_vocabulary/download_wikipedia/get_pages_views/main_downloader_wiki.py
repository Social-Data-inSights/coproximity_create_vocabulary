'''
main file to download and process the wikipedia dumps from wikipedia for creating a vocabulary.
Create 2 csv:
    - a list of articles title with the number of time it was viewed sorted descendingly
    - a list of redirection from a redirection to the main page it redirects to

It also downloads the article dumps of Wikipedia to be used to get a text to create a vector representing articles using word2vec.
'''
import os

from coproximity_create_vocabulary.data_conf import base_vocab_folder, set_allowed_download_projects
from coproximity_create_vocabulary.download_wikipedia.get_pages_views.download_synonyms import main_download_synonyms
from coproximity_create_vocabulary.download_wikipedia.get_pages_views.download_wiki_title import main_download_wiki_title
from coproximity_create_vocabulary.download_wikipedia.get_pages_views.wikipedia_date_handle import get_most_recent_date, delete_old_date

from coproximity_create_vocabulary.extract_vocabulary.basic_method.util_vocab import download_page


def main_downloader_wiki(project, language_folder, save_parent_folder=base_vocab_folder) :
    '''
    For a project {project} download and process the wikipedia dumps from wikipedia for creating a vocabulary.
    The project should be in {set_allowed_download_projects}.
    
    language_folder: name of the language to extract, will be used as the name of the language folder. 
    save_parent_folder: parent folder in which all the vocabulary files/folder will be saved/created (vocabulary base folder)
    '''
    #date of the latest dumps for this project
    wiki_most_recent_date = get_most_recent_date(project)

    print('start main_downloader_wiki')
    
    #download and process redirections
    main_download_synonyms(project, language_folder, wiki_most_recent_date, save_parent_folder=save_parent_folder)
    
    #download the article dump and an index to find them more easily in the dump
    plain_dump_file = save_parent_folder + language_folder + f'/dumps/wiki_{project}_dump-{wiki_most_recent_date}.xml.bz2'
    index_dump_file = save_parent_folder + language_folder + f'/dumps/wiki_{project}_dump_index-{wiki_most_recent_date}.xml.bz2'
    for filepath, url_save in [
        (plain_dump_file, f'https://dumps.wikimedia.org/{project}wiki/latest/{project}wiki-latest-pages-articles-multistream.xml.bz2'),
        (index_dump_file,f'https://dumps.wikimedia.org/{project}wiki/latest/{project}wiki-latest-pages-articles-multistream-index.txt.bz2'),
    ] :
        if not os.path.exists(filepath) :
            download_page(filepath, url_save)
        else :
            print(f'{filepath} already exists')
    
    #download and process the page views
    main_download_wiki_title(
        project, language_folder, save_parent_folder=save_parent_folder, set_allowed_projects = set_allowed_download_projects,
        use_multiprocessing=True,
    )
    delete_old_date(wiki_most_recent_date, save_parent_folder + language_folder + '/dumps/')

    print('download wiki dumps end')
    
    


if __name__ == '__main__' :
    for project, language_folder in [
        ('fr', 'french'),
        ('en', 'english'),
    ] :
        main_downloader_wiki(project, language_folder, save_parent_folder=base_vocab_folder)