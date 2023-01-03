TODOC


## Example of docker build

```
docker build -t vocab:fr --build-arg spacy_model=fr_core_news_lg --build-arg additional_arg="-p fr -v french --disable_tag tagger_parser_ner --fasttext_model fr" --no-cache .
```

```
docker build -t vocab:en --build-arg spacy_model=en_core_web_lg --build-arg additional_arg="-p en -v english --disable_tag parser_ner --fasttext_model en" --no-cache .
```


```
docker build -t vocab:de --build-arg spacy_model=de_core_news_sm --build-arg additional_arg="-p de -v german --disable_tag tagger_parser_ner --fasttext_model de" --no-cache .
```

```
docker build -t vocab:it --build-arg spacy_model=it_core_news_sm --build-arg additional_arg="-p it -v italian --disable_tag tagger_parser_ner --fasttext_model it" --no-cache .
```

## Example of docker run

```
docker run --rm -v "E:/UNIL/backend/data/test_vocab_new_package/vocabulary/":/vm/data/ vocab:it
```