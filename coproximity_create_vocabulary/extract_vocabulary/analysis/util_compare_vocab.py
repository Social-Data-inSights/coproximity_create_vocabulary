'''
Compare set of tokens or synonyms of 2 different vocabulary.
'''
import json
from coproximity_create_vocabulary.data_conf import base_vocab_folder

def compare_vocabulary(vocab_folder_a, vocab_folder_b) :
    '''
    Compare the set of tokens of the 2 vocabulary contained in the folder {vocab_folder_a} and {vocab_folder_b}
    '''
    list_set_articles = []
    for vocab_folder in [vocab_folder_a, vocab_folder_b] :
        with open (vocab_folder + 'set_tokens.json', encoding='utf8') as f :
            list_set_articles.append(json.load(f))
    set_articles_a, set_articles_b = list_set_articles
    
    return set(set_articles_a) - set(set_articles_b), set(set_articles_b) - set(set_articles_a)

def compare_synonyms(vocab_folder_a, vocab_folder_b) :
    '''
    Compare the synonyms of the 2 vocabulary contained in the folder {vocab_folder_a} and {vocab_folder_b}
    '''
    list_synonyms = []
    for vocab_folder in [vocab_folder_a, vocab_folder_b] :
        with open (vocab_folder + 'synonyms.json', encoding='utf8') as f :
            list_synonyms.append({ from_[0].upper() + from_[1:]: to_ for from_, to_ in json.load(f).items() })
    synonyms_a, synonyms_b = list_synonyms
    
    return set(synonyms_a.items()) - set(synonyms_b.items()), set(synonyms_b.items()) - set(synonyms_a.items())

def compare_main_dict_vocab(main_dict_vocab_a, main_dict_vocab_b) :
    '''
    TODOC
    ''' 
    main_dict_vocab_list = []
    for main_dict_vocab_file in [main_dict_vocab_a, main_dict_vocab_b] :
        with open(main_dict_vocab_file, encoding='utf8') as f :
            main_dict_vocab_list.append(json.load(f))

    set_words = [
        {word for word, vocab_info in main_dict_vocab.items() if not vocab_info[1]  }
        for main_dict_vocab in main_dict_vocab_list
    ]
    set_synonyms = [
        {
            (word, vocab_info[1]) 
            for word, vocab_info in main_dict_vocab.items()
            #we need to keep only the synonyms to words in both vocabulary because it's obvious they do not share synonyms when they don't have the "synonymed to" word
            if vocab_info[1]  and vocab_info[1] in set_words[0] and vocab_info[1] in set_words[1]
        }
        for main_dict_vocab in main_dict_vocab_list
    ]

    diff_vocab_a_min_b = list(sorted(set_words[0] - set_words[1]))
    diff_vocab_b_min_a = list(sorted(set_words[1] - set_words[0]))

    diff_syns_a_min_b = list(sorted({(from_, to_) for from_, to_ in set_synonyms[0] - set_synonyms[1] }))
    diff_syns_b_min_a = list(sorted({(from_, to_) for from_, to_ in set_synonyms[1] - set_synonyms[0] }))

    return diff_vocab_a_min_b, diff_vocab_b_min_a, diff_syns_a_min_b, diff_syns_b_min_a

def save_compare_vocabulary(vocab_folder_a, vocab_folder_b, save_file, which_comparison) :
    '''
    Compare the set of tokens or synonyms (depending on {which_comparison}) of the 2 vocabulary contained in the folder {vocab_folder_a} and {vocab_folder_b}
    and save the result at path {save_file}
    '''
    if which_comparison == 'vocab' :
        a_min_b, b_min_a = compare_vocabulary(vocab_folder_a, vocab_folder_b)
    elif which_comparison == 'synonyms' :
        a_min_b, b_min_a = compare_synonyms(vocab_folder_a, vocab_folder_b)
    else :
        raise Exception(f'unknown which_comparison: {which_comparison}')

    main_folder_a, main_folder_b = vocab_folder_a.split('/')[-2], vocab_folder_b.split('/')[-2]
    with open(save_file, 'w', encoding='utf8') as f :
        json.dump({
            f'{main_folder_a}-{main_folder_b}' : list(a_min_b),
            f'{main_folder_b}-{main_folder_a}' : list(b_min_a),
        }, f, indent=4)


if __name__ == '__main__' :
    save_folder = base_vocab_folder + 'data_analysis/vocab_analysis/'
    french_parent_vocab_folder = base_vocab_folder + 'french/ngram_title_wiki/'
    
    main_100Kvocab_folder = french_parent_vocab_folder + 'wiki_title_best_100000/'
    del_cat_100Kvocab_folder = french_parent_vocab_folder + 'wiki_title_del_book_music_films_best_100000/'

    save_compare_vocabulary(main_100Kvocab_folder, del_cat_100Kvocab_folder, save_folder + 'change_filter_categories.json', 'vocab')