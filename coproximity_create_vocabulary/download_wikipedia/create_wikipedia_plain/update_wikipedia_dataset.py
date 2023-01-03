'''
Update the wikipedia dataset by downloading the most recent wikipedia dump and recreating the plain wikipedia files
'''

import os
from multiprocessing import Pool

from coproximity_create_vocabulary.data_conf import base_vocab_folder
from coproximity_create_vocabulary.download_wikipedia.create_wikipedia_plain.split_articles_to_csv import split_articles_to_csv
from coproximity_create_vocabulary.download_wikipedia.create_wikipedia_plain.subset_whole_plain import get_subset_view_from_csv

from coproximity_create_vocabulary.extract_vocabulary.basic_method.util_vocab import download_page

def main_wikipedia_get_plain(language, wikipedia_folder, subset_sorted_article_list_file=None, subset_id2title_file=None) :
    '''
    Download and recreate the plain wikipedia files for the language {language} and save it in {wikipedia_folder}
    
    subset_sorted_article_list_file(optional): sorted list of articles or id, we use it to create subset of the created big dump.
    subset_id2title_file: (must be given with a {subset_sorted_article_list_file}) allows to give a path to a json file : { article id: article title},
        if one is given, consider {subset_sorted_article_list_file} to be titles and use the json to get the ids to keep
        if none is given, consider {subset_sorted_article_list_file} to be ids
    '''
    whole_folder = wikipedia_folder + 'whole/'

    dump_file = whole_folder + f'wiki_{language}_dump.xml.bz2'
    csv_extracted_file = whole_folder + f'wiki_{language}_dump.csv'

    for folder in [wikipedia_folder, whole_folder] :
        if not os.path.exists(folder) :
            os.mkdir(folder)
            
    url_dump = f'https://dumps.wikimedia.org/{language}wiki/latest/{language}wiki-latest-pages-articles-multistream.xml.bz2'

    #download the new dump
    download_page(dump_file, url_dump )
    #parse the xml dump to a csv dump
    split_articles_to_csv (whole_folder, from_xml_bz2 = dump_file , dump_save_to=csv_extracted_file, threshold_skip_little = 100)
    print('split_articles_to_csv done')
    if subset_sorted_article_list_file and os.path.exists(subset_sorted_article_list_file):
        for nb_view in [100, 250000, int(1e6)] :
            get_subset_view_from_csv(
                nb_view, 
                whole_folder + 'best_avg',  
                csv_extracted_file , 
                subset_sorted_article_list_file,
                id2title_file = subset_id2title_file,
            )

if __name__ == '__main__' :
    #to test the 
    test_data_folder = base_vocab_folder + 'test_data/'
    if not os.path.exists(test_data_folder) :
        os.mkdir(test_data_folder)
    
    subset_sorted_article_list_file = base_vocab_folder +'french/meta/sorted_view_wiki_over_years.csv'
    subset_id2title_file = base_vocab_folder +'french/meta/id2title.json'
    main_wikipedia_get_plain(
        language = 'fr',
        wikipedia_folder = test_data_folder + 'wikipedia/',
        subset_sorted_article_list_file = subset_sorted_article_list_file,
        subset_id2title_file = subset_id2title_file
    )