"""
Get the categories of Wikipedia pages from a XML dump
"""

import csv,re,json,time, bz2, os
csv.field_size_limit(100000000)

from coproximity_create_vocabulary.data_conf import base_vocab_folder

categories_re = re.compile (r'\[\[[^\]]*\]\]')
def get_categories(s) :
    '''
    Get the category in a line by getting all hyperlink linking to a Wikipedia page beginning with "Catégorie:
    '''
    urls = [url.strip('[').strip(']').strip() for url in categories_re.findall(s)]
    return [url for url in urls if url.startswith('Catégorie:')]

def get_categories_from_xml (from_xml , id2categories_filename, title2categories_filename) :
    """
    Get the categories of Wikipedia pages from a XML dump

    from_xml : path to the xml file to parse
    id2categories_filename: path in which to save the dict {wikipedia id: categories}
    title2categories_filename: path in which to save the dict {wikipedia title: categories}
    """

    if os.path.exists(title2categories_filename) and os.path.exists(title2categories_filename) :
        print('get_categories_from_xml already done')
        return

    #state for where on the article we are
    #outside any article
    OUT_ARTICLE = 0
    #in the header where there is the id and name
    IN_HEADER = 1
    #in the article but not in the header or the text
    IN_ARTICLE = 2
    #in the text itself
    IN_TEXT = 3


    #set the states
    state = OUT_ARTICLE

    page_id = ''
    page_title = ''

    id2categories = {}
    title2categories = {}

    counter = 0



    with bz2.open(from_xml) as f_in :
        for line in f_in :
            line = line.decode('utf-8')
            ################## OUT_ARTICLE ##################
            if state == OUT_ARTICLE :
                #change state if we enter a page
                if '<page>' in line :
                    categories = []
                    #print some time to see how well the program is going.
                    if counter % 100000 == 0 :
                        print(counter , time.ctime())

                    counter += 1
                    state = IN_HEADER
                #if we leave an article without being into one or without any line between the beginning and end, we consider that there is a problem  
                if '</page>' in line :
                    print ('line')
                    raise Exception('article open before the one before being closed')

            ################## IN_HEADER ##################
            elif state == IN_HEADER :
                #if we are on a title or id tag, save its value
                if '<title>' in line :
                    page_title = re.findall("<title>(.*)</title>", line)[0]
                if '<id>' in line :
                    page_id = re.findall("<id>(.*)</id>", line)[0]
                #if we quit the header we change state
                if '<revision>' in line :
                    assert page_title != '' and page_id != '' , 'page_title or page_id not found'
                    state = IN_ARTICLE

            ################## IN_ARTICLE ##################
            elif state == IN_ARTICLE :

                #change state if we enter the text
                if '<text' in line :
                    #Get the category of the current line if there is any
                    categories.extend(get_categories(line))
                    #if we quit the text in the same line we entered it, discard it. 
                    if '</text>' in line :
                        state = IN_ARTICLE

                    else :
                        state = IN_TEXT

                #if we quit the page change state and save the data of the article
                if '</page>' in line :
                    state = OUT_ARTICLE
                    id2categories[page_id] = categories
                    title2categories[page_title] = categories
                    categories = []


                #if a new page begins before one is closed, raise error
                if '<page>' in line :
                    raise Exception('page open before the one before being closed')

            ################## IN_TEXT ##################
            elif state == IN_TEXT :
                #Get the category of the current line if there is any
                categories.extend(get_categories(line))   

                # if the page ends while in text or on the same line, print  a warning and save the result
                if '</page>' in line :
                    state = OUT_ARTICLE


                #if we quit the text change state
                elif '</text>' in line :

                    state = IN_ARTICLE 
                #if a new page begins before one is closed, raise error
                if '<page>' in line :
                    raise Exception('page open before the one before being closed')

            else :
                raise Exception('state not found')

    with open(id2categories_filename, 'w', encoding='utf8') as f :
        json.dump(id2categories, f)

    with open(title2categories_filename, 'w', encoding='utf8') as f :
        json.dump(title2categories, f)

if __name__ == '__main__' :
    from_xml = base_vocab_folder + 'wikipedia/whole_test/wiki_fr_dump.xml.bz2'
    id2categories_filename = base_vocab_folder + 'wikipedia/whole/categories/id2categories.json'
    title2categories_filename = base_vocab_folder + 'wikipedia/whole/categories/title2categories.json'
    get_categories_from_xml (from_xml , id2categories_filename, title2categories_filename ) 