'''
create the tf-idfs of the expert for wikipedia for :
    articles of the expert as a normal dataset
    articles that links to articles of experts
'''
import json , os , sys
from shutil import copyfile
from typing import Dict
from ade_imi.data_conf import base_data_folder
from ade_imi.create_datasets.get_tfidf.tfidf_wiki_title import main_tfidf
from ade_imi.dataset_dump_to_plain.rts_to_plain.create_expert_tfidf import get_sum_count , get_details

def get_expert_wikipedia(base_expert_tfidf : str  , expert_wiki_folder : str ) -> Dict[str,str] :
    """
    get the dict expert to their article (if they have one)

    base_expert_tfidf : json file of a dict that has as keys the names of the experts
    expert_wiki_folder: path to a folder to save the results
    """
    #load the experts' name
    with open(base_expert_tfidf ) as f :
        experts = [expert.strip(' ') for expert in (json.load(f))]

    #load the titles
    with open( base_data_folder + 'wikipedia/whole/meta_wiki/title_to_id.json' ) as f:
        wiki_title_to_id = json.load(f)

    #load the articles which can be experts
    wiki_experts_ambi = {
        exp : [ title for title in wiki_title_to_id if title.startswith(exp)] 
        for exp in experts 
    }
    #delete the experts that have no such article
    wiki_experts_ambi = {
        name:articles
        for name,articles in wiki_experts_ambi.items()
        if articles
    }

    with open(expert_wiki_folder+'wiki_experts_ambi.json' , 'w' ) as f :
        json.dump(wiki_experts_ambi , f)

    #disambiguate or delete the ambiguous experts
    del wiki_experts_ambi['Sergio Rossi']
    wiki_experts_ambi['Jacques Levy'] = ['Jacques Levy (géographe)']
    del wiki_experts_ambi['Philippe Morel']
    wiki_experts_ambi['François Walter']=['François Walter (historien)'] 
    wiki_experts_ambi['Pierre Margot']=['Pierre Margot (scientifique)']
    del wiki_experts_ambi['Edward Mitchell']
    del wiki_experts_ambi['Michel Maillard']
    wiki_experts_ambi['Jean-François Bert']=['Jean-François Bert']
    del wiki_experts_ambi['Bernard Noël']
    del wiki_experts_ambi['Philippe Lefebvre']

    #now take, for each experts that was not deleted, the only article that is still linked to them
    wiki_experts = {
        name : articles[0]
        for name , articles in wiki_experts_ambi.items()
    }

    #save and return results
    with open(expert_wiki_folder+'wiki_experts.json' , 'w' ) as f :
        json.dump(wiki_experts , f)

    return wiki_experts


def get_expert_tfidfs_pages( expert_tfidf_wiki_folder , to_copy_idf_file , vocab_folder , wiki_experts) :
    '''
    create the tf-idfs of the articles of the experts for wikipedia

    expert_tfidf_wiki_folder  : Folder in which the tf-idf will be saved
    to_copy_idf_file    : a directory to an idf to copy to have an idf over wikipedia and not on an handfull of article on the experts
    vocab_folder   : folder in which the ngrams are saved 
    base_expert_tfidf   : a directory to a json that contains all the experts


    value saved         : the tf-idfs of the experts
    '''
    #load wikipedia's article title
    with open( base_data_folder + 'wikipedia/whole/meta_wiki/title_to_id.json' ) as f:
        wiki_title_to_id = json.load(f)

    len(wiki_experts)

    #creates the main folder and idf folder if they do not exist
    for to_create in [expert_tfidf_wiki_folder , expert_tfidf_wiki_folder+'idfs/'] :
        if not os.path.exists (to_create) :
            os.mkdir(to_create)
        
    #copy the idf so that the main_tfidf script can use it
    idf_file = expert_tfidf_wiki_folder +'idfs/' + to_copy_idf_file.split('/')[-1]
    if not os.path.exists (idf_file) :
        copyfile(to_copy_idf_file , idf_file)

    #get the plain articles of the experts
    with open(base_data_folder + 'wikipedia/whole/fr_wiki_clean.json') as f:
        plain = json.load(f)
    experts_plain = {
        exp : plain[wiki_title_to_id[exp_page]]
        for exp ,exp_page in wiki_experts.items()
        if wiki_title_to_id[exp_page] in plain
    }
    with open(expert_tfidf_wiki_folder+'clean.json' , 'w') as f :
            json.dump(experts_plain,f)
    del plain

    # apply the tf-idf on the experts' article

    base_dir = expert_tfidf_wiki_folder
    base_name = 'clean.json'

    idf_schemes = ['ids'  ]
    tf_schemes = ['ln' ] 
    keeps = [75] 
    use_multi = False 
    nb_split = 1
    tfidf_file_base = 'tfidf'
    ngram = 7 
    ambi_tfidf_file = vocab_folder + 'ambi_tfidfs.json' 

    main_tfidf(
        base_dir = base_dir ,
        base_name = base_name, 
        idf_schemes = idf_schemes ,
        tf_schemes = tf_schemes , 
        keeps = keeps , 
        use_multi = use_multi , 
        nb_split = nb_split ,
        tfidf_file_base = tfidf_file_base ,
        ngram = ngram ,
        vocab_folder  = vocab_folder ,
        ambi_tfidf_file = ambi_tfidf_file 
    )

    #save the result with a better name and without the experts from which we could not extract a tf-idf 
    with open (base_dir+'tfidfs/%dgram_%s_%s_%s_%s.json'%(ngram,tfidf_file_base,idf_schemes[0],tf_schemes[0],str(keeps[0]) if keeps[0] else 'all')) as f :
        tfidf_expert = json.load(f)
    tfidf_expert = {
        expert:scores
        for expert , scores in tfidf_expert.items()
        if scores
    }
    with open(base_dir+'tfidfs/expert_tfidf.json','w') as f :
        json.dump(tfidf_expert , f)

    #get the for each experts the tf-idf and the id of his article
    with open( base_data_folder + 'wikipedia/whole/meta_wiki/title_to_id.json' ) as f:
        wiki_title_to_id = json.load(f)
    details_expert = {
        expert : {wiki_title_to_id[wiki_experts[expert]]:scores}
        for expert , scores in tfidf_expert.items()
    }
    with open(base_dir + 'expert_details.json' , 'w' ) as f :
        json.dump(details_expert,f)

def get_expert_tfidfs_ref (wiki_experts : Dict[str,str] , expert_wiki_folder :str , keep_threshold : int , wiki_tfidf : str)  :
    """
    create en expert tf-idf by summing the tf-idfs score of words over all article that link to the article of an experts. 
    Also creates a dictionary from expert to such articles

    wiki_experts        : dictionary from an expert to its article
    expert_wiki_folder  : folder in which to save the result
    keep_threshold      : number of words by expert to keep 
    wiki_tfidf          : path to a json containing the tf-idfs to use.
    """

    # get for each experts, the articles in which they were cited
    expert_cited_file = expert_wiki_folder + 'expert_cited.json'
    #if it already exists load it
    if os.path.exists(expert_cited_file) :
        with open(expert_cited_file) as f :
            expert_cited = json.load(f)
    #otherwise make it
    else :
        #dict expert : (article name, article linked)
        expert_cited = {
            name : ( '[[%s]]'%article , [])
            for name , article in wiki_experts.items()
        }

        # search which article has a link to an expert's article
        xml_folders = base_data_folder + 'wikipedia/whole/articles_wiki_text/'
        for xml_folder in os.listdir(xml_folders) :
            print(xml_folder)
            xml_folder = xml_folders + xml_folder +'/'
            for xml_file in os.listdir(xml_folder) :
                with open(xml_folder+xml_file , encoding = 'UTF8') as f :
                    curr_file = f.read()
                #for each article search if they are not in the current article
                for name , (website,concerned_pages) in expert_cited.items() :
                    if website in curr_file :
                        print(xml_file,name)
                        expert_cited [name] = (website , concerned_pages + [xml_file])
        
        #get for each experts the article id (i.e. the file without the extension)
        expert_cited = {
            name : [page.split('.')[0] for page in  concerned_pages]
            for name , (website,concerned_pages) in expert_cited.items()
        }
        #save result
        with open(expert_cited_file , 'w' ) as f :
            json.dump( expert_cited , f)

    #load the tf-idf
    with open(wiki_tfidf , encoding='utf8' ) as f :
        from_tfidf = json.load(f)
    #filter the article that are not in the tf-idf
    expert_cited = {
        name : [page for page in  concerned_pages if page in from_tfidf]
        for name , (concerned_pages) in expert_cited.items()
        if  [page for page in  concerned_pages if page in from_tfidf]
    }

    #get the tf-idf for each expert
    expert_tfidf = {
        expert :
        get_sum_count(from_tfidf , articles , keep_threshold)
        for expert , articles in expert_cited.items()
    }

    #get the tf-idf of articles linked to the experts' articles for each experts
    expert_details = {
        expert :
        get_details(from_tfidf , articles , expert_tfidf[expert])
        for expert , articles in expert_cited.items()
    }

    #save results
    with open(expert_wiki_folder + 'expert_tfidf.json' , 'w' , encoding='utf8' ) as f :
        json.dump(expert_tfidf,f)

    with open(expert_wiki_folder + 'expert_details.json' , 'w' , encoding='utf8' ) as f :
        json.dump(expert_details,f)


def main( 
    expert_wiki_folder :str ,
    expert_tfidf_wiki_folder :str ,
    to_copy_idf_file :str ,
    vocab_folder :str ,
    base_expert_tfidf :str ,
    wiki_tfidf :str ,
    keep_threshold_expert : int
    ) :
    """
    get the dict expert to their article (if they have one) and create the tf-idf of expert on both the experts' article and on articles that link to them

    expert_wiki_folder      : path to a folder to save the results
    expert_tfidf_wiki_folder: Folder in which the tf-idf of get_expert_tfidfs_pages will be saved
    to_copy_idf_file        : a directory to an idf to copy to have an idf over wikipedia and not on an handfull of article on the experts
    vocab_folder       : folder in which the ngrams are saved
    base_expert_tfidf       : json file of a dict that has as keys the names of the experts
    wiki_tfidf              : path to a json containing the tf-idfs to use in get_expert_tfidfs_ref
    keep_threshold_expert   : number of words by expert to keep
    """
    # create the folder if they do not exist
    for fold in [expert_wiki_folder , expert_tfidf_wiki_folder] :
        if not os.path.exists(fold) :
            os.mkdir(fold)

    #get the experts' article
    if os.path.exists(expert_wiki_folder+'wiki_experts.json') :
        print('wiki_experts found')
        with open(expert_wiki_folder+'wiki_experts.json') as f :
            wiki_experts = json.load(f)
    else :
        print('wiki_experts not found')
        wiki_experts = get_expert_wikipedia(
            base_expert_tfidf , expert_wiki_folder
        )

    #create the expert tf-idf
    get_expert_tfidfs_pages( expert_tfidf_wiki_folder , to_copy_idf_file , vocab_folder , wiki_experts)
    get_expert_tfidfs_ref (wiki_experts , expert_wiki_folder , keep_threshold_expert , wiki_tfidf)


if __name__ == '__main__' :

    expert_wiki_folder      = base_data_folder + 'wikipedia/experts/'
    expert_tfidf_wiki_folder= expert_wiki_folder + 'expert_tfidf/' 
    to_copy_idf_file        = base_data_folder + 'wikipedia/main_wiki/idfs/idf_7gram_ids.json'
    vocab_folder       = base_data_folder + 'whole/vocabulary/french/ngram_title_wiki/wiki_title_best_100000/'
    base_expert_tfidf       = base_data_folder + 'RTS/coproximity/main_rts/tfidfs/expert_tfidf.json' 
    wiki_tfidf              = base_data_folder + 'wikipedia/main_wiki/tfidfs/simp_7gram_tfidf_ids_ln_75.json'
    keep_threshold_expert   = 75

    main(
        expert_wiki_folder ,
        expert_tfidf_wiki_folder,
        to_copy_idf_file,
        vocab_folder,
        base_expert_tfidf,
        wiki_tfidf,
        keep_threshold_expert
    )