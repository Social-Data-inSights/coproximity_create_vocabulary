'''
TODOC
'''

from coproximity_create_vocabulary.data_conf import base_vocab_folder
from coproximity_create_vocabulary.download_wikipedia.get_pages_views.main_downloader_wiki import main_downloader_wiki

from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.main_get_default_by_project import main_default_wikititle

def main_generate_vocab(project, vocab_folder_name, save_parent_folder=base_vocab_folder, spacy_model = None, disable_tag = None) :
    main_downloader_wiki(project, vocab_folder_name)
    main_default_wikititle(spacy_model, disable_tag, project, print_progress_info=False, whole_folder = save_parent_folder + vocab_folder_name + '/')


if __name__ == '__main__' :
    for project, vocab_folder_name, spacy_model, disable_tag in [
        #is none because we have an argument getter  in var_getter_by_project
        ('fr', 'french', None, None),
        ('en', 'english', None, None),
    ] :
        main_generate_vocab(project, vocab_folder_name, save_parent_folder=base_vocab_folder, spacy_model=spacy_model, disable_tag=disable_tag)
