'''
use wiki title as vocab and wikitionnary as synonyms. Language is french
Need the result from synonym_dictionnary_wiktionnary.py
'''

from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.wiki_title import factory_create_title_wiki
from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.get_args import get_french_var
from coproximity_create_vocabulary.extract_vocabulary.basic_method.create_ngram import create_ngram_framework, get_processed_file

from coproximity_create_vocabulary.data_conf import base_vocab_folder

test_data_folder = base_vocab_folder + 'test_data/'
def main_wikititle_wiktionary(n_best_taken, base_data_folder, use_id_to_title=True, overwrite=False, additional_folder_name = '', print_progress_info=False) :
    '''
    create the vocabulary for the Wiktionnary in french
    
    n_best_taken: size of the vocabulary to create
    base_data_folder: data folder of https://github.com/matthieuDev/Projet_AdE-IMI/ where we will search the Wikipedia articles 
    use_id_to_title: if true consider that the wikipedia title csv is made of the wikipedia id and give a id2title_file to create_processed_title
    overwrite: try to overwrite the processed files (but reuse the processed elements if they are shared by the old and new files)
    additional_folder_name: suffix to add to a folder to change its name, to use to change the name of a vocabulary folder
    print_progress_info:  print the progress of the vocabulary creation, in a stereotyped behavior. Used in electron front to get the progress of the process.
    '''
    stop_words , duplicate_stop_words, processed_method, synonym_to_ignore, word_to_add, synonym_to_add, spacy_model, disable_tag = get_french_var()

    data_folder = base_data_folder + '/'
    vocab_parent_folder = base_vocab_folder + 'french/ngram_title_wiki/'
    article_list_file=  data_folder + 'wikipedia/sorted_view_wiki_over_years.csv'
    processed_article_file = get_processed_file(article_list_file, spacy_model, disable_tag, 'csv')
    whole_folder :str = data_folder + 'wikipedia/whole/'

    
    synonyms_file = data_folder + 'whole/thesaurus/wiktionary_synonyms.csv'
    vocab_folder = vocab_parent_folder+'wiktionnary%s_%s/'%(additional_folder_name, 'whole' if n_best_taken is None else 'best_%d'%n_best_taken)
    processed_syn_file = get_processed_file(synonyms_file, spacy_model, disable_tag, 'csv')

    preprocess_wiki, create_vocabulary_wiki, create_synonyms, process_all, post_process = factory_create_title_wiki (
        stop_words , 
        duplicate_stop_words, 
        processed_method, 
        synonym_to_ignore,
        whole_folder, 
        n_best_taken, 
        vocab_folder,
        article_list_file,
        processed_article_file,
        synonyms_file, 
        processed_syn_file,
        whole_folder + 'cc.fr.300.bin',
        'fr',
        word_to_add,
        synonym_to_add,
        use_id_to_title=use_id_to_title,
        overwrite=overwrite,
        print_progress_info=print_progress_info,
    )


    create_ngram_framework (
        vocab_parent_folder,
        vocab_folder,
        preprocess_wiki,
        create_vocabulary_wiki ,
        create_synonyms ,
        process_all,
        post_process,
        processed_article_file,
        processed_syn_file
    )

if __name__ == '__main__' :
    main_wikititle_wiktionary(n_best_taken= 100000, base_data_folder=test_data_folder)