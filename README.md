# wikipedia_downloader

Allows to easily download the dumps of Wikipedia for pageviews and redirections. Use them to create a vocabulary as a list of tokens with synonyms. The main aim of this repository is to create a vocabulary from Wikipedia to be used for https://github.com/matthieuDev/Projet_AdE-IMI to extract keywords from texts.  

Also allows to download the Wikipedia articles dumps and extract the plain article from them.


## Mains

To easily explain the repository, we can refer to 3 mains :

### main_downloader_wiki.py 

Path: coproximity_create_vocabulary/download_wikipedia/get_pages_views/main_downloader_wiki.py

Given a Wikipedia project and a name (for language folder), from scratch, downloads the views since january 2016 and the redirections. The results are 2 csv files: one with the articles with their views sorted on them in descending order, and the other with the redirections. To be used if you don't care about the vocabulary, and only want the pageviews and redirections.

### main_generate_vocab.py

Path: coproximity_create_vocabulary/main_generate_vocab.py

Download the dumps from Wikipedia and create the main vocabularies from scratch. Generate the vocabulary structure below. The main result of this is the main_dict_vocab.json that represents the vocabulary in 1 file.

Can be used with arguments :

- '--project', '-p': project: Wikipedia project from which to extract the data from
- '--language_name', '-l': name of the language folder, where all the data specific to this language will be stored
- '--fasttext_model': spacy model used to lemmatize the titles during the vocabulary creation
- '--spacy_model': tags to disable in the spacy model (to speed it up) during the vocabulary creation. If None, try to get a default value from 
    coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.get_args.var_getter_by_project using project as a key
- '--disable_tag': fasttext model to use to create word2vec vectors from articles during the vocabulary creation. If None, try to get a default value from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.get_args.var_getter_by_project using project as a key

example:  python main_generate_vocab.py --project it --language_name italian --spacy_model it_core_news_lg --disable_tag parser_ner --fasttext_model fr

Warning: to avoid re downloading all the page views at each new Wikipedia project, the project to keep are set in the .env. If you want to add a project that was not in the .env, you need to add it, delete all the count from the {base folder}/dumps folder and re run the main. 

### update_wikipedia_dataset.py

Path: coproximity_create_vocabulary/download_wikipedia/create_wikipedia_plain/update_wikipedia_dataset.py

Download the article Wikipedia dump, parse them, and get the best views from them.

## repository variables

This repository used some repository variables. Those variables will be used in a lot of scripts and over multiple usage. They need to be easilly available and to be static over multiple sessions. There are 2:

- base_vocab_folder: The folder in which all the folder and files will be generated/downloaded/saved. This is the base of the structure described below. 

- set_allowed_download_projects: The set of all projects that will be considered for this usage. It is mostly used to know which project to keep in the count dumps (to use less space). If you want to add a project that was not in the .env, you need to add it, delete all the count from the {base folder}/dumps folder and re run the main. The format of this variable should be a string of all desired projects separeted by '_'. i.e. if we want english, german, italian and french, we give it : en_de_it_fr 

TODOC décrire utilisation du script pour set le .env

## Vocabulary creation structure

This module will create a path structure in the base folder (set in the .env), here is a description:

| -- {vocabulary base folder}: folder set in the .env to be the base folder of the vocabularies\
|\
|&emsp;| -- dumps: where the dumps used in all projects will be stored. It will contains the count dumps.\
|\
|&emsp;| -- {language folder}: folder where all the dumps, dumps extraction and vocabularies of one language will be saved. There can be multiple language folder.\
|&emsp;|\
|&emsp;|&emsp;| --dumps: folder containing all the dumps for this language (pages, redirect, article dump, article dump index). See Wikipedia dumps for more info.\
|&emsp;|\
|&emsp;|&emsp;| --meta: Folder containing the metadata of the vocabulary\
|&emsp;|&emsp;|\
|&emsp;|&emsp;|&emsp;| --id2title.json: Dictionary: wikipedia id -> Wikipedia title\
|&emsp;|&emsp;|\
|&emsp;|&emsp;|&emsp;| --multi_synonyms_text.json: Text of all main tokens which are in a multiple_synonyms.json. To be used when the meta are put online, so that the user can still disambiguate while not having to redownload Wikipedia dumps.\
|&emsp;|&emsp;|\
|&emsp;|&emsp;|&emsp;| --sorted_view_wiki_over_years.csv: the articles with their views sorted on them in descending order. (Result of main_downloader_wiki.py)\
|&emsp;|&emsp;|\
|&emsp;|&emsp;|&emsp;| --{processed articles title file}.csv: sorted_view_wiki_over_years.csv to which we added the processed version of its titles. In the main it is formatted as "sorted_view_wiki_over_years_{spacy model}_{first letters of the spacy disable tag}.csv"\
|&emsp;|&emsp;|\
|&emsp;|&emsp;|&emsp;| --synonyms.csv: Wikipedia redirections. (Result of main_downloader_wiki.py)\
|&emsp;|&emsp;|\
|&emsp;|&emsp;|&emsp;| --{processed synonyms file}.csv: synonyms.csv to which we added the processed version of its synonyms. In the main it is formatted as "synonyms_{spacy model}_{first letters of the spacy disable tag}.csv"\
|&emsp;|\
|&emsp;|&emsp;| --ngram_title_wiki: folder containing the vocabularies of this language.\
|&emsp;|&emsp;| \
|&emsp;|&emsp;|&emsp;| {vocabulary folder}: Folder that contains all files for a vocabulary. There can be multiple vocabulary folder.\
|&emsp;|&emsp;|&emsp;|\
|&emsp;|&emsp;|&emsp;|&emsp;| --discarded_token.json: List of tokens considered but discarded for this vocabulary\
|&emsp;|&emsp;|&emsp;|\
|&emsp;|&emsp;|&emsp;|&emsp;| --has_double.json: List of synonyms which redirect to multiple main tokens when adding lowercase. Use for debug, is not a problem in french and english.\
|&emsp;|&emsp;|&emsp;|\
|&emsp;|&emsp;|&emsp;|&emsp;| --ignored_synonyms.json: List of ignored synonyms\
|&emsp;|&emsp;|&emsp;|\
|&emsp;|&emsp;|&emsp;|&emsp;| --main_dict_vocab.json: Main file to describe the vocabulary. Dict {token: [lematized token, main page if the token was a synonym otherwise it is an empty string, number of word of the token]}\
|&emsp;|&emsp;|&emsp;|\
|&emsp;|&emsp;|&emsp;|&emsp;| --multiple_synonyms.json: Synonyms that redirect to multiple main tokens.\
|&emsp;|&emsp;|&emsp;|\
|&emsp;|&emsp;|&emsp;|&emsp;| --multiple_vecs.pkl: Vector (created based on Word2vec) of the main tokens from multiple_synonyms.json. Used to chose which main tokens is closer to a synonym from multiple_synonyms.json based on the context.\
|&emsp;|&emsp;|&emsp;|\
|&emsp;|&emsp;|&emsp;|&emsp;| --set_tokens.json: Set of the tokens that are considered the main tokens of this vocabulary.\
|&emsp;|&emsp;|&emsp;|\
|&emsp;|&emsp;|&emsp;|&emsp;| --synonyms.json: Dictionary of all tokens that are considered synonyms of a main token.\
|&emsp;|&emsp;|&emsp;|\
|&emsp;|&emsp;|&emsp;|&emsp;| --word_to_bad_synonyms.json: Reason why some synonyms were discarded\
|&emsp;|\
|&emsp;|&emsp;| --cc.{project}.300.bin cc.{project}.300.bin.gz: fasttext model used for this language. Used for disambiguation when synonyms redirect to multiple main tokens.\
|&emsp;|\


Note: {...} are variable set in the code, the ... is the name of the variable. If there is non {} around something, it is hard coded
