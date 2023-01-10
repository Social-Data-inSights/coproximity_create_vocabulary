'''
TODOC, not urgent because dead end
'''

import os, json, re, numpy as np, pickle, time, numba as nb
from collections import Counter
from nltk import ngrams

from coproximity_create_vocabulary.data_conf import base_vocab_folder

'''@nb.jit('float64(int64,int64[:])', nopython=True)
def numba_get_max_likelihood_square_func (freq_expr, count) :
    return (freq_expr**2) / (count[0] * count[1])'''

@nb.jit('float64(int64,int64,int64)', nopython=True)
def numba_get_max_likelihood_square_func (freq_expr,count_first , count_second) :
    return (freq_expr**2) / (count_first * count_second)

def get_max_likelihood_square_func (count, word, freq_expr , N) :
    first, second = word
    try :
        return (freq_expr**2) / (count[first] * count[second])
    except ZeroDivisionError :
        return 0

def get_max_likelihood_func (count, word, freq_expr, N ) :
    first, second = word
    try :
        return (freq_expr) / (count[first] * count[second])
    except ZeroDivisionError :
        return 0

def ttest (count, word, freq_expr, N ) :
    first, second = word
    proba_expr = freq_expr/N
    return (proba_expr - (count[first] * count[second] / (N**2))) / np.sqrt(proba_expr*(1-proba_expr)/N)


dict_func = {
    'likelihood_square' : get_max_likelihood_square_func,
    'likelihood' : get_max_likelihood_func,
    'ttest' : ttest,

}

def merge_sorted_list (A,B, key = lambda x : x) :
    if not A :
        return B 
    if not B :
        return A
    a = A.pop(0)
    b = B.pop(0)
    a_score , b_score = key (a) , key(b)
    res = []
    while True :
        if a_score > b_score :
            res.append(a)
            if A :
                a = A.pop(0)
                a_score = key (a)
            else :
                res.append(b)
                res.extend(B)
                return res
        else :
            res.append(b)
            if B :
                b = B.pop(0)
                b_score = key (b)
            else :
                res.append(a)
                res.extend(A)
                return res

def create_ngram_wordpiece(save_folder, plain_file ,max_nb_ngrams , min_score , min_freq, func_name, dataset, save_mid_results = False, is_testing = False ) :
    save_preprocess_file = save_folder + f'preprocess_{dataset}.pkl'
    save_file = f'list_ngrams_{func_name}_{dataset}_max_nb_{max_nb_ngrams}_min_score_{min_score}_min_freq_{min_freq}.json'
    print(save_file, save_preprocess_file)

    #min_freq for the preprocess
    min_min_freq = 5
    assert min_freq >= min_min_freq, 'min_freq must be >5'

    if os.path.exists(save_folder+save_file) and not is_testing :
        print(f'{save_folder+save_file} already done')
        return

    if not os.path.exists(save_preprocess_file) or not save_mid_results :
        if not os.path.exists(save_folder)  :
            os.mkdir(save_folder)
        print(save_folder)
        print('load tokenized', )
        with open(plain_file, encoding ='utf8') as f :
            tokenized = np.array(list(json.load(f).values()), dtype=object)

        print('clean tokenized', )
        for i_art , art in enumerate(tokenized) :
            if not i_art % 1000 :
                print(i_art,'       ', end='\r')
            tokenized[i_art] = re.sub('[ ,();:’\']+' , ' ', re.sub('[.?!\n]+' , '\n' , art)).strip()
        print()

        print('create int2word', )
        count = Counter()
        for i_art , art in enumerate(tokenized) :
            if not i_art % 1000 :
                print(i_art,'       ', len(count), end='\r')
            for sentence in art.split('\n') :
                count.update(sentence.strip().split(' '))
        print()
        print('count', len(count))
        if not is_testing :
            count = [word for word , c in count.items() if c > min_min_freq and word]
        else :
            count = [word for word , c in count.items() if word]
        print('count', len(count))
        int2word = np.array(count, dtype=np.object)
        print('int2word', int2word.shape)
        del count
        word2int = {word : i for i , word in enumerate(int2word)}

        print('create int2word on tokenized', )
        for i_art , art in enumerate(tokenized) :
            if not i_art % 1000 :
                print(i_art,'       ', end='\r')
            tokenized[i_art] = np.array([
                np.array( [word2int.get(word, -1) for word in line.strip().split(' ') if word], dtype=np.int64)
                for line in art.split('\n') if line.strip()
            ] , dtype=object)
        print()

        print('create count', )
        count_tuple = Counter() 
        count = np.zeros( int2word.shape, dtype=np.object)
        print('toto', count.shape , int2word.shape , )
        word2art = {}
        for i_art, art in enumerate(tokenized) :
            if not i_art % 1000 :
                print(i_art,'       ', end='\r')
            for sentence in art :
                for int_word in sentence :
                    if int_word != -1 :
                        count[int_word] += 1
                count_tuple.update(ngrams(sentence , 2))
            
            for word in {word for sentence in art for word in sentence} :
                if not word in word2art :
                    word2art[word] = set()
                word2art[word].add(i_art)                

        count_tuple = Counter({(first,second) : freq for (first,second) , freq in count_tuple.items() if freq > min_min_freq and first != second and first != -1 and second != -1  })
        if save_mid_results :
            print('save preproces')
            with open (save_preprocess_file , 'wb') as f :
                for to_save in (tokenized , int2word , word2int, count_tuple , count , word2art) :
                    pickle.dump( to_save , f)   
    else :
        print('load preproces')
        with open (save_preprocess_file , 'rb') as f :
            tokenized = pickle.load(f) 
            int2word = pickle.load(f) 
            word2int = pickle.load(f) 
            count_tuple = pickle.load(f) 
            count = pickle.load(f) 
            word2art = pickle.load(f) 
    
    print('create ngrams')

    OUT = 0
    ON_FIRST = 1
    ON_SECOND = 2

    list_ngrams = []
    int2word = np.append(int2word, [''] * max_nb_ngrams)

    tt = [0] * 10
    tt_names = [''] * 10
    tt_names[:8] = ['best' , 'check', 'pre it' , 'it' , 'set_index_changed', 'filter' , 'to_add' , 'sort']
    tt_names[-1] = 'test'
    t=time.time()

    new_ngram_i = count.shape[0]
    count = np.append(count, [-1] * max_nb_ngrams)
    N_art = tokenized.shape[0]

    if min_freq > min_min_freq :
        count_tuple = Counter({(first,second) : freq for (first,second) , freq in count_tuple.items() if freq > min_freq  })

    score_func = dict_func[func_name]
    sorted_score = list(sorted([ 
        (first, second ,score_func(count, (first, second ), freq , N_art) ) 
        for (first, second ), freq in count_tuple.items() if score_func(count, (first, second ), freq , N_art) >= min_score and freq > min_freq
    ] , key = lambda x : x[2], reverse=True))

    step_print = 100
    for it in range(max_nb_ngrams) :
        if not it % step_print and it :
            print(it, 'time', sum(tt) , [(name,x ) for x , name in zip(tt, tt_names)] , '\n' , [(name,x / sum(tt)) for x , name in zip(tt, tt_names)], '\n_______________')
            tt = [0] * 10
            if not is_testing :
                count_tuple = Counter({ idx : freq for idx , freq in count_tuple.items() if freq > min_freq })
            '''with open(save_folder+save_file.replace('.json' , '_backup_%d.json'%it) , 'w', encoding='utf8') as f :
                json.dump(list_ngrams, f)
            backup_file_2_back = save_folder+save_file.replace('.json' , '_backup_%d.json'%(it - 2 * step_print))
            if os.path.exists(backup_file_2_back) :
                os.remove(backup_file_2_back)'''
            t=time.time()
        
        #test = max(count_tuple.items(), key = lambda x : x[1] )
        
        #tt[-1] , t = tt[-1] + time.time() - t , time.time()

        '''print('countcount', count[count<=min_freq], np.where(count<=min_freq), '/', count[[9785, 9786]])
        print('toto', count.shape , int2word.shape)
        print(int2word[np.where(count<=min_freq)],)'''

        #test = max(count_tuple.items(), key = lambda x : numba_get_max_likelihood_square_func(x[1] , count[list(x[0])] ) )
        #test = max(count_tuple.items(), key = lambda x : numba_get_max_likelihood_square_func(x[1] , *count[x[0]] ) )
        #test = max(count_tuple.items(), key = lambda x : numba_get_max_likelihood_square_func(x[1] , count[x[0][0]] ,count[x[0][1]] ) )
        #test = max(count_tuple.items(), key = lambda x : x[1] )
        
        #test = max(count_tuple.items(), key = lambda x : test_numba_get_max_likelihood_square_func(x ))
        #tt[-2] , t = tt[-2] + time.time() - t , time.time()

        if not sorted_score :
            print('sorted_score empty')
            break

        #(max_first, max_second) , max_freq = max(count_tuple.items(), key = lambda x : get_max_likelihood_square_func(count,*x) )
        max_first, max_second , max_score = sorted_score.pop(0)
        max_freq = count_tuple[(max_first, max_second)]
        if -1 in (max_first, max_second) :
            print(f'skip because contains a word appearing too little : {max_first}, {max_second}')
            del count_tuple[(max_first, max_second)]
            continue

        

        tt[0] , t = tt[0] + time.time() - t , time.time()
        assert max_score == score_func(count,(max_first, max_second) , max_freq , N_art)
        #print(it,(max_first, max_second),(int2word[max_first], int2word[max_second]) , max_freq , max_score ,'//',  )

        if max_score < min_score :
            print('end because likelihood too small')
            break

        more1=False
        if max_score > 1 :
            more1 = True
            print(('>>>>1',max_first, max_second) , max_freq , count[max_first] , count[max_second])

        if count_tuple[(max_first, max_second)]<= min_freq :
            del count_tuple[(max_first, max_second)]
            print('skip because not present enough')
        else :
            list_ngrams.append(
                (
                    int2word[max_first] , 
                    int2word[max_second] , 
                    max_freq , 
                    max_score
                )
            )
            tt[1] , t = tt[1] + time.time() - t , time.time()


            word2art[new_ngram_i] = set()
            new_ngram = '%s %s'%(int2word[max_first] , int2word[max_second])
            word2int[new_ngram] = new_ngram_i
            #int2word = np.append(int2word, [new_ngram])
            int2word[new_ngram_i] = new_ngram

            expected_first_score , expected_second_score = [ x - count_tuple[( max_first , max_second )] for x in count[[max_first, max_second]]]

            tt[2] , t = tt[2] + time.time() - t , time.time()

            type1 , type2 = 0,0
            new_ngram_count = 0
            for art_i in word2art[max_first] & word2art[max_second] :

                curr_art = []
                for sentence in tokenized[art_i] :
                    curr_sentence = []
                    state = OUT
                    prev = None
                    prev_is_new_ngram = False
                    #we are on the ? of the pattern "max_first max_second max_first ?",  
                    #note : I don't count the same word appearing twice as a ngram so if there is 2 new ngram following each other, we do not update the count_tuple 
                    possible_double_new_ngram = False
                    for word in sentence :

                        if state == ON_FIRST :
                            if word == max_second :

                                if not prev is None :
                                    if not possible_double_new_ngram :
                                        curr_sentence.append(prev)
                                        if prev != -1 :
                                            if (prev , max_first) in count_tuple :
                                                count_tuple[(prev , max_first)] -= 1
                                                if count_tuple[(prev , max_first)] == 0 :
                                                    del count_tuple[(prev , max_first)]
                                            count_tuple[(prev , new_ngram_i)] += 1

                                count[max_first] -= 1
                                count[max_second] -= 1
                                count_tuple[( max_first , max_second )] -= 1
                                if count_tuple[( max_first , max_second )] == 0 :
                                    del count_tuple[( max_first , max_second )]

                                curr_sentence.append(new_ngram_i)
                                word2art[new_ngram_i].add(art_i)

                                new_ngram_count += 1
                                prev_is_new_ngram =True
                                state = OUT
                                prev = None

                                possible_double_new_ngram = False
                                continue
                            else :
                                if possible_double_new_ngram :
                                    count_tuple[(new_ngram_i , max_first)] += 1
                                    possible_double_new_ngram = False 
                                if not prev is None :
                                    curr_sentence.append(prev)
                                prev = max_first
                                state = OUT

                        if state == OUT :
                            if word == max_first :
                                state = ON_FIRST
                            else :
                                if not prev is None and not prev_is_new_ngram :
                                    curr_sentence.append(prev)
                                prev = word

                            if prev_is_new_ngram :                                    
                                if word != -1 :
                                    if (max_second , word) in count_tuple :
                                        count_tuple[(max_second , word)] -= 1
                                        if count_tuple[(max_second , word)] == 0 :
                                            del count_tuple[(max_second , word)]
                                    if state == ON_FIRST :
                                        possible_double_new_ngram = True 
                                        #prev = word
                                    else :
                                        count_tuple[(new_ngram_i , word)] += 1

                                prev_is_new_ngram = False

                    if not prev is None and prev != word and not prev_is_new_ngram :
                        curr_sentence.append(prev)
                    if not prev_is_new_ngram :
                        curr_sentence.append(word)
                    if possible_double_new_ngram :
                        count_tuple[(new_ngram_i , max_first)] += 1
                    
                    try :
                        curr_art.append(np.array(curr_sentence , dtype = np.int64))
                    except TypeError :
                        print('TypeError', 'curr_sentence', curr_sentence)

                tokenized[art_i] = np.array(curr_art, dtype = np.object)

            assert (expected_first_score , expected_second_score) == (count[max_first] , count[max_second]),(
                expected_first_score , expected_second_score,count[max_first] , count[max_second])
            assert count_tuple[( max_first , max_second )] == 0, (count_tuple[( max_first , max_second )] , type1 , type2)

            #count = np.append(count, [new_ngram_count])
            count [new_ngram_i] = new_ngram_count

            tt[3] , t = tt[3] + time.time() - t , time.time()
            
            ngram_part = {max_first, max_second,new_ngram_i }
            set_index_changed = [
                (first, second) for (first, second) , freq in count_tuple.items() 
                if (first in ngram_part or second in ngram_part) and freq > min_freq
            ]
            tt[4] , t = tt[4] + time.time() - t , time.time()

            
            sorted_score = [(first , second , score) for first,second,score in sorted_score if not (first in ngram_part or second in ngram_part)]
            tt[5] , t = tt[5] + time.time() - t , time.time()
            to_add = [ (first,second, score_func(count, (first, second ), count_tuple[(first, second )] , N_art)) for first , second in set_index_changed ]
            to_add = list(sorted([ (first , second , score) for first , second , score in to_add if score >= min_score] , key = lambda x : x[2] , reverse=True))
            tt[6] , t = tt[6] + time.time() - t , time.time()
            
            sorted_score = merge_sorted_list(sorted_score,to_add , key=lambda x : x[2])
            assert all([x >= min_score for _,_,x in sorted_score])
            
            tt[7] , t = tt[7] + time.time() - t , time.time()
            new_ngram_i+=1

  
    if not is_testing :
        with open(save_folder+save_file , 'w', encoding='utf8') as f :
            json.dump(list_ngrams, f)
    else : 
        #print({int2word[word] : art for word , art in  word2art.items()})
        #print(int2word)
        tokenized = [[ [int2word[word] for word in sentence] for sentence in art] for art in tokenized]
        count = {word : c for word , c in zip(int2word, count) if word and c > 0}
        count_tuple = { (int2word[w1], int2word[w2]) : c for (w1,w2) , c in count_tuple.items() }
        return tokenized,count, count_tuple, list_ngrams



if __name__ == '__main__' :
    min_score =  0.1
    #max_nb_ngrams=int(1e6)
    max_nb_ngrams=10000
    min_freq = 10
    save_mid_results=True
    whole_folder :str = base_vocab_folder + '/wikipedia/whole/' 
    save_folder = whole_folder+'wordpiece_based/'

    '''tokenized,count, count_tuple, list_ngrams = create_ngram_wordpiece(save_folder, base_vocab_folder + '/RTS/plain_ade.json' ,max_nb_ngrams=max_nb_ngrams , min_score=0.1, 
            min_freq=min_freq , dataset='ade', save_mid_results = True, is_testing=True)

    with open(save_folder+'list_ngrams_ade_max_nb_1000000_min_score_0.1_test%d.json'%(len(os.listdir(save_folder))) , 'w' ) as f :
        json.dump(list_ngrams)

    print(0/0)'''

    for dataset, plain_file in [
         ( 'ade' ,  base_vocab_folder + '/RTS/plain_ade.json'), 
         ( 'wiki' ,  base_vocab_folder + '/wikipedia/best_avg_250.000.json'),
    ] :
        for func_name, min_score in [
            ('likelihood_square' , 0.1),
            ('likelihood' , 0.01),
            ('ttest',3.0),
        ] :
            create_ngram_wordpiece(save_folder, plain_file ,max_nb_ngrams=max_nb_ngrams , min_score=min_score, 
                min_freq=min_freq , func_name=func_name, dataset=dataset, save_mid_results = save_mid_results)

    '''for dataset , plain_file, min_score, save_mid_results in [
        ( 'ade' ,  base_vocab_folder + '/RTS/plain_ade.json', 0.95, True) , 
        ( 'ade' ,  base_vocab_folder + '/RTS/plain_ade.json', 0.9,True) , 
        ( 'ade' ,  base_vocab_folder + '/RTS/plain_ade.json', 0.1,True) , 
        ( 'wiki' ,  base_vocab_folder + '/wikipedia/best_avg_250.000.json', 0.1, True) ,
        ( 'wiki' ,  base_vocab_folder + '/wikipedia/best_avg_250.000.json', 0.01, True) ,
    ] :
        create_ngram_wordpiece(save_folder, plain_file ,max_nb_ngrams=max_nb_ngrams , min_score=min_score, 
            min_freq=min_freq , dataset=dataset, save_mid_results = save_mid_results)'''