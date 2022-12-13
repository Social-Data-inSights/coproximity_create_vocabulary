'''
download dump here : https://dumps.wikimedia.org/frwiktionary/20211020/
Extract synonyms and equivalent (derivative or related) for wiktionary
'''

import json, os, time, re, csv

from coproximity_create_vocabulary.data_conf import base_vocab_folder

def new_dict_data() :
    return {
        'synonymes' : [],
        'dérivés': [],
        'apparentés': [],
        'id' : -1,
        'title' : ''
    }

def create_wiktionary_dictionnary(xml_file, synonym_file ) :
    

    if os.path.exists(synonym_file) :
        print('wiktionary synonyms already exists')
        return

     #state for where on the article we are
    #outside any article
    OUT_ARTICLE = 0
    #in the article
    IN_ARTICLE = 1
    #in the text
    IN_TEXT = 2

    re_text_state = re.compile(r'=+ *{{S\|(.*)}} *=+')
    re_text_value = re.compile(r'\* \[\[(.*)\]\]')

    set_good_state_in_article = { 'synonymes', 'dérivés', 'apparentés',}

    state = OUT_ARTICLE
    state_text = ''
    counter = 0  

    res = {}
    curr = new_dict_data()

    with open(xml_file, encoding='utf8') as f :
        for i, line in enumerate(f) :
            line = line.strip()
            line = line.replace('\xa0', ' ')
            ################## OUT_ARTICLE ##################
            if state == OUT_ARTICLE :
                #change state if we enter a page
                if '<page>' in line :
                    #print some time to see how well the program is going.
                    if counter % 100000 == 0 :
                        print(counter , time.ctime())
                    counter += 1
                    state = IN_ARTICLE
                #if we leave an artiacle without being into one or without any line between the beginning and end, we consider that there is a problem  
                if '</page>' in line :
                    print ('line')
                    raise Exception('article open before the one before being closed')
            #if we are in an article
            elif state == IN_ARTICLE :
                #get title if title found
                if '<title>' in line :
                    curr['title'] = re.findall("<title>(.*)</title>", line)[0]
                #get article id if id found
                if '<id>' in line :
                    curr['id'] = re.findall("<id>(.*)</id>", line)[0]
                #change state if we enter the text
                if '<text' in line :
                    #if we quit the text in the same line we entered it, discard it. 
                    state = IN_TEXT
                    
                #update the result and change state if we're leaving the page
                if '</page>' in line :
                    assert curr['id'] != -1 and curr['title'] != ''
                    res [curr['title']] = curr
                    curr = new_dict_data()
                    
                    state_text = ''
                    state = OUT_ARTICLE
                #can't open a page before the previous one is closed
                if '<page>' in line :
                    print (line)
                    raise Exception('page open before the one before being closed')
                    
            elif state == IN_TEXT :
                # if we are in a part where we can found synonyms or equivalent, search them and add them if some are found
                if state_text :
                    try_value = re_text_value.search(line)
                    if try_value :
                        curr[state_text].append(try_value.group(1))
                    '''else :
                        print('failed', line,  )'''
                #Check if we are entering into a part where we can found synonyms or equivalent
                if line.startswith('===') :
                    try_state = re_text_state.search(line)
                    if try_state :
                        try_state=try_state.group(1)
                        state_text = try_state if try_state in set_good_state_in_article else ''
                    '''else :
                        if '{{' in line :
                            print('failed', line,  )'''
                
                
                # if the page ends while in text or on the same line, print  a warning and save the result
                if '</page>' in line :
                    state_text = ''
                    state = OUT_ARTICLE

                    assert curr['id'] != -1 and curr['title'] != ''
                    res [curr['title']] = curr
                    curr = new_dict_data()

                #if we quit the text change state
                elif '</text>' in line :
                    state = IN_ARTICLE 
                #if a new page begins before one is closed, raise error
                if '<page>' in line :
                    print (line)
                    raise Exception('page open before the one before being closed')

    with open(synonym_file, 'w' , encoding='utf8') as f :
        json.dump(res, f)

def wiktionnary_to_csv (wiktio_file, wiktio_csv) :
    """
    Transform the synonym json into a csv to be able to be read by wiki_title
    """
    if os.path.exists(wiktio_csv) :
        print('wiktionary csv synonyms already exists')
        return

    with open(wiktio_file, encoding='utf8') as f :
        wikt_snynonym = json.load(f)

    rewikititle = lambda x : x[0].upper() + ( x[1:] if len(x) > 1 else '')

    with open(wiktio_csv, 'w', encoding='utf8', newline='') as f :
        writer = csv.writer(f, delimiter=';', quotechar='"')
        for title, dict_values in wikt_snynonym.items() :
            title = rewikititle(title)
            for syn in dict_values['synonymes'] :
                syn = rewikititle(syn)
                writer.writerow((title, syn))

if __name__ == '__main__' :
    data_folder = base_vocab_folder + '/'
    thesaurus_folder = data_folder + 'whole/thesaurus/'

    xml_file = thesaurus_folder + 'frwiktionary-20211020-pages-articles-multistream.xml'
    synonym_file = thesaurus_folder + 'wiktionary_synonyms.json'
    wiktio_csv = thesaurus_folder + 'wiktionary_synonyms.csv'

    create_wiktionary_dictionnary(xml_file, synonym_file) 
    wiktionnary_to_csv (synonym_file, wiktio_csv)
