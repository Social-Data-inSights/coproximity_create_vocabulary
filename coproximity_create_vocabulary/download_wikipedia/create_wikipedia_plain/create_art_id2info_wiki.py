'''
create the information files for the wikipedia dataset: the title and what to add to the url to get the page (which is also the title).
'''
import json, os
from coproximity_create_vocabulary.data_conf import base_vocab_folder

def create_id2info ( from_id2title_file , to_id2info_file, set_id_file = None ) :
    '''
    create the information files for the wikipedia dataset: the title and what to add to the url to get the page (which is also the title).
    Load the id to title dictionary from path {from_id2title_file}, create the metadata in a good form, 
    filter with {set_id_file} if some was given and save it to {to_id2info_file}
    '''
    with open(from_id2title_file) as f :
        id2title = json.load(f) 

    if set_id_file :
        with open(set_id_file, encoding='utf8') as f :
            set_id = set(json.load(f))
    else :
        set_id = None

    id2info = {
        art_id : {
            'url_id' : title ,  
            'title' : title
        }
        for art_id , title in id2title.items()
        if set_id is None or art_id in set_id
    }

    with open(to_id2info_file ,'w') as f :
        json.dump(id2info , f)

if __name__ == "__main__":
    #example of the use of this script, you need to have run update_wikipedia_dataset on the fr project 
    test_data_folder = base_vocab_folder + 'test_data/'
    if not os.path.exists(test_data_folder) :
        os.mkdir(test_data_folder)
    from_id2title_file  = test_data_folder + 'wikipedia/whole/meta_wiki/id_to_title.json'
    to_id2info_file = test_data_folder + 'wikipedia/whole/meta_wiki/id_to_info.json'
    set_id_file = test_data_folder + 'wikipedia/whole/meta_wiki/best_avg_250.000.json'
    create_id2info ( from_id2title_file , to_id2info_file, set_id_file )