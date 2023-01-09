# basic_method

Basic method used to create and use a vocabulary. Use it simplify your vocabulary creation or to emulate to make your own methods. Is a more generalized version than what is needed to extract the Wikipedia vocabulary.

## Scripts

## base_create_vocab_factory.py

Template for the different methods necessary to make create_ngram.py works

## create_ngram.py

Template to create a vocabulary and it synonyms.

### get_list_vocab.py

Transform the expected result of create_ngram into a more usefull format for the ngram extraction.

Get the processed synonyms and processed ngrams to the ngrams they represent for every ngram in the vocabulary, filter out ngrams which are too big, 
group the remainder by their numbers of words, sort it in descending order.

### util_wiki.py

Useful methods for creating the vocabulary