'''
Basic test for the ngrams creator
'''
from create_ngram_wordpiece import create_ngram_wordpiece
import os, json

from coproximity_create_vocabulary.data_conf import base_vocab_folder

def test(itest = None) :
    #itest : test on test number i
    min_likelihood =  0.4
    max_nb_ngrams=10
    min_freq = 5
    save_folder = base_vocab_folder + '/wikipedia/whole/wordpiece_based/test/'
    if not os.path.exists(save_folder) :
        os.mkdir(save_folder)

    list_test = [
        [['a' , 'b' , 'c']] * 10,
        [[str(i) , 'a' , 'b' , 'c' , str(i+20)] for i in range(10) ],
        [['1', 'a' , 'b' , 'c' ,'11']] * 10 + [['2', 'a' , 'b' , 'c' ,'12']] * 10,
        [['a', 'b','a', 'b','a', 'b',] for i in range(10) ],
        [['a','a', 'b','a', 'a','a', 'b', 'a']]+[['a', 'b',] for i in range(9) ],
        [['a', 'b','a', 'a', 'b',]]+[['a', 'b',] for i in range(9) ],
        [['a', 'b','a', str(i), 'a', 'b',] for i in range(10) ],
        [[str(i),'a', 'b',str(i+10),'a', 'b',str(i+20),'a', 'b',] for i in range(10) ],
        ['a b a c a b a c'.split(' ') for i in range(10) ],
    ]

    for i , to_save in enumerate(list_test) :
        save_file = save_folder + 'save_%d.json'%i
        if not os.path.exists(save_file) :
            with open(save_file , 'w') as f :
                json.dump({i : ' '.join(x) for i,x in enumerate (to_save)} , f)

    if itest is None or itest == 0 :
        #[['a' , 'b' , 'c']] * 10,
        tokenized,count, count_tuple, list_ngrams = create_ngram_wordpiece(
            save_folder, save_folder + 'save_0.json' ,max_nb_ngrams , min_likelihood, min_freq,'likelihood_square' , 'test', save_mid_results=False, is_testing = True) 
        assert tokenized == [[['a b c']] for i in range(10)] , tokenized
        assert count == {'a b c' : 10}, count
        assert count_tuple == {} , count_tuple

    if itest is None or itest == 1 :
        #[[str(i) , 'a' , 'b' , 'c' , str(i+20)] for i in range(10) ],
        tokenized,count, count_tuple, list_ngrams = create_ngram_wordpiece(
            save_folder, save_folder + 'save_1.json' ,max_nb_ngrams , min_likelihood, min_freq,'likelihood_square' , 'test', save_mid_results=False, is_testing = True)
        assert tokenized == [[[str(i) ,'a b c', str(i+20)]] for i in range(10) ]  , tokenized
        assert count == dict([('a b c' , 10)] + [ (str(i+to_add) , 1) for i in range(10) for to_add in (0,20)] ), count
        assert count_tuple == dict([ x for i in range(10) for x in [((str(i) ,'a b c') , 1 ) , (('a b c', str(i+20)) , 1 )] ]) , count_tuple

    if itest is None or itest == 2 :
        #[['1', 'a' , 'b' , 'c' ,'11']] * 10 + [['2', 'a' , 'b' , 'c' ,'12']] * 10,
        tokenized,count, count_tuple, list_ngrams = create_ngram_wordpiece(
            save_folder, save_folder + 'save_2.json' ,max_nb_ngrams , min_likelihood, min_freq,'likelihood_square' , 'test', save_mid_results=False, is_testing = True)
        assert tokenized == [[['1 a b c 11']]] * 10 + [[['2 a b c 12']]] * 10 , tokenized
        assert count == {'1 a b c 11' : 10, '2 a b c 12' : 10, }, count
        assert count_tuple == {} , count_tuple

    if itest is None or itest == 3 :
        #[['a', 'b','a', 'b','a', 'b',] for i in range(10) ],
        tokenized,count, count_tuple, list_ngrams = create_ngram_wordpiece(
            save_folder, save_folder + 'save_3.json' ,max_nb_ngrams , min_likelihood, min_freq,'likelihood_square' , 'test', save_mid_results=False, is_testing = True)
        assert tokenized == [[['a b',]*3]]*10 , tokenized
        assert count == {'a b' : 30 }, count
        assert count_tuple == {} , count_tuple
        
    if itest is None or itest == 4 :
        #[['a','a', 'b','a', 'a','a', 'b', 'a']]+[['a', 'b',] for i in range(9) ],
        tokenized,count, count_tuple, list_ngrams = create_ngram_wordpiece(
            save_folder, save_folder + 'save_4.json' ,max_nb_ngrams , min_likelihood, min_freq,'likelihood_square' , 'test', save_mid_results=False, is_testing = True)
        assert count == {'a b' : 11 , 'a' : 4}, count
        assert count_tuple == {('a b','a') : 2 , ('a','a b') : 2 } , count_tuple
        assert tokenized == [[['a', 'a b','a', 'a','a b','a']]]+[[['a b',]] for i in range(9) ] , tokenized
        
        
    if itest is None or itest == 5 :
        #[['a', 'b','a', 'a', 'b',]]+[['a', 'b',] for i in range(9) ],
        tokenized,count, count_tuple, list_ngrams = create_ngram_wordpiece(
            save_folder, save_folder + 'save_5.json' ,max_nb_ngrams , min_likelihood, min_freq,'likelihood_square' , 'test', save_mid_results=False, is_testing = True)
        assert tokenized == [[['a b','a', 'a b',]]]+[[['a b',]] for i in range(9) ] , tokenized
        assert count == {'a b' : 11 , 'a' : 1}, count
        assert count_tuple == {('a b','a') : 1 , ('a','a b') : 1 } , count_tuple
        
        
    if itest is None or itest == 6 :
        #[['a', 'b','a', str(i), 'a', 'b',] for i in range(10) ],
        tokenized,count, count_tuple, list_ngrams = create_ngram_wordpiece(
            save_folder, save_folder + 'save_6.json' ,max_nb_ngrams , min_likelihood, min_freq,'likelihood_square' , 'test', save_mid_results=False, is_testing = True)
        assert tokenized == [[['a b a', str(i) , 'a b']] for i in range(10) ]  , tokenized
        assert count == dict([('a b a' , 10), ('a b' , 10)] + [ (str(i) , 1) for i in range(10) ] ), count
        assert count_tuple == dict([ x for i in range(10) for x in [((str(i) ,'a b') , 1 ) , (('a b a', str(i)) , 1) ] ]) , count_tuple
        
    if itest is None or itest == 7 :
        #[[str(i),'a', 'b',str(i+10),'a', 'b',str(i+20),'a', 'b',] for i in range(10) ],
        tokenized,count, count_tuple, list_ngrams = create_ngram_wordpiece(
            save_folder, save_folder + 'save_7.json' ,max_nb_ngrams , min_likelihood, min_freq,'likelihood_square' , 'test', save_mid_results=False, is_testing = True)
        assert tokenized == [[[str(i),'a b',str(i+10),'a b',str(i+20),'a b',]] for i in range(10) ]  , tokenized
        assert count == dict([('a b' , 30)] + [ (str(i+to_add) , 1) for i in range(10) for to_add in (0,10,20) ] ), count
        assert count_tuple == dict([ x for i in range(10) for x in [
            ((str(i) ,'a b') , 1 ) , ((str(i+10) ,'a b') , 1 ) ,((str(i+20) ,'a b') , 1 ) , (('a b',str(i+10)) , 1 ) ,(('a b',str(i+20)) , 1 ) ,
        ] ]) , list(sorted(count_tuple.items()))


    if itest is None or itest == 8 :
        #['a b a c a b a c'.split(' ') for i in range(10) ],
        tokenized,count, count_tuple, list_ngrams = create_ngram_wordpiece(
            save_folder, save_folder + 'save_8.json' ,max_nb_ngrams , min_likelihood, min_freq,'likelihood_square' , 'test', save_mid_results=False, is_testing = True)
        assert tokenized == [[['a b a c', 'a b a c']]] *10 , tokenized
        assert count == {'a b a c' : 20 ,}, count
        assert count_tuple == {} , count_tuple



    print('passed all')

test()