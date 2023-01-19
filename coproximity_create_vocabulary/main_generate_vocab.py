'''
Creates the main vocabularies from scratch: download the dumps, extract only the main articles, sort them by pageviews, get the redirections 
and create the main vocabularies from them.

example:  python main_generate_vocab.py --project it --language_name italian --spacy_model it_core_news_lg --disable_tag parser_ner --fasttext_model fr
'''

import argparse

from coproximity_create_vocabulary.data_conf import base_vocab_folder
from coproximity_create_vocabulary.download_wikipedia.get_pages_views.main_downloader_wiki import main_downloader_wiki

from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.main_get_default_by_project import main_default_wikititle

def main_generate_vocab(project, language_folder, fasttext_model, save_parent_folder=base_vocab_folder, spacy_model = None, disable_tag = None) :
    '''
    Creates the main vocabularies from scratch.

    project: Wikipedia project from which to extract the data from
    language_folder: name of the language folder, where all the data specific to this language will be stored
    fasttext_model: spacy model used to lemmatize the titles during the vocabulary creation
    save_parent_folder: vocabulary base folder, folder in which all the vocabulary will be saved 
    spacy_model: tags to disable in the spacy model (to speed it up) during the vocabulary creation. If None, try to get a default value from 
        coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.get_args.var_getter_by_project using project as a key
    disable_tag: fasttext model to use to create word2vec vectors from articles during the vocabulary creation. If None, try to get a default value from 
        coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.get_args.var_getter_by_project using project as a key
    '''
    #main_downloader_wiki(project, language_folder)
    main_default_wikititle(spacy_model, disable_tag, fasttext_model, project, print_progress_info=False, whole_folder = save_parent_folder + language_folder + '/')

vocab_parser = argparse.ArgumentParser(description='Creates the main vocabularies from scratch: download the dumps, extract only the main articles, sort them by pageviews, get the redirections and create the main vocabularies from them.')
vocab_parser.add_argument('--project', '-p', default=None,  help = 'Wikipedia project from which to extract the data from')
vocab_parser.add_argument('--language_name', '-l', default=None,  help = 'name of the language folder, where all the data specific to this language will be stored')
vocab_parser.add_argument(
    '--spacy_model', default=None,
    help = 'spacy model used to lemmatize the titles during the vocabulary creation.If None, try to get a default value from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.get_args.var_getter_by_project using project as a key'
)
vocab_parser.add_argument(
    '--disable_tag', default=None,
    help = 'tags to disable in the spacy model (to speed it up) during the vocabulary creation.If None, try to get a default value from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.get_args.var_getter_by_project using project as a key'

)
vocab_parser.add_argument('--fasttext_model', default=None,  help = 'fasttext model to use to create word2vec vectors from articles during the vocabulary creation')


if __name__ == '__main__' :
    args, unknown = vocab_parser.parse_known_args()

    #if we give the script no argument, it will do french and english with the default value.
    #if some arguments are given, but not enough to make the vocabularies, an exception will be raised
    nb_args = len([arg_val for arg_val in args.__dict__.values() if not arg_val is None])
    has_main_args = bool(args.project and args.language_name)

    if nb_args > 0 and not has_main_args :
        raise Exception('Has arguments main_generate_vocab but missing the main args (project name and vocab name')

    if has_main_args :
        spacy_model = args.spacy_model if args.spacy_model else None
        disable_tag = args.disable_tag.split('_') if args.disable_tag else None
        main_generate_vocab(args.project, args.language_name, fasttext_model=args.fasttext_model, save_parent_folder=base_vocab_folder, spacy_model=spacy_model, disable_tag=disable_tag)
    else :
        #default project values
        for project, language_folder, spacy_model, disable_tag, fasttext_model in [
            #is none because we have an argument getter  in var_getter_by_project
            #('fr', 'french', None, None, 'en'),
            ('en', 'english', None, None, 'fr'),
        ] :
            main_generate_vocab(project, language_folder, fasttext_model=fasttext_model, save_parent_folder=base_vocab_folder, spacy_model=spacy_model, disable_tag=disable_tag)
