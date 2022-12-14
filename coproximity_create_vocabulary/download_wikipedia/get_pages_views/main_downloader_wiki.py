
from coproximity_create_vocabulary.data_conf import base_vocab_folder
from coproximity_create_vocabulary.download_wikipedia.get_pages_views.download_synonyms import main_download_synonyms
from coproximity_create_vocabulary.download_wikipedia.get_pages_views.download_wiki_title import main_download_wiki_title

from coproximity_create_vocabulary.download_wikipedia.get_pages_views.util import download_page


def main_downloader_wiki(project, vocab_folder_name, save_parent_folder=base_vocab_folder) :
    #main_download_synonyms(project, vocab_folder_name, save_parent_folder=save_parent_folder)
    main_download_wiki_title(
        project, vocab_folder_name, save_parent_folder=save_parent_folder, set_allowed_projects = {b'fr' , b'en', b'it', b'de'},
        use_multiprocessing=True,
    )
    download_page(
        save_parent_folder + vocab_folder_name + f'/dumps/dump/wiki_{project}_dump.xml.bz2',
        f'https://dumps.wikimedia.org/{project}wiki/latest/{project}wiki-latest-pages-articles-multistream.xml.bz2'
    )

if __name__ == '__main__' :
    for project, vocab_folder_name in [
        ('fr', 'french'),
        ('en', 'english'),
    ] :
        main_downloader_wiki(project, vocab_folder_name, save_parent_folder=base_vocab_folder)