'''
Get the categories of a Wikipedia article
'''

import json, sys
from coproximity_create_vocabulary.data_conf import base_vocab_folder

categories_folder = base_vocab_folder + 'whole/vocabulary/french/categories/'

def get_title(title, black_list_file = None) :
    '''
    get the categories of a an article whose title is {title}
    if  a set of categories {black_list_file} is given, return only the categories which are in both this set and the categories of {title}
    '''
    with open(categories_folder + 'title2categories.json', encoding='utf8') as f :
        title2categories = json.load(f)
    res = title2categories.get(title, set())

    if black_list_file :
        with open(categories_folder + black_list_file, encoding='utf8') as f :
            black_list = json.load(f)
        res -= set(black_list)

    return res

if __name__ == '__main__' :
    title = sys.argv[1]
    black_list_file = sys.argv[2] if len(sys.argv) > 3 else None
    print(get_title(title, black_list_file))