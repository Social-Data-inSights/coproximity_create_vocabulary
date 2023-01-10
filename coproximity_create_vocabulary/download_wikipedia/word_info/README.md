# word_info

Get the categories of the Wikipedia pages. Used to create an alternative vocabulary without the titles of films, TV series, books and music which were considered as too problematic.

### download_categories_sub_categories_from_wiki_page.ipynb

Notebook used to debug download_categories_sub_categories_from_wiki_page.py .To delete once download_categories_sub_categories_from_wiki_page.py is stable 

### download_categories_sub_categories_from_wiki_page.py

Download the subcategories by recursively requesting them to Wikipedia. Based on the structure of subcategories from the Wikipedia categories. 
(ex: section "Sous-catégories" from https://fr.wikipedia.org/wiki/Cat%C3%A9gorie:Cin%C3%A9ma)

Tuned only for french, but can be a base for other languages.

### main_categories.py

Main file of the folder

Get all you need to filter based on categories for the french wiki titles

### get_categories_from_xml.py

Get the categories of Wikipedia pages from a XML dump
