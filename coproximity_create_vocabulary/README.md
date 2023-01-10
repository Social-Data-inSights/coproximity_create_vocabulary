# create_vocab

Create the vocabulary to detect in texts to be used as nodes in the graph.

## File

### .env

File containing the values of the data_conf. Putting them in the .env allows to easily use and set them. If you don't have this file, it is recommended to use generate_env.py to generate it.

### data_conf.py

data configuration file. Give variables that should be easily accessible and static over multiple sessions, but that can be change by the user. There are 2:

- base_vocab_folder: The folder in which all the folder and files will be generated/downloaded/saved.

- set_allowed_download_projects: The set of all projects that will be considered for this usage. It is mostly used to know which project to keep in the count dumps (to use less space). If you want to add a project that was not in the .env, you need to add it, delete all the count from the {base folder}/dumps folder and re run the main. The format of this variable should be a string of all desired projects separated by '_'. i.e. if we want english, german, italian and french, we give it : en_de_it_fr 

### generate_env.py

File to generate .env based. Needs to give both the base folder with parent_folder_init and the allowed download projects with allowed_download_projects.
If a .env already exists, it is used to give default values if one of the 2 arguments are missing. Otherwise, if 1 argument is missing, an error will be raised.

Example :

python generate_env.py --parent_folder_init E:/UNIL/backend/data/whole/vocabulary/ --allowed_download_projects fr_en_it_de

### main_generate_vocab.py

Main script for creating the vocabularies from scratch

Creates the main vocabularies from scratch: download the dumps, extract only the main articles, sort them by pageviews, get the redirections 
and create the main vocabularies from them.

Can be activated py passing arguments :

- '--project', '-p': project: Wikipedia project from which to extract the data from
- '--language_name', '-l': name of the language folder, where all the data specific to this language will be stored
- '--fasttext_model': spacy model used to lemmatize the titles during the vocabulary creation
- '--spacy_model': tags to disable in the spacy model (to speed it up) during the vocabulary creation. If None, try to get a default value from 
    coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.get_args.var_getter_by_project using project as a key
- '--disable_tag': fasttext model to use to create word2vec vectors from articles during the vocabulary creation. If None, try to get a default value from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.get_args.var_getter_by_project using project as a key

example:  python main_generate_vocab.py --project it --language_name italian --spacy_model it_core_news_lg --disable_tag parser_ner --fasttext_model fr

## Folder

### download_wikipedia

Folder containing everything to download and handle dumps

### extract_vocabulary

Contains everything to generate the vocabularies from the results of download_wikipedia, and handle them afterwards