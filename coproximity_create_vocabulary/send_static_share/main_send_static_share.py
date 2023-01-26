'''
TODOC send default wiki

Creates the main vocabularies from scratch: download the dumps, extract only the main articles, sort them by pageviews, get the redirections 
and create the main vocabularies from them. And then zip the meta folder (in which the synonyms and lexicon are saved, with their precessed version) 
and main vocabulary (vocabulary with a lexicon of size 1e5, with uppercase and accents)
and send them to the static_share server.

use the command line arguments from the coproximity_create_vocabulary.main_generate_vocab parser

example:  python main_send_static_share.py --project it --language_name italian --spacy_model it_core_news_lg --disable_tag parser_ner --fasttext_model fr
'''
from coproximity_create_vocabulary.data_conf import base_vocab_folder

from coproximity_create_vocabulary.main_generate_vocab import vocab_parser, main_generate_vocab
from coproximity_create_vocabulary.send_static_share.zip_vocab import zip_vocab, zip_wiki_plains
from coproximity_create_vocabulary.send_static_share.handle_server import send_vocab_to_server, send_wiki_plain_to_server

from coproximity_create_vocabulary.download_wikipedia.create_wikipedia_plain.extract_main_plains_from_vocabulary import extract_main_plains_from_vocabulary

def main_send_static_share(project, language_name, fasttext_model, save_parent_folder=base_vocab_folder, spacy_model = None, disable_tag = None) :
    '''
    Creates the main vocabularies from scratch, zip the important part and send them to the static_share server.
    TODOC send default wiki

    project: Wikipedia project from which to extract the data from. Will also be the name of the language folder in the server.
    language_name: name of the language folder, where all the data specific to this language will be stored
    fasttext_model: spacy model used to lemmatize the titles during the vocabulary creation
    save_parent_folder: vocabulary base folder, folder in which all the vocabulary will be saved 
    spacy_model: tags to disable in the spacy model (to speed it up) during the vocabulary creation. If None, try to get a default value from 
        coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.get_args.var_getter_by_project using project as a key
    disable_tag: fasttext model to use to create word2vec vectors from articles during the vocabulary creation. If None, try to get a default value from 
        coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.get_args.var_getter_by_project using project as a key
    '''
    main_generate_vocab(project, language_name, fasttext_model=fasttext_model, save_parent_folder=save_parent_folder, spacy_model=spacy_model, disable_tag=disable_tag)
    
    language_folder = save_parent_folder + language_name +'/'
    to_send_folder = f'/home/debian/cs.prod/static_share/voc/{project}/'
    zip_vocab(language_folder)
    send_vocab_to_server(language_folder, to_send_folder)

    #send default wiki
    wiki_plain_folder = f'{base_vocab_folder}extracted_wikipedia/{language_name}/'
    to_send_folder_wiki = f'/home/debian/cs.prod/static_share/datasets/wikipedia/{project}/'
    extract_main_plains_from_vocabulary(language_name, project)
    zip_wiki_plains(wiki_plain_folder)
    send_wiki_plain_to_server(wiki_plain_folder, to_send_folder_wiki)

if __name__ == '__main__' :
    args, unknown = vocab_parser.parse_known_args()
    spacy_model = args.spacy_model if args.spacy_model else None
    disable_tag = args.disable_tag.split('_') if args.disable_tag else None
    main_send_static_share(args.project, args.language_name, fasttext_model=args.fasttext_model, save_parent_folder=base_vocab_folder, spacy_model=spacy_model, disable_tag=disable_tag)
   
