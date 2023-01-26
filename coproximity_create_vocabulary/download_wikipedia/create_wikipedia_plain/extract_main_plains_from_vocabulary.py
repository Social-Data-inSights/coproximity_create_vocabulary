'''
TODOC
'''
from coproximity_create_vocabulary.data_conf import base_vocab_folder
from coproximity_create_vocabulary.download_wikipedia.get_pages_views.wikipedia_date_handle import get_most_recent_date
from coproximity_create_vocabulary.download_wikipedia.create_wikipedia_plain.split_articles_to_csv import split_articles_to_csv
from coproximity_create_vocabulary.download_wikipedia.create_wikipedia_plain.subset_whole_plain import get_subset_view_from_csv

import csv, os

def get_best_titles(language, nb_words) :
    '''
    TODOC
    '''
    sorted_article_list_file = f'{base_vocab_folder}{language}/meta/sorted_view_wiki_over_years.csv'

    #get the ids of kth the most viewed articles
    article_views = []
    nb_added = 0
    with open(sorted_article_list_file, encoding='utf8') as f:
        csv_reader = csv.reader(f, delimiter=';', quotechar='"' )
        next(csv_reader)
        for title,_ in csv_reader :

            nb_added+=1
            article_views.append(title.replace('_', ' '))
            if nb_added >= nb_words :
                break
                
    return set(article_views)

def extract_main_plains_from_vocabulary(language, wiki_project) :
    '''
    TODOC
    '''
    wiki_most_recent_date = get_most_recent_date(wiki_project)
    dump_file = f'{base_vocab_folder}{language}/dumps/wiki_{wiki_project}_dump-{wiki_most_recent_date}.xml.bz2'

    wikipedia_folder = f'{base_vocab_folder}extracted_wikipedia/{language}/'
    plain_file = f'{wikipedia_folder}/wiki_plain_{language}_1e6-{wiki_most_recent_date}.csv'
    for folder in [
        base_vocab_folder,
        base_vocab_folder + 'extracted_wikipedia/',
        base_vocab_folder + 'extracted_wikipedia/' + language,
    ]:
        if not os.path.exists(folder):
            os.mkdir(folder)
            
    if os.path.exists(plain_file):
        os.remove(plain_file)

    article_views_1e6 = get_best_titles(language, int(1e6))

    split_articles_to_csv (
        wikipedia_folder,
        from_xml_bz2=dump_file ,
        dump_save_to=plain_file, 
        get_only_title = article_views_1e6
    )

    subset_sorted_article_list_file = base_vocab_folder +f'{language}/meta/sorted_view_wiki_over_years.csv'
    subset_id2title_file = base_vocab_folder + f'{language}/meta/id2title.json'
    for nb_view in [100, 250000, int(1e6)] :
        get_subset_view_from_csv(
            nb_view, 
            wikipedia_folder + 'best_avg',  
            plain_file , 
            subset_sorted_article_list_file,
            id2title_file = subset_id2title_file,
        )


if __name__ == '__main__':
    for language, wiki_project in [
        ('french', 'fr'),
    ]:
        extract_main_plains_from_vocabulary(language, wiki_project)