'''
Get the french vocabulary and synonyms from the most viewed wikipedia pages and their redirections while deleting titles whose categories are considered a film/book/music 
'''
from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.wiki_title import (
    factory_create_title_wiki, plain_get_text_from_title_factory
)
from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.get_args import get_french_var, get_preprocess_args, get_processed_file
from coproximity_create_vocabulary.extract_vocabulary.basic_method.create_ngram import create_ngram_framework

from coproximity_create_vocabulary.extract_vocabulary.basic_method.auto_reader_writer import auto_reader

from coproximity_create_vocabulary.data_conf import base_vocab_folder

import json



test_data_folder = base_vocab_folder + 'test_data/'
def factory_vocabulary_get_problems_and_ask_if_stopping(
    wiki_title2categories_file, black_list_category_file, white_list_category_file=None,
) :
    '''
    Filter function factory for filtering article with unwanted categories

    wiki_title2categories_file: file containing a json of a dict {article id: list of the categories of the article}
    black_list_category_file: list of categories to reject
    white_list_category_file: list of categories to keep even if they are in {black_list_category_file}

    return:
    a function that takes a title, clean title, processed title, and the set of tokens in the current vocabulary 
        and return [if the article is in a forbidden category, name of this problem for the vocabulary creator]
    '''
    with open(wiki_title2categories_file, encoding='utf8') as f :
        wiki_title2categories = { title: set(categories) for title, categories in json.load(f).items()  }

    with open(black_list_category_file, encoding='utf8') as f :
        black_list_category = set(json.load(f))
    
    if white_list_category_file :
        with open(white_list_category_file, encoding='utf8') as f :
            white_list_category = set(json.load(f))
    else :
        white_list_category = set()

    def get_problems_and_ask_if_stopping_delete_bad_categories (title, clean_title, processed_title, set_articles) :
        curr_black_listed = wiki_title2categories.get(title, set()).intersection(black_list_category)
        curr_black_listed -= white_list_category
        return (
            [(True, f'bad categories: {list(curr_black_listed)[0]}')]
            if curr_black_listed else 
            [(False, 'bad categories')]
        )


    return get_problems_and_ask_if_stopping_delete_bad_categories


def main_wikititle_del_book_music_films (
    n_best_taken, base_data_folder, use_id_to_title=False, overwrite=False, additional_folder_name = '', print_progress_info=False,
    use_lower_processed = False, use_no_accent_processed = False,
) :
    '''
    n_best_taken: size of the vocabulary to create
    base_data_folder: data folder of https://github.com/matthieuDev/Projet_AdE-IMI/ where we will search the Wikipedia articles 
    use_id_to_title: if true consider that the wikipedia title csv is made of the wikipedia id and give a id2title_file to create_processed_title
    overwrite: try to overwrite the processed files (but reuse the processed elements if they are shared by the old and new files)
    additional_folder_name: suffix to add to a folder to change its name, to use to change the name of a vocabulary folder
    print_progress_info:  print the progress of the vocabulary creation, in a stereotyped behavior. Used in electron front to get the progress of the process.
    use_lower_processed: if true, the processing sets the result as lowercase
    use_no_accent_processed: if true, the processing deletes the accents
    '''
    categories_folder = base_vocab_folder + 'whole/vocabulary/french/categories/'
    wiki_title2categories_file = categories_folder + 'title2categories.json'
    black_list_category_file = categories_folder + 'all_trimmed_flatten_set_categories.json'

    whole_folder :str = base_vocab_folder + 'french/'
    vocab_parent_folder = base_vocab_folder + 'french/ngram_title_wiki/'
    
    _ , _, _, _, _, _, spacy_model, disable_tag = get_french_var()

    article_list_file=  whole_folder + 'meta/sorted_view_wiki_over_years.csv'
    processed_article_file = get_processed_file(article_list_file, spacy_model, disable_tag, 'csv')
    synonyms_file = whole_folder + 'meta/synonyms.csv'
    processed_syn_file = get_processed_file(synonyms_file, spacy_model, disable_tag, 'csv')

    func_get_text_from_title_factory = lambda : plain_get_text_from_title_factory(
        base_data_folder + '/wikipedia/whole/meta_wiki/title_to_id.json',
        base_data_folder + '/wikipedia/best_avg_250.000.json'
    )


    stop_words , duplicate_stop_words, processed_method, synonym_to_ignore, word_to_add, synonym_to_add, spacy_model, _ = \
        get_french_var(use_lower_processed=use_lower_processed, use_no_accent_processed=use_no_accent_processed)

    new_str = f"{'_lower' if use_lower_processed else ''}{'_no_accent' if use_no_accent_processed else ''}"
    
    vocab_folder = vocab_parent_folder+'wiki_title_del_book_music_films%s_%s%s/'%(additional_folder_name, 'whole' if n_best_taken is None else 'best_%d'%n_best_taken, new_str)

    plain_article_title_reader = auto_reader(article_list_file, csv_args = dict(delimiter=';', quotechar='"'))
    plain_synonyms_reader = auto_reader(synonyms_file, csv_args = dict(delimiter=';', quotechar='"'))

    processed_list_select, processed_method_list, preprocessed_apply_rewikititle_on_lem_list = get_preprocess_args(spacy_model)
    get_problems_and_ask_if_stopping_delete_bad_categories = factory_vocabulary_get_problems_and_ask_if_stopping(
        wiki_title2categories_file, black_list_category_file
    )

    preprocess_wiki, create_vocabulary_wiki, create_synonyms, process_all, post_process = factory_create_title_wiki (
        stop_words , 
        duplicate_stop_words,
        processed_list_select, processed_method_list, preprocessed_apply_rewikititle_on_lem_list,
        processed_method,
        synonym_to_ignore,
        whole_folder, 
        n_best_taken, 
        vocab_folder,
        plain_article_title_reader,
        processed_article_file,
        plain_synonyms_reader, 
        processed_syn_file,
        whole_folder + 'cc.fr.300.bin',
        'fr',
        apply_rewikititle_on_lem= not use_lower_processed,
        func_get_text_from_title_factory=func_get_text_from_title_factory,
        use_id_to_title=use_id_to_title,
        overwrite=overwrite,
        is_printing_progress=print_progress_info,
        vocab_additional_filter = get_problems_and_ask_if_stopping_delete_bad_categories,
    )    

    name_processed_version = f'{spacy_model}{new_str}'
    article_title_reader = auto_reader(processed_article_file, list_select=['main', 'clean_main', name_processed_version, 'count'], csv_args = dict(delimiter=';', quotechar='"'))
    synonyms_reader = auto_reader(processed_syn_file, list_select=['syn_from', name_processed_version, 'syn_to'], csv_args = dict(delimiter=';', quotechar='"'))

    create_ngram_framework (
        vocab_parent_folder,
        vocab_folder,
        preprocess_wiki,
        create_vocabulary_wiki ,
        create_synonyms ,
        process_all,
        post_process,
        article_title_reader,
        synonyms_reader,
        word_to_add,
        synonym_to_add,
        is_printing_progress=print_progress_info,
    )



if __name__ == '__main__' :
    main_wikititle_del_book_music_films(n_best_taken= 100000, base_data_folder=test_data_folder,  use_id_to_title=False)