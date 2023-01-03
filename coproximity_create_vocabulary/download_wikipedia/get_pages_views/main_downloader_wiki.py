'''
TODOC
'''

from coproximity_create_vocabulary.data_conf import base_vocab_folder, set_allowed_download_projects
from coproximity_create_vocabulary.download_wikipedia.get_pages_views.download_synonyms import main_download_synonyms
from coproximity_create_vocabulary.download_wikipedia.get_pages_views.download_wiki_title import main_download_wiki_title

from coproximity_create_vocabulary.extract_vocabulary.basic_method.util_vocab import download_page


def main_downloader_wiki(project, vocab_folder_name, save_parent_folder=base_vocab_folder) :

    print('start main_downloader_wiki')
    
    main_download_synonyms(project, vocab_folder_name, save_parent_folder=save_parent_folder)
    
    plain_dump_file = save_parent_folder + vocab_folder_name + f'/dumps/wiki_{project}_dump.xml.bz2'
    index_dump_file = save_parent_folder + vocab_folder_name + f'/dumps/wiki_{project}_dump_index.xml.bz2'
    download_page(
        plain_dump_file,
        f'https://dumps.wikimedia.org/{project}wiki/latest/{project}wiki-latest-pages-articles-multistream.xml.bz2'
    )
    download_page(
        index_dump_file,
        f'https://dumps.wikimedia.org/{project}wiki/latest/{project}wiki-latest-pages-articles-multistream-index.txt.bz2'
    )
    
    main_download_wiki_title(
        project, vocab_folder_name, save_parent_folder=save_parent_folder, set_allowed_projects = set_allowed_download_projects,
        use_multiprocessing=True,
    )
    
    
    


if __name__ == '__main__' :
    for project, vocab_folder_name in [
        ('fr', 'french'),
        ('en', 'english'),
    ] :
        main_downloader_wiki(project, vocab_folder_name, save_parent_folder=base_vocab_folder)