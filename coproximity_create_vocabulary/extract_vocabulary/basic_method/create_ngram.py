'''
Template to create a vocabulary and it synonyms. 
'''
import  json , os
from typing import  Callable

def save_all (to_save, vocab_folder) :
    '''
    Save all element of {to_save} into the folder {vocab_folder}. {vocab_folder} is a list of tuple (filename, what to save)
    '''
    for filename , to_save in to_save:
        with open(vocab_folder+filename , 'w' , encoding = 'utf8') as f :
            json.dump(to_save , f, sort_keys=True)



def create_ngram_framework (
    vocab_parent_folder:str,
    vocab_folder: str,
    preprocess: Callable,
    create_vocabulary : Callable ,
    create_synonyms : Callable ,
    process_all : Callable,
    post_process: Callable,
    word_reader  ,
    synonyms_reader  , 
    word_to_add = None,
    synonym_to_add = None,
    is_printing_progress: bool = False,
    ) :
    '''
    Template to create a vocabulary and it synonyms. 
    In the main version, creates a dictionary (here saved in main_dict_vocab.json) {expression : (processed version, if the expression is a synonym the words it represents
    otherwise an empty string, the number of word in the processed token)}

    vocab_parent_folder : Folder in which the different version of vocabulary will be saved
    vocab_folder        : Folder in which to save this vocabulary
    preprocess          : Method to prepare the data for the vocabulary extraction. 
    create_vocabulary        : Methods that takes in the path to a csv ngrams and return a set of ngrams (to consider our vocabulary), a dict of those ngrams
        to their processed versions, and the ngrams that were openly discarded (ie ngrams considered but rejected).
    create_synonyms     : A methods which takes a path to a csv of synonyms, 
        a path to a file where we will save the processed version of the synonyms previously cited, the set of the vocabulary, the set of the
        processed vocabulary. Return : a curated list of tuple (the synonyms, the processed synonyms, the the vocabulary's ngrams they
        are synonyms of) and a list of the rejected synonyms
    process_all         : Take the ngrams/synonyms dictionary and delete all synonyms whose processing is synonym of multiple ngrams and return the expressions with multiple synonyms 
    post_process        : What to do after the synonyms and vocabulary is created. 
    word_reader         : iterator that return for each iteration a token, to possibly add to the vocabulary, its clean format, its processed format and its associated score
    synonyms_reader     : iterator which return at each iteration a tuple (synonym to a token of word_reader, its processed format, the token)
    word_to_add         : list of additional tokens to add to the vocabulary
    synonym_to_add      : dict of additional synonyms to add to the synonym list (format {synonym: main token})
    is_printing_progress: print the progress of the vocabulary creation, in a stereotyped behavior. Used in electron front to get the progress of the process.
    '''
    #create the folder in which to save if it is not already created
    for to_create in [ vocab_parent_folder , vocab_folder ] :
        if not os.path.exists (to_create) :
            os.mkdir(to_create)

    if is_printing_progress :
        print('INFO_PRINT:preprocess:start', flush=True)

    preprocess()

    if is_printing_progress :
        print('INFO_PRINT:preprocess:end', flush=True)
        print('INFO_PRINT:create vocabulary:start', flush=True)

    #get all the synonyms from the synonym file
    global_synonyms = {}
    for redirect_from, _ , redirect_to in synonyms_reader :
        if redirect_from != redirect_to :
            redirect_to = redirect_to.replace('_',' ')
            redirect_from = redirect_from.replace('_',' ')
            for idx, elem in [(redirect_to, redirect_from), (redirect_from, redirect_to)] :
                if not idx in global_synonyms :
                    global_synonyms[idx] = set()
                global_synonyms[idx].add(elem)

    # get vocabulary
    set_tokens, processed_dict, to_save = create_vocabulary(word_reader, global_synonyms, word_to_add)

    #save processed version of the vocabulary and vocabulary
    save_all(to_save + [
        ('set_tokens.json' , list(sorted(set_tokens))) ,
    ], vocab_folder)
    del to_save

    if is_printing_progress :
        print('INFO_PRINT:create vocabulary:end', flush=True)
        print('INFO_PRINT:create synonyms:start', flush=True)

    # Get the synonyms of the vocabulary
    synonyms, ignored_synonyms, to_save = create_synonyms(synonyms_reader, set_tokens, set(processed_dict.values()), synonym_to_add)

    # group the discarded synonyms by their synonym to a list of the ngram they represent and why they were discarded
    word_to_bad_synonyms = {}
    for main, _ , synonym, problems in ignored_synonyms :
        if not synonym in word_to_bad_synonyms :
            word_to_bad_synonyms[synonym] = []
        word_to_bad_synonyms[synonym].append((main, problems))
        
    save_all(to_save + [
        ('ignored_synonyms.json' , ignored_synonyms) ,
        ('word_to_bad_synonyms.json' , word_to_bad_synonyms) ,
    ], vocab_folder)
    del ignored_synonyms, to_save

    if is_printing_progress :
        print('INFO_PRINT:create synonyms:end', flush=True)
        print('INFO_PRINT:simplify main_dict_vocab:start', flush=True)

    #init the global vocabulary representation with the synonyms
    main_dict_vocab = {
        syn_from : ( processed_syn_from.split(' '), syn_to , syn_from.count(' ') + 1)
        for (syn_from, processed_syn_from, syn_to) in synonyms
        if syn_from != syn_to
    }

    #add the non synonym to the global vocabulary representation
    for main_ngrams in set_tokens :
        main_dict_vocab[main_ngrams] = ( processed_dict[main_ngrams].split(' '), '' , main_ngrams.count(' ') + 1)
    
    main_dict_vocab, to_save = process_all (main_dict_vocab,)
    save_all(to_save, vocab_folder)
    del to_save

    # get only the dictionary of synonyms
    synonyms = {
        syn_from : syn_to
        for syn_from , (_,syn_to,_) in main_dict_vocab.items()
        if syn_to
    }

    save_all([('synonyms.json' , synonyms)], vocab_folder)

    if is_printing_progress :
        print('INFO_PRINT:simplify main_dict_vocab:end', flush=True)
        print('INFO_PRINT:post process:start', flush=True)

    #apply the post process method of the input
    post_process()

    if is_printing_progress :
        print('INFO_PRINT:post process:end', flush=True)
