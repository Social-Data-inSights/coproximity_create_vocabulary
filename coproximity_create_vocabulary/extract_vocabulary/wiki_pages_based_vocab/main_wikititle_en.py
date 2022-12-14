'''
Get the english vocabulary and synonyms from the most viewed wikipedia pages and their redirections.
'''

from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.wiki_title import (
    factory_create_title_wiki, create_translate_title2text_id_factory, create_smaller_multi_synonyms_text_file
)
from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.get_args import get_english_var, get_preprocess_args, get_processed_file
from coproximity_create_vocabulary.extract_vocabulary.basic_method.create_ngram import create_ngram_framework

from coproximity_create_vocabulary.extract_vocabulary.basic_method.auto_reader_writer import auto_reader

from coproximity_create_vocabulary.data_conf import base_vocab_folder

def main_wikititle(n_best_taken, use_id_to_title=False, overwrite=False, additional_folder_name = '', print_progress_info=False) : 
    '''
    n_best_taken: size of the vocabulary to create
    '''
    
    whole_folder :str = base_vocab_folder + '/whole/vocabulary/english'
    vocab_parent_folder = base_vocab_folder + '/whole/vocabulary/english/ngram_title_wiki/'
    
    _ , _, _, _, _, _, spacy_model, disable_tag = get_english_var()

    article_list_file=  whole_folder + 'meta/sorted_view_wiki_over_years.csv'
    processed_article_file = get_processed_file(article_list_file, spacy_model, disable_tag, 'csv')
    synonyms_file = whole_folder + 'meta/synonyms.csv'
    processed_syn_file = get_processed_file(synonyms_file, spacy_model, disable_tag, 'csv')

    translate_token2text_id = create_translate_title2text_id_factory(
        base_vocab_folder + '/wikipedia/whole/meta_wiki/title_to_id.json',
        base_vocab_folder + '/wikipedia/best_avg_250.000.json',
    )

    for use_lower_processed in [False, True] :
        for use_no_accent_processed in [False, True] :
            stop_words , duplicate_stop_words, processed_method, synonym_to_ignore, word_to_add, synonym_to_add, spacy_model, _ = \
                get_english_var(use_lower_processed=use_lower_processed, use_no_accent_processed=use_no_accent_processed)
            
            new_str = f"{'_lower' if use_lower_processed else ''}{'_no_accent' if use_no_accent_processed else ''}"
            
            vocab_folder = vocab_parent_folder+'wiki_title%s_%s%s/'%(additional_folder_name, 'whole' if n_best_taken is None else 'best_%d'%n_best_taken, new_str)
            
            plain_article_title_reader = auto_reader(article_list_file, csv_args = dict(delimiter=';', quotechar='"'))
            plain_synonyms_reader = auto_reader(synonyms_file, csv_args = dict(delimiter=';', quotechar='"'))

            processed_list_select, processed_method_list, preprocessed_apply_rewikititle_on_lem_list = get_preprocess_args(spacy_model, disable_tag=['parser', 'ner'])

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
                whole_folder + 'cc.en.300.bin',
                'en',
                apply_rewikititle_on_lem= not use_lower_processed,
                func_get_title_factory=translate_token2text_id,
                use_id_to_title=use_id_to_title,
                overwrite=overwrite,
                is_printing_progress=print_progress_info,
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

def main_wiki_en_create_smaller_multi_synonyms_text_file() :
    '''
    Create a dict which, for the vocabulary folder which have the most synonyms which redirect to multiple titles (i.e. all lower and no accent),
    for all titles which have a at least one synonym which redirect to multiple titles, we get their text description (used for giving them a doc2vec vector with the fasttext)
    an save them.
    
    It is used to bundle together the pertinent texts and send them to the electron frontend to avoid loading all the Wikipedia texts in the electron.
    '''
    use_lower_processed, use_no_accent_processed = True, True
    n_best_taken = 200000
    new_str = f"{'_lower' if use_lower_processed else ''}{'_no_accent' if use_no_accent_processed else ''}"
            
    wiki_title_en_folder :str = base_vocab_folder + '/whole/vocabulary/english'
    vocab_folder = wiki_title_en_folder+'ngram_title_wiki/wiki_title_%s%s/'%('whole' if n_best_taken is None else 'best_%d'%n_best_taken, new_str)
    meta_folder = wiki_title_en_folder + 'meta/'

    translate_token2text_id = create_translate_title2text_id_factory(
        base_vocab_folder + '/wikipedia/whole/meta_wiki/title_to_id.json',
        base_vocab_folder + '/wikipedia/best_avg_250.000.json',
    )

    create_smaller_multi_synonyms_text_file (vocab_folder, meta_folder, func_get_title_factory=translate_token2text_id)

if __name__ == '__main__' :
    main_wikititle(n_best_taken= 100000, overwrite=True)
    main_wikititle(n_best_taken= 200000, overwrite=True)
    main_wiki_en_create_smaller_multi_synonyms_text_file()