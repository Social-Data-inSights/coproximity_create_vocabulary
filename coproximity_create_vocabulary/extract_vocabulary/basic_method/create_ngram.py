'''
Template to create a vocabulary and its synonyms. 
'''
import  json , os
from typing import  Callable

def save_all (to_save, save_folder) :
    '''
    Save all element of {to_save} into the folder {save_folder}. {to_save} is a list of tuple (filename, what to save)
    '''
    for filename , to_save in to_save:
        with open(save_folder+filename , 'w' , encoding = 'utf8') as f :
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
    preprocess          : Method to prepare the data for the vocabulary extraction. The method takes no argument
    create_vocabulary   : Methods to get the main tokens of the vocabulary, takes in:
            - the path to a csv reader (from auto_reader_writer.py) (this will be{word_reader})
            - a dict of the synonyms ({synonym: main token})
            - a list of additional word to add (this will be {word_to_add}).
        Return: 
            - a set of ngrams (to be considered our vocabulary)
            - a dict of those ngrams to their processed versions
            - a list of additional content to save as [(name of a file, jsonable element to save)]
    create_synonyms     : A methods to create the synonyms, takes in:
            - a path to a to a csv reader (from auto_reader_writer.py) (this will be{synonyms_reader}), 
            - the set of the vocabulary
            - the set of the processed vocabulary
            - a dict of the additional synonyms (this will be {synonym_to_add}).
        Return : 
            - a curated list of tuple (the synonyms, the processed synonyms, the the vocabulary's ngrams they are synonyms of) 
            - a list of the rejected synonyms as [(synonym, preprocessed synonym, main token, why the synonym was rejected)]
            - a list of additional content to save as [(name of a file, jsonable element to save)]
    process_all         : Take the ngrams/synonyms dictionary and delete all synonyms whose processing is synonym of multiple ngrams 
        Return: this filtered result and additional elements to save as a list [(name of a file, jsonable element to save)] 
    post_process        : What to do after the synonyms and vocabulary is created. 
    word_reader         : iterator that return for each iteration a token (to possibly add to the vocabulary), its clean format, its processed format and its associated score
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

    #prepare the data for the vocabulary creation 
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

    # generate the set of tokens of the vocabulary
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
    
    #clean main_dict_vocab (mainly used to separate synonyms redirecting to multiple main tokens from the rest of the vocabulary)
    main_dict_vocab, to_save = process_all (main_dict_vocab,)
    save_all(to_save, vocab_folder)
    del to_save

    # get only the dictionary of synonyms
    synonyms = {
        syn_from : syn_to
        for syn_from , (_,syn_to,_) in main_dict_vocab.items()
        if syn_to
    }

    save_all([
        ('synonyms.json' , synonyms),
        ('main_dict_vocab.json' , main_dict_vocab),    
    ], vocab_folder)

    if is_printing_progress :
        print('INFO_PRINT:simplify main_dict_vocab:end', flush=True)
        print('INFO_PRINT:post process:start', flush=True)

    #apply the post process method of the input
    post_process()

    if is_printing_progress :
        print('INFO_PRINT:post process:end', flush=True)
