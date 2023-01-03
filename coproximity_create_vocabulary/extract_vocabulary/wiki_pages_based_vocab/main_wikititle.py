'''
Get the french vocabulary and synonyms from the most viewed wikipedia pages and their redirections
'''
from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.wiki_title import (
    factory_create_title_wiki, create_translate_title2text_id_factory, create_smaller_multi_synonyms_text_file
)
from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.get_args import get_french_var, get_preprocess_args, get_processed_file
from coproximity_create_vocabulary.extract_vocabulary.basic_method.create_ngram import create_ngram_framework

from coproximity_create_vocabulary.extract_vocabulary.basic_method.auto_reader_writer import auto_reader

from coproximity_create_vocabulary.data_conf import base_vocab_folder


default_whole_folder = base_vocab_folder + '/whole/vocabulary/french/'
def main_wikititle(
    n_best_taken, use_id_to_title=False, overwrite=False, additional_folder_name = '', print_progress_info=False, whole_folder :str = default_whole_folder
) :
    '''
    n_best_taken: size of the vocabulary to create
    use_id_to_title: if true consider that the wikipedia title csv is made of the wikipedia id and give a id2title_file to create_processed_title
    overwrite: try to overwrite the processed files (but reuse the processed elements if they are shared by the old and new files)
    additional_folder_name: suffix to add to a folder to change its name, to use to change the name of a vocabulary folder
    print_progress_info:  print the progress of the vocabulary creation, in a stereotyped behavior. Used in electron front to get the progress of the process.
    whole_folder TODOC
    '''

    
    vocab_parent_folder = whole_folder + 'ngram_title_wiki/'
    
    _ , _, _, _, _, _, spacy_model, disable_tag = get_french_var()

    article_list_file=  whole_folder + 'meta/sorted_view_wiki_over_years.csv'
    processed_article_file = get_processed_file(article_list_file, spacy_model, disable_tag, 'csv')
    synonyms_file = whole_folder + 'meta/synonyms.csv'
    processed_syn_file = get_processed_file(synonyms_file, spacy_model, disable_tag, 'csv')

    func_get_text_from_title_factory = create_translate_title2text_id_factory(
        base_vocab_folder + '/wikipedia/whole/meta_wiki/title_to_id.json',
        base_vocab_folder + '/wikipedia/best_avg_250.000.json',
    )


    for use_lower_processed in [False, True] :
        for use_no_accent_processed in [False, True] :
            stop_words , duplicate_stop_words, processed_method, synonym_to_ignore, word_to_add, synonym_to_add, spacy_model, _ = \
                get_french_var(use_lower_processed=use_lower_processed, use_no_accent_processed=use_no_accent_processed)

            new_str = f"{'_lower' if use_lower_processed else ''}{'_no_accent' if use_no_accent_processed else ''}"
            
            vocab_folder = vocab_parent_folder+'wiki_title%s_%s%s/'%(additional_folder_name, 'whole' if n_best_taken is None else 'best_%d'%n_best_taken, new_str)

            plain_article_title_reader = auto_reader(article_list_file, csv_args = dict(delimiter=';', quotechar='"'))
            plain_synonyms_reader = auto_reader(synonyms_file, csv_args = dict(delimiter=';', quotechar='"'))

            processed_list_select, processed_method_list, preprocessed_apply_rewikititle_on_lem_list = get_preprocess_args(spacy_model)

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

default_wiki_title_fr_folder : str = base_vocab_folder + '/whole/vocabulary/french/'
def main_wiki_fr_create_smaller_multi_synonyms_text_file(wiki_title_fr_folder=default_wiki_title_fr_folder) :
    '''
    Create a dict which, for the vocabulary folder which have the most synonyms which redirect to multiple titles (i.e. all lower and no accent),
    for all titles which have a at least one synonym which redirect to multiple titles, we get their text description (used for giving them a doc2vec vector with the fasttext)
    an save them.
    
    It is used to bundle together the pertinent texts and send them to the electron frontend to avoid loading all the Wikipedia texts in the electron.
    '''
    use_lower_processed, use_no_accent_processed = True, True
    n_best_taken = 200000
    new_str = f"{'_lower' if use_lower_processed else ''}{'_no_accent' if use_no_accent_processed else ''}"
            
    vocab_folder = wiki_title_fr_folder+'ngram_title_wiki/wiki_title_%s%s/'%('whole' if n_best_taken is None else 'best_%d'%n_best_taken, new_str)
    meta_folder = wiki_title_fr_folder + 'meta/'

    func_get_text_from_title_factory = create_translate_title2text_id_factory(
        base_vocab_folder + '/wikipedia/whole/meta_wiki/title_to_id.json',
        base_vocab_folder + '/wikipedia/best_avg_250.000.json',
    )

    create_smaller_multi_synonyms_text_file (vocab_folder, meta_folder, func_get_text_from_title_factory)

if __name__ == '__main__' :
    main_wikititle(n_best_taken= 100000, use_id_to_title=False)
    main_wikititle(n_best_taken= 200000, use_id_to_title=False)
    main_wiki_fr_create_smaller_multi_synonyms_text_file()