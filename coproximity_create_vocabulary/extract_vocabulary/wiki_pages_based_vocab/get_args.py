'''
Get the variables to filter: 
    -stop words: the ngram to ignore
    -duplicate stop words: see duplicate stop words for its use
    -method to processed the ngrams
    -the synonyms to ignore
    -If needed some new vocabulary to add, independently of the ngrams to extract
    -If needed some new synonym to add, independently of the ngrams to extract.

duplicate stop words : let's say we have 2 ngrams whose only difference is that one has one mor word w0 at the beginning 
(2 ngrams : "w1 w2 .. wn" , "w0 w1 w2 .. wn") if w0 is a duplicate stop words, we consider that the 2 are called duplicates.
'''
import string, unicodedata
from coproximity_create_vocabulary.extract_vocabulary.basic_method.util_vocab import get_lemmatize_text_spacy



delete_accent = lambda s : ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
def get_french_var (use_lower_processed=False, use_no_accent_processed=False) :
    '''
    Get the french variables

    use_lower_processed: if true, the processing sets the result as lowercase (except for acronyms (words with only uppercase))
    use_no_accent_processed: if true, the processing deletes the accents
    '''
    synonym_to_ignore = {
        ('Cites', "Convention sur le commerce international des espèces de faune et de flore sauvages menacées d'extinction" ),
        ('Eruptif', "Liste des créatures du monde des sorciers de J. K. Rowling" ),
        ('Éruptif', "Liste des créatures du monde des sorciers de J. K. Rowling" ),
        ('Imaginer', "Carte Imagine'R"),
        ('Futur Antérieur', 'Futur antérieur en français'), 
        ('Futur anterieur', 'Futur antérieur en français'), 
        ('Futur antérieur', 'Futur antérieur en français'), 
        ('Futur antérieur en français', 'Futur antérieur en français'), 
        ('futur Antérieur', 'Futur antérieur en français'), 
        ('futur anterieur', 'Futur antérieur en français'), 
        ('futur antérieur', 'Futur antérieur en français'),
        ('Henri de', 'Henri Dès'),
        ('Henri des', 'Henri Dès'),
        ('5S', '5'),
        ('L5', '5'),
        ('Imparfait', 'Imparfait de l\'indicatif en français'),
        ('Réformateur', 'François-Vincent Raspail'),
        ('Envers', 'Ubac'),
    }
    #stop words for duplicate
    duplicate_stop_words = 'un des le les la une l à de'.split(' ')
    #stop words for homonyms
    stop_words = set(
        duplicate_stop_words 
        + 'je tu il nous vous ils elle elles on son sa ses ça ca ces ce pas lui pas mon ma mes si ni ne de à ou où cela car'.split(' ') 
        + [x for x in string.ascii_lowercase] 
        #word present in more than half of wikipédia's articles
        + 'être avoir aller voir de et la le en est l à d du un des les une dans catégorie par au pour références qui sur a il avec son que s notes plus se ou ce aux aussi sa sont qu liens comme externes deux été cette ses mais pas n elle fait après entre ne c sous même'.split(' ') 
        #word present in more than half of wikipédia's articles if we lemmatize the words
        + 'ce avoir premier personne pouvoir aller je savoir notre faire aussi mettre comprendre jour bien croire cas nouveau connaître petit bon parler oui pense compte année différent façon'.split(' ')
    )
    duplicate_stop_words = set(duplicate_stop_words)

    if use_no_accent_processed :
        stop_words.add('étant')

    spacy_model = 'fr_core_news_lg'
    disable_tag=['tagger', 'parser', 'ner']
    processed_method = get_lemmatize_text_spacy(spacy_model, disable_tag=disable_tag, use_lower = use_lower_processed, use_no_accent = use_no_accent_processed)

    word_to_add = []
    synonym_to_add = {}

    return stop_words , duplicate_stop_words, processed_method, synonym_to_ignore, word_to_add, synonym_to_add, spacy_model, disable_tag

def get_preprocess_args (spacy_model, disable_tag=['tagger', 'parser', 'ner']) :
    '''
    Get the processed method to give to preprocessed function of the vocabulary creation. Given  a spacy model name {spacy_model} and a list of tag to ignore {disable_tag}
    use it to load a lemmatizer and return the lemmatized with and without casting as lowercase and with and without accent (=4 results in total)
    '''
    lemmed_list_select = [
        f"{spacy_model}{'_lower' if use_lower_processed else ''}{'_no_accent' if use_no_accent_processed else ''}"
        for use_lower_processed in [False, True] for use_no_accent_processed in [False, True]
    ]
    processed_method = get_lemmatize_text_spacy(spacy_model, disable_tag=disable_tag, use_lower = False, use_no_accent = False)
    def processed_method_list(s):
        lemmed = processed_method(s)
        lemmed_split = lemmed.split(' ')
        lemmed_lower_split = [w if w.isupper() else w.strip().lower() for w in lemmed_split ]
        lemmed_lower_no_accent_split = [w if w.isupper() else delete_accent(w.strip()) for w in lemmed_lower_split ]
        lemmed_no_accent_split = [w if w.isupper() else delete_accent(w.strip()) for w in lemmed_split ]

        return lemmed, ' '.join(lemmed_no_accent_split), ' '.join(lemmed_lower_split), ' '.join(lemmed_lower_no_accent_split)

    return lemmed_list_select, processed_method_list, [True, True, False, False]

def get_english_var (use_lower_processed=False, use_no_accent_processed=False) :
    '''
    Get the english variables  
    '''
    synonym_to_ignore = {('A records', 'List of DNS record types')}
    #stop words for duplicate
    duplicate_stop_words = 'a the of my'.split(' ')
    #stop words for homonyms
    stop_words = set(
        duplicate_stop_words 
        + 'she he him her i you them their your we us our his'.split(' ') 
        + 'in and use to project it research well have be'.split(' ')
        + [x for x in string.ascii_lowercase] 
    )
    duplicate_stop_words = set(duplicate_stop_words)

    spacy_model = 'en_core_web_lg'
    disable_tag=['parser', 'ner']
    processed_method = get_lemmatize_text_spacy(spacy_model, disable_tag=disable_tag, use_lower = use_lower_processed, use_no_accent = use_no_accent_processed)

    return stop_words , duplicate_stop_words, processed_method, synonym_to_ignore, [] , {}, spacy_model, disable_tag

def get_processed_file(filepath, spacy_model, disable_tag, new_extension='csv') :
    '''
    Given the path to a file {filepath}, return a stereotyped new path file that will contains the processed content of the {filepath}
    spacy_model: name of a spacy model
    disable_tag: the list of tag to disable for the spacy model
    new_extension: new extension to give to the file
    '''
    to_add_to_processed = f"{spacy_model}_{''.join([tag[0] for tag in sorted(disable_tag)])}"
    *path, extension = filepath.split('.')
    return f"{'.'.join(path)}_{to_add_to_processed}.{new_extension if new_extension else extension}"

var_getter_by_project = {
    'fr': get_french_var,
    'en': get_english_var,
}