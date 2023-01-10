# get_pages_views

Scripts used to get the pageviews of Wikipedia articles and their redirects (to be used as synonyms). 

### download_synonyms.py

Download the redirects of Wikipedia articles and the id to title dictionary.

redirects: https://dumps.wikimedia.org/{project}wiki/latest/{project}wiki-latest-redirect.sql.gz    

pages : https://dumps.wikimedia.org/{project}wiki/latest/{project}wiki-latest-page.sql.gz

### download_wiki_title.py

Download the pageviews by article (by default start the count in January 2016)

Pageviews from 2015 : https://dumps.wikimedia.org/other/pageview_complete/ 

### main_downloader_wiki.py

main file to download and process the wikipedia dumps from wikipedia for creating a vocabulary.
Create 2 csv:
    - a list of articles title with the number of time it was viewed sorted descendingly
    - a list of redirection from a redirection to the main page it redirects to

It also downloads the article dumps of Wikipedia to be used to get a text to create a vector representing articles using word2vec.