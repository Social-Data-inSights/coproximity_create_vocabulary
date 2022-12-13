# create_vocab

Create vocabulary and synonyms using Wikipedia titles and redirect.

## Folder

### get_pages_views

Scripts used to get the pageviews of Wikipedia articles and their redirects (to be used as synonyms). 

### word_info

Get the categories of the Wikipedia pages.

## Scripts

### get_args.py

Get the variables to filter: stop words, duplicate stop words, processed method, the synonyms to ignore, handpicked words and synonyms, and the name of the spacy model

### main_wikititle_en.py

Get the english vocabulary and synonyms from the most viewed wikipedia pages and their redirections

### main_wikititle_en2fr.py

Get the vocabulary that takes the vocabulary and synonyms from the best english pages and their redirections. 
And link them to a translation to the french Wikipedia

### main_wikititle.py

Get the french vocabulary and synonyms from the most viewed wikipedia pages and their redirections

### main_wikitionary.py

use wiki title as vocab and wikitionnary as synonyms. Language is french

### synonym_dictionnary_wiktionnary.py

Extract synonyms and equivalent (derivative or related) for wiktionary

### util_wiki.py

Useful methods for Wikipedia title handling

### wiki_title.py

get the methods to use in create_ngram.py to extract the vocabulary and the synonyms from the most viewed wikipedia pages and their redirections
