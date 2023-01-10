# create_wikipedia_plain

Download the dump from wikipedia and create from it a json files containing all the articles containing enough words. Also allow to take a subset of this plain file.

## Scripts

### create_art_id2info_wiki.py

create the information files for the wikipedia dataset: the title and what to add to the url to get the page (which is also the title).


### split_articles_to_csv.py

Transform a wikitext xml dump into a csv of the article ids with their plain texts

### subset_whole_plain.py

Get subsets of the whole wikipedia dataset. Split by size or number of views.

### update_wikipedia_dataset.py

Main file. Update the wikipedia dataset by downloading the most recent wikipedia dump and recreating the plain wikipedia files.
