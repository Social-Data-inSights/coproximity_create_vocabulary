'''
Get all you need to filter based on categories for the french wiki titles
'''

from coproximity_create_vocabulary.download_wikipedia.word_info.get_categories_from_xml import get_categories_from_xml
from coproximity_create_vocabulary.download_wikipedia.word_info.download_categories_sub_categories_from_wiki_page import (
    download_all_categories, download_all_categories_depth4, flatten_all_wiki_subcategories, page_name_to_filename, page_name_to_trimmed_filename,
    trim_categories
)

from coproximity_create_vocabulary.data_conf import base_vocab_folder
import os

categories_folder = base_vocab_folder + 'french/categories/'

split_path = categories_folder.split('/')
for i in [ -3, -2, -1, len(split_path)] :
    new_path = '/'.join(split_path[:i])
    if not os.path.exists(new_path) :
        os.mkdir(new_path)

#extract the categories for the wikipedia articles
from_xml = base_vocab_folder + 'french/dumps/wiki_fr_dump.xml.bz2'
id2categories_filename = f'{categories_folder}id2categories.json'
title2categories_filename = f'{categories_folder}title2categories.json'
print(id2categories_filename)
get_categories_from_xml (from_xml , id2categories_filename, title2categories_filename ) 

personne_file = categories_folder + 'personne_sub_categories.json' 
id2title_file = base_vocab_folder + 'wikipedia/whole/meta_wiki/id_to_title.json'

#Group different categories 
category_name2wiki_name = {
    'Film': ['Catégorie:Film', 'Catégorie:Série télévisée'],
    'Livres' : ['Catégorie:Littérature'],
    'Musique': ['Catégorie:Musique'],
    'Personne': ['Catégorie:Personne'],
}

#download the subcategories of category_name2wiki_name
download_all_categories([category_page for category in ['Film'] for category_page in category_name2wiki_name[category]], categories_folder)
download_all_categories_depth4([category_page for category in ['Livres', 'Musique', 'Personne'] for category_page in category_name2wiki_name[category]], categories_folder)

#save files for each category before and after being trimmed
category_name2save_files = {
    'Film': [page_name_to_filename('Film', None), page_name_to_filename('Série télévisée', None)],
    'Livres' : [page_name_to_filename('Littérature', 4)],
    'Musique': [page_name_to_filename('Musique', 4)],
    'Personne': [page_name_to_filename('Personne', 4)],
}
category_name2trimmed_save_files = {
    'Film_trim': [page_name_to_trimmed_filename('Film', None), page_name_to_filename('Série télévisée', None)],
    'Livres_trim' : [page_name_to_trimmed_filename('Littérature', 4)],
    'Musique_trim': [page_name_to_trimmed_filename('Musique', 4)],
    'Personne_trim': [page_name_to_trimmed_filename('Personne', 4)],
}
#dict of the merge action used in flatten_all_wiki_subcategories for the non trimmed and trimmed sets
category2all_action = {
    'Film': 'add',
    'Livres' : 'add',
    'Musique': 'add',
    'Personne': 'sub',
}
category2trim_all_action = {category + '_trim': action for category, action in category2all_action.items()}

flatten_all_wiki_subcategories (category_name2save_files, category2all_action, categories_folder)

#Trim the subcategory trees
delete_categories_over_reach = {
    'Film': ['récompens', 'artiste', 'narrateur', 'lauréat', 'oscar', 'césar', 'acteur', 'actrice'],
    'Livres' : [
        'humanité', 'écrivain', 'éditeur', 'histoire', 'lieu', 'mouvement', 'lexique', 'person', 'prix', 'recherche', 'technique', 'théorie', 'élève',
        'autobiographe', 'artiste', 'narrateur', 'lauréat', 'critique', 
    ],
    'Musique': [
        'compositrice', 'compositeur', 'histoire', 'industrie', 'lieu', 'musicologie', 'culture', 'technique' , 'théorie', 'musicien', 'rappeur',
        'chanteur', 'chanteuse', 'artiste', 'musicien', 'narrateur', 'lauréat', 'élève',
    ],
    #diaspora include anti-sémitisme
    'Personne':['fiction', 'ville', 'série', 'film', 's\u00e9rie', 'adaptation', 'catégorie:catégorie', 'nommé', 'diaspora', 'autobiograp'],
}
for cat_name, to_trim_vocab in delete_categories_over_reach.items():
    trim_categories(cat_name, to_trim_vocab, categories_folder, category_name2save_files, category_name2trimmed_save_files)


#flatten the trimmed subcategories
del category_name2trimmed_save_files['Personne_trim']
flatten_all_wiki_subcategories (
    {'Personne_trim': [page_name_to_trimmed_filename('Personne', 4)],}, category2trim_all_action, categories_folder, all_name=None
)

flatten_all_wiki_subcategories (category_name2trimmed_save_files, category2trim_all_action, categories_folder, all_name='all_trimmed')
