'''
Download the subcategories by recursively requesting them to Wikipedia. Based on the structure of subcategories from the Wikipedia categories. 
(ex: section "Sous-catégories" from https://fr.wikipedia.org/wiki/Cat%C3%A9gorie:Cin%C3%A9ma)
Tuned only for french, but can be a base for other languages.
'''

import requests, urllib, os, json
from bs4 import BeautifulSoup

from coproximity_create_vocabulary.data_conf import base_vocab_folder

#methods who take a category name and return specific path to different type of 
page_name_to_filename = lambda wiki_page_name, max_depth : f"{wiki_page_name.replace('Catégorie:', '')}{ '_depth' + str(max_depth) if max_depth else ''}_wiki_page_subcategories.json"
page_name_to_trimmed_filename = lambda wiki_page_name, max_depth : f"{wiki_page_name.replace('Catégorie:', '')}{ '_depth' + str(max_depth) if max_depth else ''}_wiki_page_subcategories_trimmed.json"
category2flatten_set_categories = lambda category_name : f"{category_name}_flatten_set_categories.json"
#url format to get the categories from a request 
url_base = 'https://fr.wikipedia.org/w/api.php?action=categorytree&format=json&category=%s&options={"mode":0,"hideprefix":20,"showcount":true,"namespaces":false,"notranslations":false}&uselang=fr&formatversion=2'

def download_recursive_categories (wiki_page_name, depth, max_depth, already_done= set(), url_base=url_base) :
    '''
    Download recursively the subcategories of the page {wiki_page_name}. If a {max_depth} is given, stop recursion at depth {max_depth}.

    wiki_page_name : page from which to get the subcategories
    depth: current depth from the first query
    max_depth: depth after which we don't get the subcategories anymore
    already_done: set of pages whose categories were already requested. (So we already have it so we don't need to download them again)
    url_base: url format to get the categories from a Wikipedia title by filling its format
    '''
    print(wiki_page_name)
    
    cat_html = requests.get(url_base%wiki_page_name).json()['categorytree']['html']
    cat_soup = BeautifulSoup(cat_html, features='html.parser') 
    
    res = []
    for div in cat_soup.find_all('div', { 'class': 'CategoryTreeItem' }) :
        title = 'Catégorie:' + div.find('a', href=True).get_text()
        #is recursive checks if the current page has categories
        is_recursive = div.find_all('span', { 'class': 'CategoryTreeToggle' })
        
        
        if is_recursive and not title in already_done:
            #if there is no max depth or if we are did not reach it yet, recursively get the subcategories.
            if not max_depth or depth < max_depth :
                already_done.add(title)
                reccursive_res = download_recursive_categories (title, depth + 1,max_depth, already_done=already_done, url_base=url_base)
            else :
                reccursive_res = 'max_depth'
        else:
            reccursive_res = None
        res.append((title, reccursive_res))

    print('____ end:', depth, max_depth, wiki_page_name, len(res))
    return res

def download_all_categories (category_pages, save_folder) :
    '''
    Download recursively all the subcategories of the page {wiki_page_name} and save it in the folder {save_folder}
    '''
    for wiki_page_name in category_pages :
        save_file = save_folder + page_name_to_filename(wiki_page_name, None)
        if not os.path.exists(save_file) :
            print('start ===========', save_file)
            res = download_recursive_categories (wiki_page_name, 0 , None)
            with open(save_file, 'w', encoding='utf8') as f :
                json.dump(res, f)
            print('==================', wiki_page_name, '========================')
        else :
            print('==================', wiki_page_name, 'already done')


def download_all_categories_depth4 (category_pages, save_folder) :
    '''
    Download recursively all the subcategories up to the 4th recursion of the page {wiki_page_name} and save it in the folder {save_folder}
    '''
    max_depth = 4
    for wiki_page_name in category_pages :
        save_file = save_folder + page_name_to_filename(wiki_page_name, max_depth)
        if not os.path.exists(save_file) :
            print('start ===========', save_file)
            res = download_recursive_categories (wiki_page_name, 0, max_depth)
            with open(save_file, 'w', encoding='utf8') as f :
                json.dump(res, f)
            print('==================', wiki_page_name, '========================')
        else :
            print('==================', wiki_page_name, 'already done')


def flatten_wiki_subcategories(wiki_subcategories, base_set = set()) :
    '''
    Take the result {wiki_subcategories} of one of the download_all_categories method and  transform it into a set of categories
    '''
    for title, reccursive_wiki_subcategories in wiki_subcategories :
        base_set.add(title)
        if reccursive_wiki_subcategories and reccursive_wiki_subcategories != 'max_depth' :
            flatten_wiki_subcategories(reccursive_wiki_subcategories, base_set = base_set)
    return base_set

def flatten_all_wiki_subcategories (category_name2save_files, category2all_action, categories_folder, all_name = 'all') :
    '''
    Get a dictionary to a file {category_name2save_files} containing a {category name: file of their subcategories from one of the download_all_categories method } 
    and use flatten_wiki_subcategories to transform them into sets and save them into {categories_folder}.

    Also merge the subcategories into one file whose name will be based of {all_name} and whose merge logic will be {category2all_action}:
    for a category:
        - if {category2all_action}[category] == 'add', add its subcategories to the global set
        - if {category2all_action}[category] == 'sub', delete from the global set all the subcategories from the current set
    '''
    all_categories_flatten = set()
    #sorted is used so that categories to sub are after the categories to add  
    for category_name, save_files in sorted(category_name2save_files.items(), key = lambda x : category2all_action[x[0]]):
        #flatten all the categories
        curr_categories = set()
        for save_file in save_files:
            with open(categories_folder+save_file, encoding='utf8') as f :
                wiki_subcategories = json.load(f)

            flatten_wiki_subcategories(wiki_subcategories, base_set = curr_categories)

        with open(categories_folder + category2flatten_set_categories(category_name), 'w', encoding='utf8') as f :
            json.dump(list(curr_categories), f)

        #merge the subcategories to the global set
        all_action = category2all_action[category_name]
        if all_action == 'add' :
            all_categories_flatten |= curr_categories
        elif all_action == 'sub' :
            all_categories_flatten -= curr_categories

    if all_name :
        with open(categories_folder + category2flatten_set_categories(all_name), 'w', encoding='utf8') as f :
            json.dump(list(all_categories_flatten), f)
    


def reccursive_trim_categories(categories, to_trim_vocab):
    '''
    take {categories}, a result of one of the download_all_categories and  a list of string {to_trim_vocab}.
    If one of the string of {to_trim_vocab} is in a category of {categories}, delete it from {categories} with all its subcategories.
    '''
    res = []
    for category, rec_categories in categories:
        cat_low = category.lower()
        is_trimmed = False
        for to_trim_str in to_trim_vocab :
            if to_trim_str in cat_low :
                print(category, '/', to_trim_str, )
                is_trimmed = True
                break
        if is_trimmed :
            continue
            
        if rec_categories and rec_categories != 'max_depth' :
            rec_res = reccursive_trim_categories(rec_categories, to_trim_vocab)
        else :
            rec_res = rec_categories
            
        res.append((category, rec_res))
    return res

def trim_categories(cat_name, to_trim_vocab, categories_folder, category_name2save_files, category_name2trimmed_save_files) :
    '''
    Apply reccursive_trim_categories to the category {cat_name} with the list of string {to_trim_vocab}.

    categories_folder: folder in which to save and load the categories files
    category_name2save_files : {category name: file of their subcategories from one of the download_all_categories method } for loading the categories
    category_name2trimmed_save_files : {category name: file of their subcategories from one of the download_all_categories method } 
        for saving the trimmed categories
    '''
    print('trim___________________________', cat_name)
    for base_file, trimmed_file in zip(category_name2save_files[cat_name], category_name2trimmed_save_files[f'{cat_name}_trim'],) :
        with open(categories_folder + base_file, encoding='utf8') as f :
            base_categories = json.load(f)
        trimmed_categories = reccursive_trim_categories(base_categories, to_trim_vocab)

        with open(categories_folder + trimmed_file, 'w', encoding='utf8') as f :
            json.dump(trimmed_categories, f)

if __name__ == '__main__' :
    categories_folder = base_vocab_folder + 'wikipedia/whole/categories/'
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
        #diaspora include anti-sémitisme (this  is not a political statement, but an example of what is lost if we ignore diaspora in the vocabulary)
        'Personne':['fiction', 'ville', 'série', 'film', 's\u00e9rie', 'adaptation', 'catégorie:catégorie', 'nommé', 'diaspora', 'autobiograp'],
    }
    for cat_name, to_trim_vocab in delete_categories_over_reach.items():
        trim_categories(cat_name, to_trim_vocab)


    #flatten the trimmed subcategories
    del category_name2trimmed_save_files['Personne_trim']
    flatten_all_wiki_subcategories (
        {'Personne_trim': [page_name_to_trimmed_filename('Personne', 4)],}, category2trim_all_action, categories_folder, all_name=None
    )
    
    flatten_all_wiki_subcategories (category_name2trimmed_save_files, category2trim_all_action, categories_folder, all_name='all_trimmed')
