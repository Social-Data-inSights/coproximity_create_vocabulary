'''
TODOC
'''
from coproximity_create_vocabulary.data_conf import base_vocab_folder

from coproximity_create_vocabulary.main_generate_vocab import vocab_parser, main_generate_vocab
from coproximity_create_vocabulary.send_static_share.zip_vocab import zip_vocab
from coproximity_create_vocabulary.send_static_share.handle_server import send_to_server

def main_send_static_share(project, language_name, fasttext_model, save_parent_folder=base_vocab_folder, spacy_model = None, disable_tag = None) :
    '''
    Creates the main vocabularies from scratch. TODOC

    project: Wikipedia project from which to extract the data from
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
    send_to_server(language_folder, to_send_folder)

if __name__ == '__name__' :
    args, unknown = vocab_parser.parse_known_args()
    spacy_model = args.spacy_model if args.spacy_model else None
    disable_tag = args.disable_tag.split('_') if args.disable_tag else None
    main_generate_vocab(args.project, args.language_name, fasttext_model=args.fasttext_model, save_parent_folder=base_vocab_folder, spacy_model=spacy_model, disable_tag=disable_tag)
   