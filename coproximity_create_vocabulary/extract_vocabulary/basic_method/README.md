# basic_method

Basic method used to create and use a vocabulary. Use it simplify your vocabulary creation or to emulate to make your own methods. Is a more generalized version than what is needed to extract the Wikipedia vocabulary.

## Scripts

### auto_reader_writer

Iterate over and write different type of extension. 

For now there are 3 extensions :
- .csv: csv files. By default the csv is considered as having of 2 columns: article id , their contents Their default arguments are delimiter=';' and default quotechar='"'
- .json : dictionary or list of a json file. By default considered the json as {article id: theirs contents}
- .jsons: file containing for each line a json. By default considered each line to be [article id, their contents]

To use the readers, you only need to iterate on them and close them at the end.

To use the writer, you can add elements by using writer.write_row, and once everything was written use writer.close.


## base_create_vocab_factory.py

Template for the different methods necessary to make create_ngram.py works

## create_ngram.py

Template to create a vocabulary and its synonyms.

### get_list_vocab.py

Transform the expected result of create_ngram into a more useful format for the ngram extraction. Used in https://github.com/matthieuDev/Projet_AdE-IMI to extract tokens form texts.

Get the processed synonyms and processed ngrams to the ngrams they represent for every ngram in the vocabulary, filter out ngrams which are too big, 
group the remainder by their numbers of words, sort it in descending order.

### util_wiki.py

Useful methods for creating the vocabulary