# Docker

Contains a dockerfile which creates a docker that allows to generate a vocabulary from scratch. 

## Docker build

For the file the docker file takes care of almost everything, you just need to pass 2 arguments

- spacy_model: the spacy model to be used form lemmatisation
- additional_arg: the arguments to pass to the main_generate_vocab.py (except spacy_model, because we already have it).
    i.e. the project (-p), vocabulary name (-l), spacy disable tag (--disable_tag), fasttext model (fasttext_model)

Warning:

Using --build-arg STOP_CACHE=(date +%s) is highly recommended to be able to pull the latest version of this module.
If this option is not available, replace the (date +%s) by different number each time.
If you really don't like that, use --no-cache but you will re download the spacy model.

### Example of docker build

```
docker build -t vocab:fr --build-arg spacy_model=fr_core_news_lg --build-arg additional_arg="-p fr -l french --disable_tag tagger_parser_ner --fasttext_model fr" --build-arg STOP_CACHE=(date +%s) .
```
Or

```
docker build -t vocab:fr --build-arg spacy_model=fr_core_news_lg --build-arg additional_arg="-p fr -l french --disable_tag tagger_parser_ner --fasttext_model fr" --build-arg STOP_CACHE=42 .
```

Or else with --no-cache 

```
docker build -t vocab:fr --build-arg spacy_model=fr_core_news_lg --build-arg additional_arg="-p fr -l french --disable_tag tagger_parser_ner --fasttext_model fr" --no-cache .
```

```
docker build -t vocab:en --build-arg spacy_model=en_core_web_lg --build-arg additional_arg="-p en -l english --disable_tag parser_ner --fasttext_model en" --build-arg STOP_CACHE=(date +%s) .
```

Warning: here we used *_sm spacy model, because those were used as test. It is recommended to download more robust spacy model.

```
docker build -t vocab:de --build-arg spacy_model=de_core_news_sm --build-arg additional_arg="-p de -l german --disable_tag tagger_parser_ner --fasttext_model de" --build-arg STOP_CACHE=(date +%s) .
```

```
docker build -t vocab:it --build-arg spacy_model=it_core_news_sm --build-arg additional_arg="-p it -l italian --disable_tag tagger_parser_ner --fasttext_model it" --build-arg STOP_CACHE=(date +%s) .
```

## Docker run

Once the docker is build we just have to run it: it only needs to link the volume to the folder you wish to store all the vocabulary (i.e. the vocabulary base folder) to the docker data folder by using volume i.e. "path/to/your/folder":/vm/data/

It is advised to use --rm to delete the docker once the vocabularies are created/updated, because once it is done, the container is useless.

### Example of docker run

```
docker run --rm -v "E:/UNIL/backend/data/test_vocab_new_package/vocabulary/":/vm/data/ vocab:it
```

## Send data to server Docker

To do the build and run to create the vocabulary and send to the compascience static share. (default vocabulary easily accessible)

```
nohup ./junipero_update_vocab_and_send.sh > log.txt &
```

Recommended cron for this command :

```
crontab -l | { cat; echo "0 0 3 * * ./junipero_update_vocab_and_send.sh > log.txt"; } | crontab -
```