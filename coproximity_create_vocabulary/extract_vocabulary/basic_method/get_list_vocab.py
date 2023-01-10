'''
Transform the expected result of create_ngram into a more useful format for the ngram extraction.
Get the processed synonyms and processed ngrams to the ngrams they represent for every ngram in the vocabulary, filter out ngrams which are too big, 
group the remainder by their numbers of words, sort it in descending order.  
'''
import json, pickle
from coproximity_create_vocabulary.extract_vocabulary.basic_method.util_vocab import hyphen_in_1word

def get_list_vocab(main_dict_vocab, max_ngram, multiple_synonym_file=None) :
    '''
    Transform the expected result of create_ngram into a more usefull format for the ngram extraction: 
    {number of word of the ngram : {processed synonym or ngram whose number of word is the index of the dict : ngram it represents}}
    We filter out all the ngrams whose processed synonym or ngram has more than {max_ngram} words
    
    if a {multiple_synonym_file} is given also add the synonyms linking to multiple ngrams, their formats would be :
    {number of word of the ngram : {
        processed synonym or ngram whose number of word is the index of the dict : 
        list of tuple (ngram it represents, word2vec representation to the ngram (with wikipedia, this means the fastext mean of their Wikipedia article))}
    }

    main_dict_vocab: main vocabulary file, json contains a dict :
    {'token to detect': 
        [
            [list of the processed words of the token], 
            expression the token represents, if the tokens represents itself, this is an empty string, 
            number of word of the token,
        ]
    }
    max_ngram: max number of word for a ngram to be kept
    multiple_synonym_file: file to handle the multiple synonyms, pkl contains a dict :
    {'token to detect': 
        [
            [list of the processed words of the token], 
            [lists of list [main word, its vector representation]], 
            number of word of the token,
        ]
    }  
    '''
    # load the ngrams
    with open(main_dict_vocab) as f :
        list_ngrams = json.load(f)     
    #filter out too big ngrams
    list_ngrams = [
        #hyphen_in_1word sets the words separated by a hyphen as 1 word 
        ( tuple(hyphen_in_1word([word for word in processed_words if word])), syn if syn else expression_full_string )
        for expression_full_string,(processed_words,syn , count_word) in list_ngrams.items()
        if count_word <= max_ngram
    ]
    if multiple_synonym_file :
        with open(multiple_synonym_file, 'rb') as f :
            list_ngrams += [
                ( tuple(hyphen_in_1word([word for word in processed_words if word])), syn if syn else expression_full_string )
                for expression_full_string,(processed_words,syn , count_word) in pickle.load(f).items()
                if count_word <= max_ngram
            ]

    # group the ngrams by their number of word 
    split_list_ngrams = {}
    for processed_words , main_ngram in list_ngrams :
        igram = len(processed_words)
        if not igram in split_list_ngrams :
            split_list_ngrams[igram] = {}
        split_list_ngrams[igram][processed_words] = main_ngram
    split_list_ngrams = list(sorted(split_list_ngrams.items() , key = lambda x : x[0] , reverse = True ))

    return split_list_ngrams