# extract_vocabulary

Contains everything to generate the vocabularies and handle them afterwards.

## Folder

### analysis

Scripts to analyze the created vocabularies.

### basic_method

Basic method used to create and use a vocabulary. Use it simplify your vocabulary creation or to emulate to make your own methods. Is a more generalized version than what is needed to extract the Wikipedia vocabulary.

### test_data

data to be used to test this folder.

Run the test_vocab.py to test the vocabulary creation.

### wiki_pages_based_vocab

Create vocabulary and synonyms using Wikipedia titles and redirect.

### wordpiece_ngrams

Method to try to extract ngrams from the text itself using the [wordpiece algorithm](https://arxiv.org/abs/1609.08144v2). Does not work well because it is difficult to differentiate genuine key expressions and colloquial expression.