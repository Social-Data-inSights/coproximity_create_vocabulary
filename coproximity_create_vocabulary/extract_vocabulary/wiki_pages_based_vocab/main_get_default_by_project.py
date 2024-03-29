'''
Get the french vocabulary and synonyms from the most viewed wikipedia pages and their redirections
'''
from coproximity_create_vocabulary.download_wikipedia.get_pages_views.wikipedia_date_handle import get_most_recent_date
from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.wiki_title import (
    factory_create_title_wiki, get_title_from_dump_factory, create_smaller_multi_synonyms_text_file
)
from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.get_args import var_getter_by_project, get_preprocess_args, get_processed_file

from coproximity_create_vocabulary.extract_vocabulary.basic_method.create_ngram import create_ngram_framework
from coproximity_create_vocabulary.extract_vocabulary.basic_method.util_vocab import get_lemmatize_text_spacy
from coproximity_create_vocabulary.extract_vocabulary.basic_method.auto_reader_writer import auto_reader

from coproximity_create_vocabulary.data_conf import base_vocab_folder


default_whole_folder = base_vocab_folder + 'french/'
def create_default_wikititle(
    n_best_taken, spacy_model, disable_tag, fasttext_model, project, overwrite=False, print_progress_info=False, whole_folder :str = default_whole_folder
) :
    '''
    Create 4 vocabularies with the main method, with all combinations of : keeping accent/deleting accent and lower all non-acronyms/keep all uppercase 

    n_best_taken: size of the vocabulary to create
    spacy_model: spacy model used to lemmatize 
    disable_tag: tags to disable in the spacy model (to speed it up)
    fasttext_model: fasttext model to download
    project: name of the project from comes the articles
    overwrite: try to overwrite the processed files (but reuse the processed elements if they are shared by the old and new files)
    print_progress_info:  print the progress of the vocabulary creation, in a stereotyped behavior. Used in electron front to get the progress of the process.
    whole_folder: language folder where the data will be saved
    '''

    
    vocab_parent_folder = whole_folder + 'ngram_title_wiki/'
    
    #try to get the default spacy_model and getter_disable_tag if they exists and if we did not overwrite it.
    if project in var_getter_by_project :
        _ , _, _, _, _, _, getter_spacy_model, getter_disable_tag = var_getter_by_project[project]()
        if not spacy_model:
            spacy_model = getter_spacy_model
        if not disable_tag :
            disable_tag = getter_disable_tag

    article_list_file=  whole_folder + 'meta/sorted_view_wiki_over_years.csv'
    processed_article_file = get_processed_file(article_list_file, spacy_model, disable_tag, 'csv')
    synonyms_file = whole_folder + 'meta/synonyms.csv'
    processed_syn_file = get_processed_file(synonyms_file, spacy_model, disable_tag, 'csv')

    most_recent_date = get_most_recent_date(project)
    plain_dump_file = whole_folder + f'/dumps/wiki_{project}_dump-{most_recent_date}.xml.bz2'
    plain_index_dump_file = whole_folder + f'/dumps/wiki_{project}_dump_index-{most_recent_date}.xml.bz2'
    temp_dump_file = whole_folder + f'/dumps/wiki_{project}_dump_temp.xml.bz2'
    func_get_text_from_title_factory = lambda : get_title_from_dump_factory(plain_index_dump_file, plain_dump_file, temp_dump_file)

    for use_lower_processed in [False, True] :
        for use_no_accent_processed in [False, True] :
            if project in var_getter_by_project :
                stop_words , duplicate_stop_words, processed_method, synonym_to_ignore, word_to_add, synonym_to_add, _, _ = \
                    var_getter_by_project[project](use_lower_processed=use_lower_processed, use_no_accent_processed=use_no_accent_processed)
            else :
                stop_words , duplicate_stop_words, synonym_to_ignore, word_to_add, synonym_to_add =\
                    set() , set(), set(), [] , {}
                processed_method = get_lemmatize_text_spacy(spacy_model, disable_tag=disable_tag, use_lower = use_lower_processed, use_no_accent = use_no_accent_processed)

            new_str = f"{'_lower' if use_lower_processed else ''}{'_no_accent' if use_no_accent_processed else ''}"
            
            vocab_folder = vocab_parent_folder+'wiki_title_%s%s/'%( 'whole' if n_best_taken is None else 'best_%d'%n_best_taken, new_str)

            plain_article_title_reader = auto_reader(article_list_file, csv_args = dict(delimiter=';', quotechar='"'))
            plain_synonyms_reader = auto_reader(synonyms_file, csv_args = dict(delimiter=';', quotechar='"'))

            processed_list_select, processed_method_list, preprocessed_apply_rewikititle_on_lem_list = get_preprocess_args(spacy_model, disable_tag)

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
                whole_folder + f'cc.{fasttext_model}.300.bin',
                fasttext_model,
                apply_rewikititle_on_lem= not use_lower_processed,
                func_get_text_from_title_factory=func_get_text_from_title_factory,
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

default_wiki_title_fr_folder : str = base_vocab_folder + 'french/'
def main_wiki_fr_create_smaller_multi_synonyms_text_file(project, language_folder=default_wiki_title_fr_folder) :
    '''
    Given a path of a language folder{language_folder} which contains the finished main vocabularies, create a dict which, for the vocabulary folder which have the most synonyms which redirect to 
    multiple titles (i.e. all lower and no accent); for all titles which have a at least one synonym which redirect to multiple titles, 
    we get their text description (used for giving them a doc2vec vector with the fasttext) and save them.
    
    It is used to bundle together the pertinent texts and send them to the electron frontend to avoid loading all the Wikipedia texts in the electron.

    project: project (=language) from which we created {language_folder} (used to get the articles' content)
    '''
    use_lower_processed, use_no_accent_processed = True, True
    n_best_taken = 200000
    new_str = f"{'_lower' if use_lower_processed else ''}{'_no_accent' if use_no_accent_processed else ''}"
            
    vocab_folder = language_folder+'ngram_title_wiki/wiki_title_%s%s/'%('whole' if n_best_taken is None else 'best_%d'%n_best_taken, new_str)
    meta_folder = language_folder + 'meta/'

    most_recent_date = get_most_recent_date(project)
    plain_dump_file = language_folder + f'/dumps/wiki_{project}_dump-{most_recent_date}.xml.bz2'
    plain_index_dump_file = language_folder + f'/dumps/wiki_{project}_dump_index-{most_recent_date}.xml.bz2'
    temp_dump_file = language_folder + f'/dumps/wiki_{project}_dump_temp.xml.bz2'
    func_get_text_from_title_factory = lambda : get_title_from_dump_factory(plain_index_dump_file, plain_dump_file, temp_dump_file)


    create_smaller_multi_synonyms_text_file (vocab_folder, meta_folder, func_get_text_from_title_factory)

def main_default_wikititle(spacy_model, disable_tag, fasttext_model, project, print_progress_info=False, whole_folder :str = default_whole_folder) :
    '''
    To be used after downloading the dumps and having extracted the sorted article titles and redirections. Creates all the main vocabularies
    i.e. any combination of:
        - taking the best 1e5 titles/taking the best 2e5 titles
        - keeping accent/deleting accent 
        - lower all non-acronyms/keep all uppercase

    spacy_model: spacy model used to lemmatize 
    disable_tag: tags to disable in the spacy model (to speed it up)
    fasttext_model: fasttext model to use to create word2vec vectors from articles
    project: name of the project from comes the articles
    '''
    create_default_wikititle(
        int(1e5), spacy_model, disable_tag, fasttext_model, project, overwrite=True, print_progress_info=print_progress_info, whole_folder = whole_folder
    )
    create_default_wikititle(
        int(2e5), spacy_model, disable_tag, fasttext_model, project, overwrite=False, print_progress_info=print_progress_info, whole_folder = whole_folder
    )
    main_wiki_fr_create_smaller_multi_synonyms_text_file(project, language_folder=whole_folder)

if __name__ == '__main__' :
    main_default_wikititle(n_best_taken= 100000)
    main_default_wikititle(n_best_taken= 200000)
    main_wiki_fr_create_smaller_multi_synonyms_text_file()