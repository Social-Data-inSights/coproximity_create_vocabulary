'''
get the methods to use in create_ngram.py to extract the vocabulary and the synonyms from the most viewed wikipedia pages and their redirections
'''

import os, csv, json, re, time, string, fasttext, pickle, bz2
import fasttext.util
from typing import  List, Dict, Callable
from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.util_wiki import unwikititle, rewikititle
from coproximity_create_vocabulary.extract_vocabulary.basic_method.base_create_vocab_factory import (
    create_preprocess_list_words_factory, preprocess_synonyms_factory, create_vocabulary_factory, create_synonyms_factory
)
from coproximity_create_vocabulary.extract_vocabulary.basic_method.util_vocab import delete_accent_on_first_if_upper

from coproximity_create_vocabulary.download_wikipedia.create_wikipedia_plain.split_articles_to_csv import split_articles_to_csv


print_progress_info = [
    ['preprocess', False],
    ['preprocess synonyms', True],
    ['preprocess words', True],
    ['create vocabulary', False],
    ['create synonyms', False],
    ['simplify main_dict_vocab', False],
    ['post process', False],
]

#delete the desambiuousity part of the homonym and replace the '_' by spaces
simple_clean_title=lambda x : re.sub( '\\(.*\\)$' , '' , x.replace('_',' ')).strip(' ')

def split_first_word (s, apply_rewikititle=True) :
    '''
    split the article s between its first word and the rest of the words.
    if {apply_rewikititle} is True, cast the first letter of the result as uppercase
    '''
    s = simple_clean_title(s)
    idx_space , idx_apos = s.find(' ') , s.find("'")
    if idx_space > idx_apos and idx_apos > -1 or idx_space == -1 :
        res = "'".join(s.split("'")[1:])
        first = s.split("'")[0]
    else :
        res= ' '.join(s.split(' ')[1:])
        first = s.split(' ')[0]

    res = res.strip()
    if apply_rewikititle :
        return first , res[0].upper() + res[1:] if res else res
    else :
        return first , res

def test_duplicate (s, duplicate_stop_words, article_set, apply_rewikititle=True) :
    #test if the expression {s} is a duplicate (see get_args.py) if {apply_rewikititle} is True, cast the first letter of the result of split_first_word as uppercase
    first , remainder = split_first_word (s, apply_rewikititle)
    return remainder and first.lower() in duplicate_stop_words and remainder in article_set



def factory_create_title_wiki (stop_words , duplicate_stop_words, 
    processed_list_select, processed_method_list, preprocessed_apply_rewikititle_on_lem_list,
    processed_method, synonym_to_ignore,whole_folder, n_best_taken, vocab_folder, 
    plain_article_title_reader, processed_article_file : str, plain_synonyms_reader , processed_syn_file : str ,
    fasttext_file, fasttext_model, use_id_to_title = False,
    func_get_text_from_title_factory : Callable = None,
    overwrite = False, apply_rewikititle_on_lem=True,
    is_printing_progress: bool = False,
    vocab_additional_filter = [], synonym_additional_filter = []) :
    """
    Create the method to use in basic_method.create_ngram.py to create the vocabulary based on the titles of wikipedia pages and its synonyms based on their redirections.

    stop_words          : ngrams which should not appear in the vocabulary
    duplicate_stop_words: set of words considered as determinant in the title. If a title is "{determinant} {another title}", we transform the original title into this other title

    processed_list_select: For the preprocessed part, name of the processed results
    processed_method_list: list of methods to use in the preprocessed part
    preprocessed_apply_rewikititle_on_lem_list: list of boolean of the preprocessed part, if true make sure that the first letter of each token is upper case

    processed_method    : methods that takes a string and return its processed version
        (in the main methods this means lemmatized (and maybe cast as lower case and without accent))
    synonym_to_ignore   : List of synonym not to keep
    whole_folder        : parent folder of the current vocabulary folder. Use to get the id2title TODO replace this by id2title_file
    n_best_taken        : Number of word to keep in the vocabulary  
    vocab_folder        : path to the folder where the results will be saved
    
    plain_article_title_reader  : iterator that return for each iteration a title, and its associated score
    processed_article_file : path in which was/will be saved the processed tokens of {plain_article_title_reader}. Is used in create_vocabulary_wiki
    plain_synonyms_reader      : iterator which return at each iteration a tuple (synonym to a title of plain_article_title_reader, the title)
    processed_syn_file        : path in which was/will be saved the processed synonyms of {plain_synonyms_reader}. Is used in create_synonyms
    
    fasttext_file       : folder in which to save the fasttext model
    fasttext_model      : path to a pretrained fasttext model
    
    use_id_to_title     : if true consider that the wikipedia title csv is made of the wikipedia id and give a id2title_file to create_processed_title
    
    func_get_text_from_title_factory: method taking no argument and returning a method that takes a token and return an associated text.
        Typically this used take a wikipedia title and return the content of its article.
        It is used to create the wor2vec for the main articles which have synonyms linking to multiple main article. They will be used to chose
            which main article will such synonyms will be replaced by.
        (this a method of a method so that we can load things but don't need to keep it in memory during the pipeline) 

    overwrite           : try to overwrite the processed files (but reuse the processed elements if they are shared by the old and new files)
    apply_rewikititle_on_lem: if true make sure that the first letter of each token is upper case

    is_printing_progress: if True print the progress of the vocabulary creation, in a stereotyped behavior. Used in electron front to get the progress of the process.
    
    vocab_additional_filter: function which checks additional problems for the vocabulary selection 
        takes the title, the clean title, the processed title and the current vocabulary and return the list of tuple
        (boolean if the problem happened, a potential problem)
    synonym_additional_filter: function which checks additional problems for the synonyms selection
        takes a synonym, its processed version, the vocabulary element it is linked to, the set of the current synonyms and return the list of tuple
        (boolean if the problem happened, a potential problem)
    """
    #lematize the wiki title
    if apply_rewikititle_on_lem:
        wiki_processed_method = lambda x : rewikititle(processed_method(x))
    else :
        wiki_processed_method = processed_method
    
    def preprocess_wiki () :
        #check that the synonyms with processed token is created and if not creates it
        def preprocess_synonyms_wiki (main, synonym, already_processed):
            main = main.replace('_',' ')
            synonym = synonym.replace('_',' ')
            if main in already_processed :
                lem_main_list = already_processed[main]
            else :
                lem_main_list = processed_method_list(main)
                lem_main_list = tuple(
                    rewikititle(lem_main) if use_rewikititle else lem_main
                    for use_rewikititle, lem_main in zip(preprocessed_apply_rewikititle_on_lem_list, lem_main_list)
                )


            return (main, *lem_main_list , synonym), True

        preprocess_synonyms_factory(preprocess_synonyms_wiki, ('syn_from', *processed_list_select, 'syn_to'))\
            (plain_synonyms_reader , processed_syn_file, overwrite, is_printing_progress)
        
        
        #create the csv with the processed version in it
        
        #get the set of all titles while deleting homonyms
        article_set = { simple_clean_title(row[0].replace('_', ' ')) for row in plain_article_title_reader  }

        def preprocess_vocabulary_wiki (title, count, already_processed): 
            title = title.replace('_', ' ')
            if title in already_processed :
                clean_title, lem_main_list = already_processed[title]
                return (title, clean_title, *lem_main_list , count), True
            else :
                #'_' -> ' ' and delete homonym
                clean_title = simple_clean_title(title)
                #apply the processed_method
                lem_main_list = processed_method_list(clean_title)
                lem_main_list = tuple(
                    rewikititle(lem_main) if use_rewikititle else lem_main
                    for use_rewikititle, lem_main in zip(preprocessed_apply_rewikititle_on_lem_list, lem_main_list)
                )
                #delete the duplicate if the title is one
                if test_duplicate(title, duplicate_stop_words, article_set) or any(test_duplicate(lem_title, duplicate_stop_words, article_set) for lem_title in lem_main_list) :
                    clean_title = split_first_word(clean_title)[1]
                    lem_main_list = tuple(
                        split_first_word(lem_title, preprocessed_rewikititle_on_lem)[1] 
                        for lem_title, preprocessed_rewikititle_on_lem in zip(lem_main_list, preprocessed_apply_rewikititle_on_lem_list)
                    )

                if clean_title :
                    return (title, clean_title, *lem_main_list , count), True
            return None , False    

        id2title_file = whole_folder + 'meta/id2title.json' if use_id_to_title else None
        create_preprocess_list_words_factory (preprocess_vocabulary_wiki, ('main', 'clean_main', *processed_list_select, 'count'))\
            (plain_article_title_reader , id2title_file, processed_article_file, overwrite, is_printing_progress,)

    def create_vocabulary_wiki (word_reader, global_synonyms, word_to_add) :
        '''
        Methods that takes in the content of word_reader and return a set of ngrams (to consider our vocabulary), a dict of those ngrams
        to their processed versions, and the titles that were openly discarded (ie title considered but rejected).

        word_reader: iterator that return for each iteration a token, to possibly add to the vocabulary, its clean format, its processed format and its associated score
        global_synonyms: dict {synonym: main token of word_reader} for all synonym given in the {synonyms_reader} of create_ngram.create_ngram_framework
        word_to_add: list of additional tokens to add to the vocabulary
        '''
        #used to count the number of article we added
        count_nb_title = 0
        #set of all added article in a processed form
        set_processed_articles = set()
        #function to give to the create_vocabulary_factory
        def get_problems_and_ask_if_stopping (title, clean_title, processed_title, set_articles) :
            nonlocal count_nb_title
            is_stopping = False
            simplified_title = clean_title.lower()
            problems = []
            additional_problems = vocab_additional_filter(title, clean_title, processed_title, set_articles) if vocab_additional_filter else []
            #a relevant title should :
            for bool_val, name_problem in [
                (simplified_title.lower() in stop_words, 'stop word') , #not be a stop word
                (simplified_title in string.punctuation, 'ponctuation') , #not be only punctuation
                (clean_title in set_articles, 'duplicate/homonym') , #once taken out the duplicate and homonym , the title was not already added
                (clean_title in set_processed_articles or processed_title in set_processed_articles, 'is_processed_in_set_articles'), #title is not the processed token of an already added title
                ( len(simplified_title) == 1, 'size=1') ,#not be of size 1 (includes digits, punctuation and 1-letter words)
                (bool(re.findall('Saison [0-9]+ d', title)), 'Saison'),  #delete all the "Saison X" pages
                (title in global_synonyms and global_synonyms[title].intersection(set_articles), 'global_synonyms'), #title is a synonym of an already added title
                (processed_title.lower() in stop_words, 'processed stop words'), #the processed version should not be a stop word
            ] + additional_problems:
                if bool_val :
                    problems.append(name_problem)

            #this title is to be added
            if not problems :
                set_processed_articles.add(processed_title)
                count_nb_title += 1

                if not n_best_taken is None and count_nb_title >= n_best_taken :
                    is_stopping = True

            return problems, title, clean_title, processed_title, is_stopping

        set_articles, processed_dict, to_write_list = \
            create_vocabulary_factory(get_problems_and_ask_if_stopping, wiki_processed_method)(word_reader, global_synonyms, word_to_add)
        
        #For each title of the vocabulary, associate to this title with the first letter in lower case its processed title 
        for word, lem_word in list(processed_dict.items()) :
            processed_dict[unwikititle(word)] = lem_word


        return set_articles, processed_dict, to_write_list

    def create_synonyms (synonyms_reader, set_articles, processed_set_articles, synonym_to_add) :
        '''
        Take the content of synonyms_reader and return a curated list of tuple (the synonyms, the processed synonyms, the ngrams from the vocabulary they
        are synonyms of) and a list of the rejected synonyms

        synonyms_reader: iterator which return at each iteration a tuple (synonym to a token of word_reader, its processed format, the token)
        set_token: set of the tokens considered as the vocabulary
        processed_set_token: set of the processed version of {set_token}
        synonym_to_add: dict of additional synonyms to add to the synonym list (format {synonym: main token})
        '''
        def test_synonym_duplicate (s) :
            #if a synonym is a duplicate of an expression not in the best tiles we have, return the original otherwise just return the synonym without any change
            first , remainder = split_first_word (s)
            return remainder if  remainder and first.lower() in duplicate_stop_words and not remainder in set_articles else s

        is_homonym = re.compile(' \\(.*\\)$')
        #function to give to the create_synonyms_factory
        def get_problems(main, lem_main , synonym):
            #a synonym is added if :
            additional_problems = synonym_additional_filter(main, lem_main , synonym, set_articles) if synonym_additional_filter else []
            problems = [
                problem for  val_bool, problem in [
                    (is_homonym.search(main), 'is homonym') , #it is not an homonym
                    (test_duplicate(main, duplicate_stop_words, set_articles), 'is duplicate'), #if the synonym is not a duplicate whose original was deemed relevant
                    (main in set_articles , 'is a main article' ), #the synonym is not already a title
                    (lem_main in processed_set_articles, 'processed token is a main article'), #the processed synonym is not already a processed title
                    (main.lower() in stop_words, 'stop word'), #the synonym is a stop word
                    (lem_main.lower() in stop_words, 'processed token stop word'), #the processed synonym is a stop word
                    ((main, synonym) in synonym_to_ignore, 'manually set as bad' ), #not the synonym in the synonym to ignore
                    ((lem_main, synonym) in synonym_to_ignore, 'processed token manually set as bad' ), #not the processed synonym in the synonym to ignore
                    (re.fullmatch('[A-Z]\'', main), '[A-Z]\''),  # delete all the m' and d'
                    ( len(main) == 1, 'size == 1' ), #not be of size 1 (includes digits, punctuation and 1-letter words)
                    (not lem_main, 'processed main is empty'), #the processed version should be something
                ] + additional_problems
                if val_bool 
            ] 
            if problems:
                return problems, main, lem_main , synonym

            #test if the main is a duplicate and delete the duplicate if it is
            duplicate_main , duplicate_lem_main =  test_synonym_duplicate (main), test_synonym_duplicate(lem_main)
            problems = [
                problem for  val_bool, problem in [
                    (duplicate_main.lower() in stop_words, 'duplicate stop word'),
                    (duplicate_lem_main.lower() in stop_words, 'processed duplicate stop word'),
                ] if val_bool 
            ]
            if not problems :
                return problems, duplicate_main , duplicate_lem_main , synonym
            else :
                return problems, main, lem_main , synonym

        synonyms, ignored_synonyms, to_save = create_synonyms_factory (get_problems, wiki_processed_method)(synonyms_reader, set_articles, processed_set_articles, synonym_to_add)

        return synonyms, ignored_synonyms, to_save

    def process_all (main_dict_vocab) :
        '''
        separate all synonyms whose processed token is synonym of multiple ngrams 
        '''
        to_save = []
        for title , (lem_title , syn , count ) in main_dict_vocab.items() :
            assert (not ' '.join(lem_title).lower() in stop_words and not title.lower() in stop_words) ,(title , (lem_title , syn , count ))
        #count the number of synonyms by processed redirections
        count_same = {}
        token2title = {}
        for title , (lem_title,syn,_) in main_dict_vocab.items() :
            lt = ' '.join(lem_title)
            if not lt in count_same :
                count_same [lt] = set()
            count_same[lt].add(syn if syn else title)
            if not lt in token2title :
                token2title[lt] = set()
            token2title[lt].add(title)


        #separate redirections which redirect to multiple articles 
        multiple_synonyms = []
        for new_title , set_title in count_same.items() :

            if new_title in main_dict_vocab and not main_dict_vocab[new_title][1] :
                main_dict_vocab[new_title] = ( new_title.split(' '), '' , new_title.count(' ') + 1)  
            elif len(set_title) == 1 :
                title = list(set_title)[0]
                assert not new_title in stop_words and not unwikititle(new_title) in stop_words , (new_title , title)
                main_dict_vocab[new_title] = ( new_title.split(' '), title , new_title.count(' ') + 1)  
            else :
                multiple_synonyms.append((new_title, list(set_title)))
                multiple_synonyms.append((unwikititle(new_title), list(set_title)))
                for tok_title in token2title[new_title] :
                    if not tok_title in main_dict_vocab or  main_dict_vocab[tok_title][1] :
                        del main_dict_vocab[tok_title]

        to_save.append(('multiple_synonyms.json', multiple_synonyms))

        #delete empty words
        main_dict_vocab = { title : ([w for w in lem_title if w],syn,count) for title , (lem_title,syn,count) in main_dict_vocab.items() }
        # add the redirections with lowercase on the first letter
        has_double = []
        for title , (lem_title,syn,count) in list(main_dict_vocab.items()) :
            unwiki_title = unwikititle(title)
            lem_title = [unwikititle(lem_title[0])] + lem_title[1:]
            syn = syn if syn else title

            assert not unwiki_title in stop_words 
            if not unwiki_title in main_dict_vocab :
                main_dict_vocab[unwiki_title] = (lem_title,syn,count)
            elif title[0].isupper():
                has_double.append([unwiki_title , (lem_title,syn,count) , main_dict_vocab[unwiki_title]])
        to_save.append(('has_double.json', has_double))

        #Add a synonym for any expression with a word beginning by an uppercase with an accent on it: add the expression without accents if it creates no collision with the rest of the corpus
        set_lem_title = {tuple(lem_title) for lem_title, _, _ in main_dict_vocab.values()}
        #nafiu = not accent first if uppercase
        to_add_nafiu = {}
        for title , (lem_title,syn,count) in list(main_dict_vocab.items()) :
            title_nafiu = ' '.join(delete_accent_on_first_if_upper(word) for word in title.split(' '))
            lem_title_naifu = tuple(delete_accent_on_first_if_upper(word) for word in lem_title)
            if not title_nafiu in main_dict_vocab and not lem_title_naifu in set_lem_title :
                to_add_nafiu[title_nafiu] = (lem_title_naifu,syn if syn else title,count)
        main_dict_vocab.update(to_add_nafiu)

        return main_dict_vocab, to_save

    def post_process_create_multi_synonym_vecs () :
        '''
        after all the synonyms and title are done, create load a fasttext model and get the vector of the titles which share a common synonym
        '''

        if not func_get_text_from_title_factory :
            print('must abort post_process_create_multi_synonym_vecs: no func_get_text_from_title_factory')
            return

        #load fasttext
        if os.path.exists(fasttext_file) :
            print('fasttext already downloaded')
        else :
            #download the fastext model
            current_folder = os.getcwd()
            os.chdir(os.path.dirname(fasttext_file))
            fasttext.util.download_model(fasttext_model, if_exists='ignore')
            os.chdir(current_folder)
        model = fasttext.load_model(fasttext_file)

        with open(vocab_folder + 'multiple_synonyms.json') as f :
            multiples_synonyms = json.load(f)

        #set of the articles which share a synonym with other articles.
        main_articles = { main for _, mains in multiples_synonyms for main in mains }


        #get the articles of the titles whose share synonyms with others
        func_get_title = func_get_text_from_title_factory()
        plains = {}
        for art_name in main_articles :
            plain = func_get_title(art_name)
            if plain :
                plains[art_name] = plain

        #get the fastext mean over each article
        multiple_vecs = {art_name: model.get_sentence_vector(plain.replace('\n', ' ')) for art_name, plain in plains.items()}
        multiple_vecs = { syn :(tuple(syn.split(' ')), [(main, multiple_vecs[main]) for main in mains if main in multiple_vecs], syn.count(' ') + 1) for syn, mains in multiples_synonyms}
        multiple_vecs = { syn : (lem_syn, mains, count) for syn, (lem_syn, mains, count) in multiple_vecs.items() if mains }

        with open(vocab_folder+ 'multiple_vecs.pkl', 'wb') as f :
            pickle.dump(multiple_vecs, f)

    return preprocess_wiki, create_vocabulary_wiki, create_synonyms, process_all, post_process_create_multi_synonym_vecs

def plain_get_text_from_title_factory(title2id_file, token2text_file) :
    '''
    Method used in the "with data project mains" to get the text for Wikipedia titles.
    Given a path to a json containing {Wikipedia id (or title): text} ,
    create a method that takes in a title and return the text of its article

    title2id_file: if some is given, link to a json of a dict {Wikipedia title: Wikipedia id}, and we consider that {token2text_file} contains
            Wikipedia ids and we use this to get the translate from  id to title
        if none is given, we consider that {token2text_file} contains Wikipedia titles
    '''
    if title2id_file :
        with open(title2id_file) as f :
            title2id = json.load(f) 
        title2id = { title.replace('_', ' '): id_ for title, id_ in title2id.items() }
    else :
        title2id = None

    with open(token2text_file) as f :
        plains = json.load(f)
    def create_translate_title2text_id(title) :
        return plains.get(title2id.get(title)) if title2id else plains.get(title)
    return create_translate_title2text_id

def get_dict_search_index(index_filename):
    data_length = start_byte = 0
    curr_res, res = set(), {}
    
    with bz2.open(index_filename) as f_in  :
        for line in f_in :
            curr_start_byte, _, *title = line.decode('utf8').strip().split(':')
            title = ':'.join(title)
            curr_start_byte = int(curr_start_byte)
            if curr_start_byte != start_byte :
                if curr_res :
                    res.update({title: (start_byte, curr_start_byte - start_byte) for title in curr_res})
                curr_res = set()
                start_byte = curr_start_byte
                
            curr_res.add(title)
            
    if curr_res :
        res.update({title: (start_byte, curr_start_byte - start_byte) for title in curr_res})
    return res
def get_title_from_dump_factory(index_filename, wiki_filename, temp_filename) :
    dict_search_index = get_dict_search_index(index_filename)

    def get_title_from_dump(title) :
        if not title in dict_search_index:
            return
        
        start_byte, data_length = dict_search_index[title]

        with open(wiki_filename, 'rb') as wiki_file:
            wiki_file.seek(start_byte)
            data = wiki_file.read(data_length)

        with open(temp_filename, 'wb') as temp_file:
            temp_file.write(data)

        return split_articles_to_csv (
            whole_dir = '',
            from_xml_bz2 = temp_filename,
            dump_save_to = None ,
            threshold_skip_little = 0,
            what_to_do_result = 'return_dict_title',
            get_only_ids = None,
            get_only_title = {title},
            is_printing=False,
        ).get(title)
    return get_title_from_dump

def create_smaller_multi_synonyms_text_file (vocab_folder, save_folder, func_get_text_from_title_factory) :
    '''
    Given a typical Wikipedia Vocabulary folder (created with main_wikititle.py for example) {vocab_folder}, take all the synonyms which redirect to multiple tokens. 
        And create for those tokens a dictionary : {token: text representation} (ex: {article title: article content })

    vocab_folder: vocabulary folder from which to extract the list of tokesn from which to save the text
    save_folder: folder in which to save the result
    func_get_text_from_title_factory: method taking no argument and returning a method that takes a token and return an associated text.
        Typically this used take a wikipedia title and return the content of its article.
        It is used to create the wor2vec for the main articles which have synonyms linking to multiple main article. They will be used to chose
            which main article will such synonyms will be replaced by.
        (this a method of a method so that we can load things but don't need to keep it in memory during the pipeline) 

    '''
    with open(vocab_folder + 'multiple_synonyms.json') as f :
        multiples_synonyms = json.load(f)

    #set of the articles which share a synonym with other articles.
    main_articles = { main for _, mains in multiples_synonyms for main in mains }


    #get the articles of the titles whose share synonyms with others
    func_get_title = func_get_text_from_title_factory()
    plains = {}
    for art_name in main_articles :
        plain = func_get_title(art_name)
        if plain :
            plains[art_name] = plain

    with open(save_folder + 'multi_synonyms_text.json', 'w', encoding='utf8') as f :
        json.dump(plains, f, indent=2)
