"""
Get subsets of the whole wikipedia dataset. Split by size or number of views.
"""
import json , csv , textwrap
csv.field_size_limit(100000000)
from ade_imi.data_conf import base_data_folder

def get_subset_view_from_json (k:int , base_save : str = base_data_folder + 'wikipedia/best', input_file = base_data_folder + 'wikipedia/whole/fr_wiki_clean.json' , 
    article_list_file : str = base_data_folder + 'wikipedia/sorted_views_wiki.csv') :
    """
    get the kth most viewed wikipedia articles from a json dump {article_list_file} and will be save in a file
    Old version, now use get_subset_view_from_csv
    """
    #load the whole dataset
    with open(input_file, encoding='utf8') as f:
        plain = json.load(f)

    #get the ids of kth the most viewed articles
    article_views = []
    with open(article_list_file) as f:
        csv_reader = csv.reader(f, delimiter=';', quotechar='"' )
        next(csv_reader)
        for row in csv_reader :
            id_,views = row

            if id_ in plain :
                article_views += [id_]
            
    #the id of the k most viewed articles
    best_id_k = set ( article_views [:k] )
    #get the kth most viewed articles
    best_k = { id_ : article for id_ , article in plain.items() if id_ in best_id_k}

    #save the result
    with open('%s_%s.json'%(base_save , '.'.join(textwrap.wrap(str(k)[::-1] , 3))[::-1]) , 'w') as f:
        json.dump(best_k , f)

def get_subset_view_from_csv (k:int , base_save : str , input_file : str , article_list_file : str, id2title_file: str = None) :
    """
    get the kth most viewed wikipedia articles from the dump article_list_file and will be save in a file
    if a {id2title_file} load it and consider the article_list_file contains title and not ids
    """
    #load the dict title -> id if some was given
    if id2title_file :
        with open(id2title_file, encoding='utf8') as f :
            title2id = {}
            for id_, title in json.load(f).items() :
                if not title in title2id :
                    title2id[title] = []
                title2id[title].append(id_)

    else :
        title2id = None

    #get the ids of kth the most viewed articles
    article_views = []
    nb_added = 0
    with open(article_list_file, encoding='utf8') as f:
        csv_reader = csv.reader(f, delimiter=';', quotechar='"' )
        next(csv_reader)
        for id_or_title,_ in csv_reader :

            if title2id : 
                if id_or_title in title2id :
                    nb_added+=1
                    article_views.extend(title2id[id_or_title])
            else :
                nb_added+=1
                article_views.append(id_or_title)
            if nb_added >= k :
                break
            
    print(nb_added, len(article_views))
    best_id_k = set ( article_views )
    
    #get the kth most viewed articles
    plain_best_k = {}
    with open(input_file ,encoding='utf8' , newline='', errors = 'replace' ) as old_csv :
        reader = csv.reader(old_csv, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL ,)
        for art_id , plain in reader :
            if art_id in best_id_k :
                plain_best_k[art_id] = plain
                best_id_k.remove(art_id)
                if not best_id_k :
                    break

    print(len(plain_best_k))

    #save the result
    with open('%s_%s.json'%(base_save , '.'.join(textwrap.wrap(str(k)[::-1] , 3))[::-1]) , 'w') as f:
        json.dump(plain_best_k , f)


def get_subset_size (k:int) :
    """
    get the kth biggest wikipedia articles from the dump 
    """

    #load the whole dataset
    with open(base_data_folder + 'wikipedia/whole/fr_wiki_clean.json') as f:
        plain = json.load(f)

    #the id of the k biggest articles
    biggest_id_k = sorted(
        [ (name_article , len(article)) for name_article , article in plain.items() ] , 
        key = lambda x : x[1] , reverse = True
    ) [:k]
    biggest_id_k = {id_ for id_ , _ in biggest_id_k }

    #get the kth biggest articles
    biggest_k = {
        id_ : article
        for id_ , article in plain.items()
        if id_ in biggest_id_k
    }

    #save the result
    with open(base_data_folder + 'wikipedia/biggest_%s.json'%('.'.join(textwrap.wrap(str(k)[::-1] , 3))[::-1]) , 'w') as f:
        json.dump(biggest_k , f)

if __name__ == '__main__' :    
    '''
    whole_folder = base_data_folder + 'wikipedia/whole/'
    dump_file = whole_folder + f'wiki_fr_dump.xml.bz2'
    csv_extracted_file = whole_folder + f'wiki_fr_dump.csv'
    article_list_file = base_data_folder + 'whole/vocabulary/french/meta/sorted_view_wiki_over_years.csv'
    id2title_file = base_data_folder + 'whole/vocabulary/french/meta/id2title.json',
    '''

    whole_folder = base_data_folder + 'wikipedia_en/whole/'
    dump_file = whole_folder + f'wiki_en_dump.xml.bz2'
    csv_extracted_file = whole_folder + f'wiki_en_dump.csv'
    article_list_file = base_data_folder + 'whole/vocabulary/english/meta/sorted_view_wiki_over_years.csv'
    id2title_file = base_data_folder + 'whole/vocabulary/english/meta/id2title.json'

    for nb_view in [100, 250000, int(1e6)] :
        get_subset_view_from_csv(
            nb_view, 
            whole_folder + 'best_avg',  
            csv_extracted_file , 
            article_list_file,
            id2title_file = id2title_file,
        )
