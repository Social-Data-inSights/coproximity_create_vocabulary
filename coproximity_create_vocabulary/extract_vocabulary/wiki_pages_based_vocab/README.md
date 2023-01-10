# wiki_pages_based_vocab

Create vocabulary and synonyms using Wikipedia titles and redirect.

## Mains

This module was created to be used in an other one : https://github.com/matthieuDev/Projet_AdE-IMI/ . This creates 2 sort on main in this vocabulary creation:

- main_get_default_by_project.py: which is the main you will have to use if you want to create vocabulary without using the other project. It is used in the main of this module (main_generate_vocab.py)

- And the mains that are used with Projet_AdE-IMI (let's call them "with data project mains"). Which considered that there exists a folder (called base_data_folder) containing extracted data from different dataset (here the most important one is Wikipedia), and use them.

### main_get_default_by_project.py

Allows to create a vocabulary from only elements downloaded and created by coproximity_create_vocabulary.download_wikipedia.get_pages_views.main_downloader_wiki ,for any project whose data were downloaded and processed.

### main_wikititle_en.py

Get the english vocabulary and synonyms from the most viewed wikipedia pages and their redirections ("with data project mains")

### main_wikititle.py

Get the french vocabulary and synonyms from the most viewed wikipedia pages and their redirections ("with data project mains")

## Folder

### alt_vocab

Alternative vocabulary that were proposed but did not became the main ones because it was not possible to know which one were better. They are "with data project mains".

## Scripts

### get_args.py

Get the variables to filter for the main languages (French and English): stop words, duplicate stop words, processed method, the synonyms to ignore, handpicked words and synonyms, and the name of the spacy model

### util_wiki.py

Useful methods for Wikipedia title handling

### wiki_title.py

get the methods to use in create_ngram.py to extract the vocabulary and the synonyms from the most viewed wikipedia pages and their redirections
