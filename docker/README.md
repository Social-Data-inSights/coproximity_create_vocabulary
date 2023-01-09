# Docker

Contains a dockerfile which creates a docker that allows to generate a vocabulary from scratch. 

## Docker build

For the file the docker file takes care of almost everything, you just need to pass 2 arguments

- spacy_model: the spacy model to be used form lemmatisation
- additional_arg: the arguments to pass to the main_generate_vocab.py (except spacy_model, because we already have).
    i.e. the project (-p), vocabulary name (-l), spacy disable tag (--disable_tag), fasttext model (fasttext_model)

Warning:

Using --no-cache is highly recommended to be able to pull the latest version of this module.

### Example of docker build

```
docker build -t vocab:fr --build-arg spacy_model=fr_core_news_lg --build-arg additional_arg="-p fr -l french --disable_tag tagger_parser_ner --fasttext_model fr" --no-cache .
```

```
docker build -t vocab:en --build-arg spacy_model=en_core_web_lg --build-arg additional_arg="-p en -l english --disable_tag parser_ner --fasttext_model en" --no-cache .
```

Warning: here we used *_sm spacy model, because those were used as test. It is recommended to download more robust spacy model.

```
docker build -t vocab:de --build-arg spacy_model=de_core_news_sm --build-arg additional_arg="-p de -l german --disable_tag tagger_parser_ner --fasttext_model de" --no-cache .
```

```
docker build -t vocab:it --build-arg spacy_model=it_core_news_sm --build-arg additional_arg="-p it -l italian --disable_tag tagger_parser_ner --fasttext_model it" --no-cache .
```

## Docker run

Once the docker is build we just have to run it: it only needs to link the volume to the folder you wish to store all the vocabulary (i.e. the vocabulary base folder) to the docker data folder by using volume i.e. "path/to/your/folder":/vm/data/

It is advised to use --rm to delete the docker once the vocabularies are created/updated, because once it is done, the container is useless.

### Example of docker run

```
docker run --rm -l "E:/UNIL/backend/data/test_vocab_new_package/vocabulary/":/vm/data/ vocab:it
```