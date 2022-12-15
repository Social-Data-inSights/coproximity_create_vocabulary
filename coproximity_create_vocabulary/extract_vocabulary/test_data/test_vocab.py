'''
Test the vocabulary creation with different inputs and processing
'''
from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.wiki_title import factory_create_title_wiki
from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.get_args import get_french_var, get_preprocess_args, get_processed_file
from coproximity_create_vocabulary.extract_vocabulary.basic_method.create_ngram import create_ngram_framework

from coproximity_create_vocabulary.extract_vocabulary.basic_method.auto_reader_writer import auto_reader

from coproximity_create_vocabulary.data_conf import base_vocab_folder

import os

whole_folder = base_vocab_folder + 'test_data/vocabulary/'
vocab_parent_folder = whole_folder + 'ngram_title_wiki/'
meta_folder = whole_folder + 'meta/'

split_meta_folder = meta_folder.split('/')
new_folder = ''
for add_folder in split_meta_folder :
    new_folder += add_folder + '/'
    print(new_folder, os.path.exists(new_folder))
    if not os.path.exists(new_folder):
        os.mkdir(new_folder)

for filename in os.listdir(meta_folder) :
    filepath = meta_folder + filename
    if os.path.exists(filepath) :
        os.remove(filepath)

for i in range(-4,0) :
    folder = '/'.join(meta_folder.split('/')[:i])
    if not os.path.exists(folder) :
        os.mkdir(folder)

translate_token2text_id = None

_ , _, _, _, _, _, spacy_model, disable_tag = get_french_var()
n_best_taken = 1000
delimiter = 'a'
quotechar = '"'

for extension, list_select_article, list_select_synonyms in [
    ('_csv.csv', ['word', 'score'], ['from', 'to']),
    ('_dict.json', None, None),
    ('_dict2.json', ['word', 'score'], ['from', 'to']),
    ('_list.json', [1, 3], [1, 3]),
] :
    additional_folder_name = extension.split('.')[0]
    article_list_file=  f'list_words{extension}'
    processed_article_file = get_processed_file(meta_folder + article_list_file, spacy_model, disable_tag, 'csv')
    synonyms_file = f'synonyms{extension}'
    processed_syn_file = get_processed_file(meta_folder + synonyms_file, spacy_model, disable_tag, 'csv')
    
    for use_lower_processed in [False, True] :
        for use_no_accent_processed in [False, True] :
            stop_words , duplicate_stop_words, processed_method, synonym_to_ignore, word_to_add, synonym_to_add, spacy_model, _ = \
                get_french_var(use_lower_processed=use_lower_processed, use_no_accent_processed=use_no_accent_processed)

            new_str = f"{'_lower' if use_lower_processed else ''}{'_no_accent' if use_no_accent_processed else ''}"

            vocab_folder = vocab_parent_folder+'wiki_title%s_%s%s/'%(additional_folder_name, 'whole' if n_best_taken is None else 'best_%d'%n_best_taken, new_str)

            plain_article_title_reader = auto_reader(article_list_file, list_select_article, csv_args = dict(delimiter=delimiter, quotechar=quotechar), has_header=True)
            plain_synonyms_reader = auto_reader(synonyms_file, list_select_synonyms, csv_args = dict(delimiter=delimiter, quotechar=quotechar), has_header=True)

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
                func_get_title_factory=translate_token2text_id,
                use_id_to_title=False,
                overwrite=True,
                is_printing_progress=False,
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
                is_printing_progress=False,
            )