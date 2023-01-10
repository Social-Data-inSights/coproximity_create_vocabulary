'''
Template for the different methods necessary to make create_ngram.py works
'''

import os, csv, json, time
from coproximity_create_vocabulary.extract_vocabulary.basic_method.auto_reader_writer import auto_reader, auto_writer

def preprocess_synonyms_factory(preprocess_method, processed_list_select) :
    '''
    Factory to create a function which process the synonyms and save it so that it is not needed to be done at every vocabulary creation.
    To be used as a preprocessing

    preprocess_method: the method to process the synonym, it takes in the synonym, the main token it redirects to, a dictionary of the already processed
        and return a list of element to write, the size of this list should be constant and of same size as {processed_list_select}
        This list should be [synonym, *(one or many preprocessed synonym), the main token it redirects to]
    processed_list_select: name of the column for the created csv in which the processed synonyms will be saved
    '''
    def create_preprocessed_synonyms (synonym_reader , save_file, overwrite = False, is_printing_progress = False, ) :
        '''
        method which take an iterator {synonym_reader} which return at each iteration a tuple (synonym, main token), apply the {preprocess_method} to the synonym 
        and save them in {save_file} as a csv with column's name {processed_list_select}
        preprocess_method can return multiple results, for multiple processed elements

        overwrite: if False, don't redo the processing if a file already exists at {save_file}, if True, redo the processing even if there already is one saved, if there is already one,
            reuse its processed results.
        is_printing_progress: if True, print the progress of the vocabulary creation, in a stereotyped behavior. Used in electron front to get the progress of the process.
        '''
        #print the start of this function
        if is_printing_progress :
            print('INFO_PRINT:preprocess synonyms:start', flush=True)
        if os.path.exists(save_file) and not overwrite:
            print(f'preprocessed synonyms {save_file} already calculated')
        else :
            #count number of element in the reader
            if is_printing_progress :
                nb_synonyms = 0
                for _ in synonym_reader :
                    nb_synonyms += 1

            already_processed = {}
            #can happen if overwrite
            #load the previous processed elements
            if os.path.exists(save_file) :
                reader = auto_reader(save_file, csv_args = dict(delimiter=';', quotechar='"'))
                for main, *processed_mains , _ in reader :
                    already_processed[main] = processed_mains
                reader.close()

            
            writer = auto_writer(save_file, csv_args = dict(delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL), list_select=processed_list_select)
            print(synonym_reader.filepath,'synonyms_file')
            for i, (main , synonym) in enumerate(synonym_reader) :
                if is_printing_progress and not i % 1000 :
                    print(f'INFO_PRINT:preprocess synonyms:count:{i}/{nb_synonyms}', flush=True)

                to_write, is_writing = preprocess_method(main, synonym, already_processed)
                if is_writing :
                    writer.writerow(*to_write)
        #print the end of this function
        if is_printing_progress :
            print('INFO_PRINT:preprocess synonyms:end', flush=True)

    return create_preprocessed_synonyms

def create_preprocess_list_words_factory (preprocess_method, processed_list_select) :
    '''
    Factory to create a function which process the tokens of the vocabulary and save it so that it is not needed to be done at every vocabulary creation.
    To be used as a preprocessing

    preprocess_method: the method to process the tokens, takes in a token, a count score, a dict of already preprocessed tokens,
        and return a list of element to write, the size of this list should be constant and of same size as {processed_list_select}
        This list should be [token, clean token (for example, for Wikipedia, it used for deleting the '_'), *(one or many preprocessed token), the count score]
    processed_list_select: name of the column for the created csv in which the processed synonyms will be saved
    '''
    def create_preprocess_list_words (csv_word_reader , id2token_file, save_file, overwrite=False, is_printing_progress = False,) :
        '''
        method which take an iterator {csv_word_reader} which return at each iteration iteration a tuple (token, score), apply the {preprocess_method} to the token
        and save them in {save_file} as a csv with column's name {processed_list_select}
        preprocess_method can return multiple results, for multiple processed elements

        id2token_file: if, in Wikipedia style, the base elements are id and not the token itself, you can give to this argument a path to a json of a dict 
            {id: true token} to be used to get the token from those ids.
        overwrite: if False, don't redo the processing if a file already exists at {save_file}, 
            if True, redo the processing even if there already is one saved. If there is already one, reuse its processed results.
        is_printing_progress: if True, print the progress of the vocabulary creation, in a stereotyped behavior. Used in electron front to get the progress of the process.         
        '''
        if is_printing_progress :
            print('INFO_PRINT:preprocess words:start', flush=True)
        if id2token_file :
            with open(id2token_file) as f :
                id2token = json.load(f) 
        else :
            id2token = None     

        if os.path.exists(save_file) and not overwrite :
            print(f'preprocessed words {save_file} already calculated')
        else :
            if is_printing_progress :
                nb_lines = 0
                for _ in csv_word_reader :
                    nb_lines += 1

            already_processed = {}
            #can happen if overwrite
            #load the previous processed elements
            if os.path.exists(save_file) :
                reader = auto_reader(save_file, csv_args = dict(delimiter=';', quotechar='"'))
                for token, clean_token, *processed_token , _ in reader :
                    already_processed[token] = (clean_token, processed_token)
                reader.close()

            read = csv_word_reader
            writer = auto_writer(save_file, csv_args = dict(delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL), list_select=processed_list_select)
            for i, (id_, count) in enumerate(read) :
                if is_printing_progress and not i % 1000 :
                    print(f'INFO_PRINT:preprocess words:count:{i}/{nb_lines}', flush=True)
                #the id2token is supposed to take an id and return the associated true token, if id2token is None, the id_ is already the token 
                if not id2token or id_ in id2token :
                    if id2token :
                        token = id2token[id_]
                    else :
                        token = id_

                    to_write, is_writing = preprocess_method(token, count, already_processed)
                    if is_writing :
                        writer.writerow(*to_write)
                                
        if is_printing_progress :
            print('INFO_PRINT:preprocess words:end', flush=True)
    return create_preprocess_list_words

def create_vocabulary_factory(get_problems_and_ask_if_stopping, added_word_processed) :
    '''
    Factory for a create_vocabulary to give to create_ngram.create_ngram_framework

    get_problems_and_ask_if_stopping: function that takes a token, its clean form, its processed form and the list of the current vocabulary and return 
        - the list of problems (list of reason why this token was discarded, if we add this token it is empty)
        - the token, clean token, and processed token (that way we can make change to them in the method) 
        - boolean if we need to stop the vocabulary creation
    added_word_processed: method which takes a word of {word_to_add} and process it
    '''
    def create_vocabulary (word_reader, global_synonyms, word_to_add) :
        '''
        a create_vocabulary to give to create_ngram.create_ngram_framework
        create a vocabulary

        word_reader: iterator that return for each iteration a token (to possibly add to the vocabulary), its clean format, its processed format and its associated score
        global_synonyms: dict {synonym: main token of word_reader} for all synonym given in the {synonyms_reader} of create_ngram.create_ngram_framework
        word_to_add: list of additional tokens to add to the vocabulary
        '''

        list_tokens = []
        processed_dict = {}
        discarded_token = []
        t = time.time()
            
        #set of all added tokens 
        set_token = set()
        for i,(token, clean_token, processed_token, views) in enumerate(word_reader) :
            if not i %10000 :
                print(i,token, processed_token, views,len(set_token), time.time()-t)
                t=time.time()

            problems, token, clean_token, processed_token, is_stopping = get_problems_and_ask_if_stopping(token, clean_token, processed_token, set_token)
            #if there is no problem, add to the vocabulary
            if not problems:
                processed_dict[clean_token] = processed_token

                #add the token to the list and set
                list_tokens += [(clean_token)]
                set_token.add(clean_token)
                
            else :
                #save which problem prevented this token to be in the vocabulary
                discarded_token.append((token, problems))

            if is_stopping :
                break

        #add additional vocabulary
        if word_to_add :
            set_token.update(word_to_add)
            for word in word_to_add :
                processed_word = added_word_processed(word)
                processed_dict[word] = processed_word

        return set_token, processed_dict, [('discarded_token.json', discarded_token)]
    return create_vocabulary

def create_synonyms_factory (get_problems, added_synonyms_processed) :
    '''
    Factory for a create_synonyms to give to create_ngram.create_ngram_framework

    get_problems: function that takes as input a synonym, its processed version and the token it represents, and return :
        - the synonym, processed synonym and its represented token (that way we can make change to them in the method)
        - the list of problems (list of reason why this token was discarded, if we add this token it is empty)
    added_synonyms_processed: method which takes a synonym of {synonym_to_add} and process it
    '''
    def create_synonyms (synonyms_reader, set_token, processed_set_token, synonym_to_add) :
        '''
        a create_synonyms to give to create_ngram.create_ngram_framework
        create a list of synonyms

        synonyms_reader: iterator which return at each iteration a tuple (synonym to a token of word_reader, its processed format, the token)
        set_token: set of the tokens considered as the vocabulary
        processed_set_token: set of the processed version of {set_token}
        synonym_to_add: dict of additional synonyms to add to the synonym list (format {synonym: main token})
        '''
        synonyms = []
        ignored_synonyms = []
        for main, processed_main , synonym in synonyms_reader :
            if synonym in set_token :
                problems, main, processed_main , synonym = get_problems(main, processed_main , synonym)
                #if there is no problems, add the synonym to the current list
                if not problems :
                    synonyms += [( main, processed_main , synonym)]
                else :
                    ignored_synonyms.append((main, processed_main , synonym, problems))

        #add the synonyms from synonym_to_add
        for from_word, to_word in synonym_to_add.items() :
            from_word_processed = added_synonyms_processed(from_word)
            synonyms.append((from_word, from_word_processed, to_word))

        return synonyms, ignored_synonyms, []

    return create_synonyms

