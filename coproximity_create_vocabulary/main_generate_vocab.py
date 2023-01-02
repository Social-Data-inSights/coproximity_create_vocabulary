'''
TODOC

example:  python main_generate_vocab.py --project it --vocab_name italian --spacy_model it_core_news_lg --disable_tag parser_ner
'''

import argparse

from coproximity_create_vocabulary.data_conf import base_vocab_folder
from coproximity_create_vocabulary.download_wikipedia.get_pages_views.main_downloader_wiki import main_downloader_wiki

from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.main_get_default_by_project import main_default_wikititle

def main_generate_vocab(project, vocab_folder_name, save_parent_folder=base_vocab_folder, spacy_model = None, disable_tag = None) :
    print('__________', main_downloader_wiki)
    main_downloader_wiki(project, vocab_folder_name)
    print('__________', main_downloader_wiki)
    main_default_wikititle(spacy_model, disable_tag, project, print_progress_info=False, whole_folder = save_parent_folder + vocab_folder_name + '/')


if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', '-p', default=None,  help = 'project')
    parser.add_argument('--vocab_name', '-v', default=None,  help = 'vocab_name')
    parser.add_argument('--spacy_model', default=None,  help = 'spacy_model')
    parser.add_argument('--disable_tag', default=None,  help = 'disable_tag')
    args, unknown = parser.parse_known_args()

    nb_args = len([arg_val for arg_val in args.__dict__.values() if not arg_val is None])
    has_main_args = bool(args.project and args.vocab_name)

    if nb_args > 0 and not has_main_args :
        raise Exception('Has arguments main_generate_vocab but missing the main args (project name and vocab name')

    if has_main_args :
        spacy_model = args.spacy_model if args.spacy_model else None
        disable_tag = args.disable_tag.split('_') if args.disable_tag else None
        main_generate_vocab(args.project, args.vocab_name, save_parent_folder=base_vocab_folder, spacy_model=spacy_model, disable_tag=args.disable_tag)
    else :
        #default project values
        for project, vocab_folder_name, spacy_model, disable_tag in [
            #is none because we have an argument getter  in var_getter_by_project
            #('fr', 'french', None, None),
            ('en', 'english', None, None),
        ] :
            main_generate_vocab(project, vocab_folder_name, save_parent_folder=base_vocab_folder, spacy_model=spacy_model, disable_tag=disable_tag)
