# create_vocab

Create the vocabulary to detect in texts to be used as nodes in the graph.

## Folder

### analysis

Scripts to analyze the created vocabularies.

### basic_method

Basic method used to create and use a vocabulary. Use it simplify your vocabulary creation or to emulate to make your own methods.

### test_data

data to be used to test this folder.

Run the test_vocab.py to test the vocabulary creation.

### wiki_pages_based_vocab

Create vocabulary and synonyms using Wikipedia titles and redirect.

### wordpiece_ngrams

Method to try to extract ngrams from the text itself using the [wordpiece algorithm](https://arxiv.org/abs/1609.08144v2). Does not work well because it is difficult to differentiate genuine key expressions and colloquial expression.
