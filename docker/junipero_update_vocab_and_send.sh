mkdir ../vocabulary

docker build -f dockerfile_send_data -t vocab_and_send:fr --build-arg spacy_model=fr_core_news_lg --build-arg additional_arg="-p fr -l french --disable_tag tagger_parser_ner --fasttext_model fr" --no-cache .
docker build -f dockerfile_send_data -t vocab_and_send:en --build-arg spacy_model=en_core_web_lg --build-arg additional_arg="-p en -l english --disable_tag parser_ner --fasttext_model en" --no-cache .

docker run --rm -v "../vocabulary/":/vm/data/ vocab_and_send:fr
docker run --rm -v "../vocabulary/":/vm/data/ vocab_and_send:en
