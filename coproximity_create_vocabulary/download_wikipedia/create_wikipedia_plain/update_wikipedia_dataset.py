'''
Update the wikipedia dataset by downloading the most recent wikipedia dump and recreating the plain wikipedia files
'''

import os, requests
from multiprocessing import Pool

from ade_imi.data_conf import base_data_folder
from split_articles_to_csv import split_articles_to_csv
from subset_whole_plain import get_subset_view_from_csv


def download_page(page_file, url ) : 
    '''
    Download an internet page {url} to a save file {page_file}
    '''   
    dump = requests.get(url, stream=True)
    with open(page_file, 'wb') as f :
        for chunk in dump.raw.stream(1024 * 1024 * 100, decode_content=False):
            if chunk:
                f.write(chunk)

def main_wikipedia_get_plain(language = 'fr', wikipedia_folder =base_data_folder + 'wikipedia/') :
    '''
    Download and recreate the plain wikipedia files for the language {language} and save it in {wikipedia_folder}
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
    for nb_view in [100, 250000, int(1e6)] :
        get_subset_view_from_csv(
            nb_view, 
            whole_folder + 'best_avg',  
            csv_extracted_file , 
            base_data_folder + 'whole/vocabulary/french/meta/sorted_view_wiki_over_years.csv',
            id2title_file = base_data_folder + 'whole/vocabulary/french/meta/id2title.json',
        )


def update_wikipedia_fr() :
    main_wikipedia_get_plain(language = 'fr', wikipedia_folder =base_data_folder + 'wikipedia/')
    '''to_preprocess_parse =  [ "wiki_1e6_fr2e5_", "wiki_1e6", "wiki", "wiki_fr2e5_"]
    with Pool(3) as p:
        p.map(update_vocabulary, to_preprocess_parse)'''

if __name__ == '__main__' :
    update_wikipedia_fr()