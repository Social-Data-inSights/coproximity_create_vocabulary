# send_static_share

Access the server containing the statistically shared data. It has scripts to send and load the default vocabulary and data needed to create your own vocabulary from scratch.

### handle_server.py

Send data to the static share.

### load_static_share.py

Load the main zip for compascience's static share

### main_send_static_share.py

Creates the main vocabularies from scratch: download the dumps, extract only the main articles, sort them by pageviews, get the redirections 
and create the main vocabularies from them. And then zip the meta folder (in which the synonyms and lexicon are saved, with their precessed version) and main vocabulary (vocabulary with a lexicon of size 1e5, with uppercase and accents)
and send them to the static_share server.

use the command line arguments from the coproximity_create_vocabulary.main_generate_vocab parser

example:  python main_send_static_share.py --project it --language_name italian --spacy_model it_core_news_lg --disable_tag parser_ner --fasttext_model fr


### zip_vocab.py

create the zip to send to the static share