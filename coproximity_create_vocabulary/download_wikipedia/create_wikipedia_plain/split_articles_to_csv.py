"""
Transform a wikitext xml dump into a csv of the article ids with their plain texts
"""

import csv,re,json,time,os, mwparserfromhell, bz2
csv.field_size_limit(100000000)

def wikitext_to_plain (wikitext) :
    '''
    parse a mediawiki text.

    Parse a first time, delete the urls and reparse a second time to be sure
    '''
    parsed_wikitext = mwparserfromhell.parse(wikitext).strip_code(normalize=True, collapse=True)
    parsed_wikitext = re.sub(r'(www.|https?://)[-a-zA-Z0-9@:%._/\+~#=]+' , ' ' , parsed_wikitext)
    return mwparserfromhell.parse(parsed_wikitext).strip_code(normalize=True, collapse=True)


def count_words (s) :
    '''
    Count the number of words in a text
    '''
    return re.sub( ' +', ' ', s.replace('\n' , ' ').strip() ).count(' ')

def preprocess_wiki_text (wikitext , threshold_skip_little) :
    '''
    Take a string of MediaWiki markup {wikitext} and return its plain text with a boolean "if this article must be discarded"

    threshold_skip_little : minimum number of words an article must have under which it is discarded
    '''
    try :
        plain = wikitext_to_plain(wikitext)
        if (  count_words(plain) < threshold_skip_little ):
            return '', True
        else :
            return plain, False

    except KeyError :
        return '', True
    except mwparserfromhell.parser.ParserError :
        return '', True

def get_check_only (get_only_ids, get_only_title, id_, title) :
    if get_only_ids :
        if id_ in get_only_ids :
            get_only_ids.remove(id_)
            return True, get_only_ids, get_only_title, not bool(get_only_ids)
    if get_only_title :
        if title in get_only_title:
            get_only_title.remove(title)
            return True, get_only_ids, get_only_title, not bool(get_only_title)
    return False, get_only_ids, get_only_title, False

def split_articles_to_csv (whole_dir, from_xml_bz2 , dump_save_to, threshold_skip_little = 100, what_to_do_result = 'save', get_only_ids = None, get_only_title = None, is_printing=True) :
    """
    Take the file path {from_xml_bz2} to the bz2 compressed Wikipedia dump and creates a csv of the plain text of the articles.

    whole_dir: folder in which will be created the meta folder, in which will be saved the information of the articles.
    from_xml_bz2: wikipedia dump from which to extract the 
    dump_save_to: path to where the csv dump will be saved 
    threshold_skip_little: minimum number of words under which an article is discarded from the csv
    what_to_do_result: TODOC
    get_only_title get_only_ids TODOC
    is_printing TODOC
    """
    assert what_to_do_result in {'save', 'return_dict_id', 'return_dict_title'}

    # direction of the important file and folder
    meta_dir = whole_dir + '/meta_wiki'

    #create the folder if it does not exists
    if not os.path.exists(meta_dir) :
        os.mkdir(meta_dir)

    #state for where on the article we are
    #outside any article
    OUT_ARTICLE = 0
    #in the header where there is the id and name
    IN_HEADER = 1
    #in the article but not in the header or the text
    IN_ARTICLE = 2
    #in the text itself
    IN_TEXT = 3

    #use when the page is a redirect, note which article redirect to which other.
    is_redirect = False
    redirect_to = ''

    #used when the page is one line : just ignore it. and note which one was passed.
    skip_little = False
    skipped = []

    #set the states
    state = OUT_ARTICLE

    page_id = ''
    page_title = ''
    page_content = ''

    #dictionary {name of an article: its id}
    title_to_id = {}
    #dictionary {id:name_article} where the article with id : id, redirect to article named name_article
    redirections = {}
    # ids of all articles saved in the file
    ids = []

    #used to see how many pages were considered
    counter = 0    

    # if the dump was already started, load the ids of all the already parsed articles (to skip them)
    set_id_already = set()
    if dump_save_to and os.path.exists(dump_save_to) and what_to_do_result == 'save':
        with open(dump_save_to ,encoding='utf8' , newline='', errors = 'replace' ) as old_csv :
            reader = csv.reader(old_csv, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL ,)
            for art_id , _ in reader :
                set_id_already.add(art_id)

    with bz2.open(from_xml_bz2) as f_in :
        if what_to_do_result == 'save' :
            f_out =  open(dump_save_to , 'a' , encoding='utf8' , newline='', errors = 'replace' ) 
            writer = csv.writer(f_out, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        elif what_to_do_result.startswith('return'):
            to_return = {}

        for line in f_in :
            line = line.decode('utf8')
            ################## OUT_ARTICLE ##################
            if state == OUT_ARTICLE :
                #change state if we enter a page
                if '<page>' in line :
                    #print some time to see how well the program is going.
                    if counter % 10000 == 0 and is_printing:
                        print(counter , time.ctime())
                        
                    counter += 1
                    state = IN_HEADER
                #if we leave an artiacle without being into one or without any line between the beginning and end, we consider that there is a problem  
                if '</page>' in line :
                    print ('line')
                    raise Exception('article open before the one before being closed')
            
            ################## IN_HEADER ##################
            elif state == IN_HEADER :
                #if we are on the balise for the title or id, save its value
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
                    #add the line to the content to save
                    page_content += line

                    #if we quit the text in the same line we entered it, discard it. 
                    if '</text>' in line :
                        state = IN_ARTICLE
                        # check if the article is a redirect, if it is and we can know where it is pointing to save it.
                        if any ( [ red in line for red in ['#Redirect','#redirection','#redirect','#REDIRECTION','#REDIRECT',]]) :
                            redirect_to = re.findall(r"\[\[(.*)\]\]", line)
                            if redirect_to :
                                is_redirect = True
                                redirect_to = redirect_to[0]
                            elif is_printing :
                                print('failed redirect',line)

                    else :
                        state = IN_TEXT
                    
                #if we quit the page change state and save the data of the article
                if '</page>' in line :
                    state = OUT_ARTICLE

                    #if we redirected , save from which article to which article the redirection goes to.
                    if is_redirect :
                        if what_to_do_result == 'save' :
                            redirections [page_id] = redirect_to
                        redirect_to = ''
                    # if we skip the result because it was too little, add this article to the list of skipped
                    elif skip_little or (  page_content.count(' ') < threshold_skip_little ):
                        if what_to_do_result == 'save' :
                            skipped.append(page_id)
                    #otherwise save the result of the article
                    else :
                        add_current, get_only_ids, get_only_title, has_ended = get_check_only(get_only_ids, get_only_title, page_id, page_title)
                        if not page_id in set_id_already and add_current:

                            plain , skip_little = preprocess_wiki_text(page_content, threshold_skip_little)
                            if skip_little :
                                if what_to_do_result == 'save' :
                                    skipped.append(page_id)
                            else :
                                if what_to_do_result == 'save' :
                                    writer.writerow([page_id , plain])
                                    ids.append(page_id) 
                                elif what_to_do_result == 'return_dict_id' :
                                    to_return[page_id] = plain
                                elif what_to_do_result == 'return_dict_title' :
                                    to_return[page_title] = plain
                        if has_ended:
                            break                      

                    # either way save the id and article
                    title_to_id [page_title] = page_id

                    #reset the values to save
                    page_id = ''
                    page_title = ''
                    page_content = '' 
                    is_redirect = False
                    skip_little=False

                #if a new page begins before one is closed, raise error
                if '<page>' in line :
                    print (page_content)
                    raise Exception('page open before the one before being closed')
            
            ################## IN_TEXT ##################
            elif state == IN_TEXT :
                #update the clean part (without trying to delete the table)
                page_content += line
                
                        
                # if the page ends while in text or on the same line, print  a warning and save the result
                if '</page>' in line :
                    state = OUT_ARTICLE

                    add_current, get_only_ids, get_only_title, has_ended = get_check_only(get_only_ids, get_only_title, page_id, page_title)
                    if not page_id in set_id_already and add_current:

                        plain , skip_little = preprocess_wiki_text(page_content, threshold_skip_little)
                        if skip_little :
                            if what_to_do_result == 'save' :
                                skipped.append(page_id)
                        else :
                            if what_to_do_result == 'save' :
                                writer.writerow([page_id , plain])
                                ids.append(page_id)
                            elif what_to_do_result == 'return_dict_id' :
                                to_return[page_id] = plain
                            elif what_to_do_result == 'return_dict_title' :
                                to_return[page_title] = plain

                    if what_to_do_result == 'save' :
                        title_to_id [page_title] = page_id

                    if has_ended:
                        break

                    page_id = ''
                    page_title = ''
                    page_content = '' 
                    is_redirect = False
                    skip_little=False
                #if we quit the text change state
                elif '</text>' in line :
                    state = IN_ARTICLE 
                #if a new page begins before one is closed, raise error
                if '<page>' in line :
                    print (page_content)
                    raise Exception('page open before the one before being closed')
            
            else :
                raise Exception('state not found')

        if what_to_do_result == 'save' :
            f_out.close()

    if what_to_do_result == 'save' :
        #save the results
        with open(meta_dir+'/title_to_id.json','w' , encoding='utf8') as f :
            json.dump(title_to_id , f)

        id_to_title = {
            _id : title for title , _id in title_to_id.items()
        }
        with open(meta_dir+'/id_to_title.json','w' , encoding='utf8') as f :
            json.dump(id_to_title , f)

        with open(meta_dir+'/redirections.json','w' , encoding='utf8') as f :
            json.dump(redirections , f)
            
        with open(meta_dir+'/skipped.json','w' , encoding='utf8') as f :
            json.dump(skipped , f)

        with open(meta_dir+'/plain_ids.json','w' , encoding='utf8') as f :
            json.dump(ids , f)

    elif what_to_do_result.startswith('return'):
        return to_return

