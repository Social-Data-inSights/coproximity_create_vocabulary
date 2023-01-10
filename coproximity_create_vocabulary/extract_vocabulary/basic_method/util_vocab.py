'''
Useful methods for creating the vocabulary
'''
import string , spacy, requests, unicodedata
#delete accents 
delete_accent = lambda s : ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def delete_accent_on_first_if_upper(text) :
    '''
    Given a text, if the first letter is upper case and has an accent, delete the accent on this 1st letter.
    '''
    if not text or text[0].islower() :
        return text
    return f"{delete_accent(text[0])}{text[1:]}"

def hyphen_in_1word (text) :
    '''
    transform all [.., 'w1', '-', 'w2', ...] into [.., 'w1-w2', ...]
    '''
    if not text :
        return []

    punctuation = set(string.punctuation + '\n')
    prev = text[0]
    prev_hyphen = False
    new_text = []
    for word in text[1:] :
        if word == '-' and not prev is None and not prev in punctuation :
            prev_hyphen = True
        elif prev_hyphen :
            if not word in punctuation :
                prev = f'{prev}-{word}'
            else :
                new_text.append(prev)
                new_text.append('-')
                prev = word
            prev_hyphen = False
        else :
            new_text.append(prev)
            prev = word
 
    
    if prev_hyphen :
        new_text.append(prev+'-')
    else :
        new_text.append(prev)
    return new_text


def tuple_hyphen_in_1word (text) :
    '''
    transform all [.., ('w11', 'w12'), ('-', '-'), ('w21', 'w22'), ...] into [.., ('w11-w21', 'w12-w22'), ...]
    '''
    if not text :
        return []

    punctuation = set(string.punctuation + '\n')
    prev = text[0]
    prev_hyphen = False
    new_text = []
    for processed, base in text[1:] :
        if processed == '-' and base == '-' and not prev is None and not prev in punctuation :
            prev_hyphen = True
        elif prev_hyphen :
            if not processed in punctuation :
                prev = (f'{prev[0]}-{processed}', f'{prev[1]}-{base}')
            else :
                new_text.append(prev)
                new_text.append(('-', '-'))
                prev = (processed, base)
            prev_hyphen = False
        else :
            new_text.append(prev)
            prev = (processed, base)
 
    
    if prev_hyphen :
        new_text.append(prev)
        new_text.append(('-', '-'))
    else :
        new_text.append(prev)
    return new_text

def get_tuple_tokenize_text_spacy (to_load, disable_tag=['tagger', 'parser', 'ner'], use_lower=False, use_no_accent=False) :
    """
    Used for the word tokenization, load a lemmatizer and return a method that takes a string 
    and return a list of tuples(processed words, non-processed words).

    to_load: spacy model to load
    disable_tag: disable_tag to give to spacy
    use_lower: if true, set all non acronyms (words with only uppercase) as lowercase
    use_no_accent: if true, delete all accents
    """
    nlp = spacy.load(to_load, disable = disable_tag)
    #tuple_hyphen_in_1word is used so that the words with "-" are not split around it.
    # if the word is only made of uppercase, it's an acronym so don't lematize
    if not use_lower and not use_no_accent :
        processed_method = lambda text : tuple_hyphen_in_1word([(w.text.strip() if w.text.isupper() else w.lemma_.strip(), w.text.strip(),) for w in nlp(text) if w.lemma_.strip()])
    elif not use_lower and use_no_accent :
        processed_method = lambda text : tuple_hyphen_in_1word([(w.text.strip() if w.text.isupper() else delete_accent(w.lemma_.strip()), w.text.strip(),) for w in nlp(text) if w.lemma_.strip()])
    elif use_lower and not use_no_accent :
        processed_method = lambda text : tuple_hyphen_in_1word([(w.text.strip() if w.text.isupper() else w.lemma_.strip().lower(), w.text.strip(),) for w in nlp(text) if w.lemma_.strip()])
    elif use_lower and use_no_accent :
        processed_method = lambda text : tuple_hyphen_in_1word([(w.text.strip() if w.text.isupper() else delete_accent(w.lemma_.strip().lower()), w.text.strip(),) for w in nlp(text) if w.lemma_.strip()])

    return processed_method

def get_lemmatize_text_spacy (to_load, disable_tag=['tagger', 'parser', 'ner'], use_lower=False, use_no_accent=False) :
    """
    Used for the word tokenization, load a lemmatiser and return a method that takes a string 
    and return a list of processed words

    to_load: spacy model to load
    disable_tag: disable_tag to give to spacy
    use_lower: if true, set all non acronyms (words with only uppercase) as lowercase
    use_no_accent: if true, delete all accents
    """
    nlp = spacy.load(to_load, disable = disable_tag)
    #hyphen_in_1word is used so that the words with "-" are not split around it. if the word is only made of uppercase, it's an acronym so don't lemmatize
    if not use_lower and not use_no_accent :
        processed_method = lambda text : ' '.join(hyphen_in_1word([w.text.strip() if w.text.isupper() else w.lemma_.strip() for w in nlp(text) if w.lemma_.strip()]))
    elif not use_lower and use_no_accent :
        processed_method = lambda text : ' '.join(hyphen_in_1word([w.text.strip() if w.text.isupper() else delete_accent(w.lemma_.strip()) for w in nlp(text) if w.lemma_.strip()]))
    elif use_lower and not use_no_accent :
        processed_method = lambda text : ' '.join(hyphen_in_1word([w.text.strip() if w.text.isupper() else w.lemma_.strip().lower() for w in nlp(text) if w.lemma_.strip()]))
    elif use_lower and use_no_accent :
        processed_method = lambda text : ' '.join(hyphen_in_1word([w.text.strip() if w.text.isupper() else delete_accent(w.lemma_.strip().lower()) for w in nlp(text) if w.lemma_.strip()]))
    
    return processed_method

def download_page(page_file, url ) :
    '''
    Download an internet page at {url} and save it in file {page_file}
    '''
    dump = requests.get(url, stream=True)
    with open(page_file, 'wb') as f :
        for chunk in dump.raw.stream(1024 * 1024 * 100, decode_content=False):
            if chunk:
                f.write(chunk)

if __name__ == '__main__' :
    #test delete_accent_on_first_if_upper
    for text, good_res in [
        ['être', 'être'],
        ['ou', 'ou'],
        ['Ne', 'Ne'],
        ['pas', 'pas'],
        ['Être', 'Etre'],
        ['ça', 'ça'],
        ['Ça', 'Ca'],
        ['élan', 'élan'],
        ['Élan', 'Elan']
    ] :
        assert delete_accent_on_first_if_upper(text) == good_res, f'res: "{delete_accent_on_first_if_upper(text)}", should be : "{good_res}"'
    print('pass test delete_accent_on_first_if_upper')