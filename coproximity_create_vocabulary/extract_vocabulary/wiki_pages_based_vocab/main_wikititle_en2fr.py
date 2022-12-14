'''
Get the vocabulary that takes the vocabulary and synonyms from the best english pages and their redirections. 
And link them to a translation to the french Wikipedia
'''
import os, json, csv, pickle, gzip
from shutil import copyfile
from coproximity_create_vocabulary.data_conf import base_vocab_folder

from coproximity_create_vocabulary.extract_vocabulary.basic_method.auto_reader_writer import auto_reader

from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.wiki_title import factory_create_title_wiki, create_translate_title2text_id_factory
from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.get_args import get_english_var, get_processed_file, get_preprocess_args
from coproximity_create_vocabulary.extract_vocabulary.wiki_pages_based_vocab.util_wiki import unwikititle

from coproximity_create_vocabulary.extract_vocabulary.basic_method.create_ngram import create_ngram_framework
from coproximity_create_vocabulary.extract_vocabulary.basic_method.util_vocab import download_page

n_best_taken = int(1e5)

def get_translate_from_dump(from_, to_, save_file, translate_folder, from_id2title_file):
    '''
    Get the the associated wikipedia pages between 2 language. i.e. if we have en and fr, get all the pages which can are the same but just
    switching project. Save the result in {save_file}

    from_: project from which to search the page to translate
    to_: project toward  which to search the page to translate
    save_file: file in which the result is saved
    translate_folder: folder in which the langlinks will be saved
    from_id2title_file: json of a dict {wikipedia id: wikipedia title} of the {from_} project
    '''
    if not os.path.exists(save_file):
        prj2url_langlinks = lambda prj: f'https://dumps.wikimedia.org/{prj}wiki/latest/{prj}wiki-latest-langlinks.sql.gz'
        prj2langlinks_file = lambda prj: translate_folder + f'{prj}wiki-latest-langlinks.sql.gz'

        for project in (from_, to_) :
            if not os.path.exists(prj2langlinks_file(project)) :
                download_page(prj2langlinks_file(project), prj2url_langlinks(project),)

        with open(from_id2title_file, encoding='utf8') as f :
            from_id2title = json.load(f)

        translate = []
        with gzip.open(prj2langlinks_file(from_)) as f  :
            for line in f :
                if line.startswith(b'INSERT INTO `langlinks` VALUES') :
                    split_insert = [x.strip('(') for x in line.decode('utf8', errors="ignore").strip(');\n)').split('VALUES ')[1].split('),(')]
                    for vals in csv.reader(split_insert, delimiter=',', quotechar="'", escapechar ='\\') :
                        if vals[1] == to_ and vals[2]:
                            if vals[0] in from_id2title :
                                translate.append((from_id2title[vals[0]], vals[2]))

        with open(save_file, 'w') as f :
            json.dump(translate, f)
    else :
        with open(save_file) as f :
            translate = json.load(f)
    return translate

n_best_taken = int(1e5)

_ , _, _, _, _, _, spacy_model, disable_tag = get_english_var()

whole_vocab_folder = base_vocab_folder + 'whole/vocabulary/'
whole_folder :str = base_vocab_folder + '/whole/vocabulary/english/'
translate_folder = whole_vocab_folder+'translate/'
vocab_parent_folder = base_vocab_folder + '/whole/vocabulary/english/ngram_title_wiki/'

fr_id2title_file = whole_vocab_folder + 'french/meta/id2title.json'
en_id2title_file = whole_vocab_folder + 'english/meta/id2title.json'

vocab_folder = whole_vocab_folder+'english/ngram_title_wiki/wiki_title_fr_in_en_%s/'%('whole' if n_best_taken is None else 'best_%d'%n_best_taken)

synonyms_file = whole_folder + 'meta/synonyms.csv'
processed_syn_file = get_processed_file(synonyms_file, spacy_model, disable_tag, 'csv')
article_list_file=  base_vocab_folder + '/whole/vocabulary/english/meta/sorted_view_wiki_over_years.csv'
processed_article_file = get_processed_file(article_list_file, spacy_model, disable_tag, 'csv')

french_set_articles_file = base_vocab_folder + 'whole/vocabulary/french/ngram_title_wiki/wiki_title_best_100000/set_tokens.json'

wiki_title_fr_folder = whole_vocab_folder + 'french/ngram_title_wiki/wiki_title_best_100000/'
wiki_title_en_folder = whole_vocab_folder + 'english/ngram_title_wiki/wiki_title_best_100000/'

for folder in [whole_vocab_folder, translate_folder, vocab_folder] :
    if not os.path.exists(folder) :
        os.mkdir(folder)

stop_words , duplicate_stop_words, processed_method, synonym_to_ignore, _, _, _, _ = get_english_var()
synonym_to_ignore.add(('How Fly', 'Wiz Khalifa'))
synonym_to_ignore.add(('Grow Season', 'Wiz Khalifa'))
synonym_to_ignore.add(('Future changes', 'Yu-Gi-Oh! GX'))
synonym_to_ignore.add(('Job.', 'Book of Job'))
synonym_to_ignore.add(('Unveiling ceremony', 'Bereavement in Judaism'))
synonym_to_ignore.add(('Unveiling', 'Bereavement in Judaism'))
synonym_to_ignore.add(('A record', 'List of DNS record types'))

def wikititle_en2fr (use_lower_processed = False, use_no_accent_processed = False) :
    '''
    Create the method to feed to create_ngram_framework
    '''
    #get the vocabulary by getting all the articles from the french and english projects which can be linked to an article of the other set
    en2fr = {
        en.replace('_', ' ') : fr.replace('_', ' ') 
        for en, fr in get_translate_from_dump('en', 'fr', translate_folder + 'en2fr.json', translate_folder, en_id2title_file)
    }
    fr2en = {
        fr.replace('_', ' ') : en.replace('_', ' ')
        for fr, en in get_translate_from_dump('fr', 'en', translate_folder + 'fr2en.json', translate_folder, fr_id2title_file)
    } 

    with open(wiki_title_fr_folder + 'set_tokens.json', encoding='utf8') as f :
        set_articles_fr = set(json.load(f))
        
    with open(wiki_title_en_folder + 'set_tokens.json', encoding='utf8') as f :
        set_articles_en = set(json.load(f))
        
    good_en2fr = { en : fr for en, fr in en2fr.items() if en in set_articles_en and fr in set_articles_fr}
    good_fr2en = { fr : en for fr, en in fr2en.items() if en in set_articles_en and fr in set_articles_fr} 

    clean_en2clean_fr = dict(set(good_en2fr.items()).intersection({(en, fr) for fr, en in good_fr2en.items()}))

    #get the processed and clean version of the ngrams of the vocab
    processed_dict = {}
    article_views = []
    set_tokens = set()

    name_processed_version = f"{spacy_model}{'_lower' if use_lower_processed else ''}{'_no_accent' if use_no_accent_processed else ''}"
    csv_reader = auto_reader(processed_article_file, list_select=['main', 'clean_main', name_processed_version, 'count'], csv_args = dict(delimiter=';', quotechar='"') )
    for i,(title, clean_title, processed_title, views) in enumerate(csv_reader) :
        if title in clean_en2clean_fr :
            processed_dict[unwikititle(clean_title)] = processed_dict[clean_title] = processed_title

            #add the article to the list and set, write the homonym equivalent(if the title is not an homonym, dictionary just return itself), and add 1 to the count 
            article_views += [(clean_title)]
            set_tokens.add(clean_title)
    csv_reader.close()

    def create_title_en2fr (*args) :
        return set_tokens, processed_dict, []

    en2fr = dict(en2fr)
    def post_process_en2fr () :
        '''
        apply the article translation while keeping the english version. In this method we ignore the synonyms which link to multiple article.
        '''
        
        with open (vocab_folder+'main_dict_vocab.json') as f :
            main_dict_vocab = json.load(f)
            
        with open (vocab_folder+'main_dict_vocab_en.json', 'w') as f :
            json.dump(main_dict_vocab, f)
            
        main_dict_vocab = {
            syn: (lem_syn, clean_en2clean_fr[title] if title else clean_en2clean_fr[syn], igram)
            for syn, (lem_syn, title, igram) in main_dict_vocab.items()
        }

        with open (vocab_folder+'main_dict_vocab.json', 'w') as f :
            json.dump(main_dict_vocab, f)

        copyfile(vocab_folder + 'set_tokens.json', vocab_folder + 'set_articles_en.json')
        with open (vocab_folder+'set_tokens.json', 'w') as f :
            json.dump(list(set_tokens), f)

        with open(vocab_folder+ 'multiple_vecs.pkl', 'wb') as f :
            pickle.dump({}, f)

    return create_title_en2fr, post_process_en2fr

if __name__ == '__main__' :
    use_lower_processed, use_no_accent_processed = False, False

    create_title_en2fr, post_process_en2fr = wikititle_en2fr ()

    processed_list_select, processed_method_list, preprocessed_apply_rewikititle_on_lem_list = get_preprocess_args(spacy_model, disable_tag=['parser', 'ner'])
    translate_token2text_id = create_translate_title2text_id_factory(
        base_vocab_folder + '/wikipedia/whole/meta_wiki/title_to_id.json',
        base_vocab_folder + '/wikipedia/best_avg_250.000.json',
    )
    plain_article_title_reader = auto_reader(article_list_file, csv_args = dict(delimiter=';', quotechar='"'))
    plain_synonyms_reader = auto_reader(synonyms_file, csv_args = dict(delimiter=';', quotechar='"'))

    preprocess_wiki, _, en_create_synonyms, en_process_all, _ = factory_create_title_wiki (
        stop_words , 
        duplicate_stop_words,
        processed_list_select, processed_method_list, preprocessed_apply_rewikititle_on_lem_list,
        processed_method,
        synonym_to_ignore,
        whole_folder, 
        n_best_taken, 
        vocab_folder,
        plain_article_title_reader,
        processed_article_file,
        plain_synonyms_reader, 
        processed_syn_file,
        whole_folder + 'cc.en.300.bin',
        'en',
        apply_rewikititle_on_lem= not use_lower_processed,
        func_get_title_factory=translate_token2text_id,
        use_id_to_title=False,
        overwrite=False,
        is_printing_progress=True,
    )

    new_str = f"{'_lower' if use_lower_processed else ''}{'_no_accent' if use_no_accent_processed else ''}"
    name_processed_version = f'{spacy_model}{new_str}'
    article_title_reader = auto_reader(processed_article_file, list_select=['main', 'clean_main', name_processed_version, 'count'], csv_args = dict(delimiter=';', quotechar='"'))
    synonyms_reader = auto_reader(processed_syn_file, list_select=['syn_from', name_processed_version, 'syn_to'], csv_args = dict(delimiter=';', quotechar='"'))

    create_ngram_framework (
        vocab_parent_folder,
        vocab_folder,
        preprocess_wiki,
        create_title_en2fr ,
        en_create_synonyms ,
        en_process_all,
        post_process_en2fr,
        article_title_reader,
        synonyms_reader,
        [],
        {},
        is_printing_progress=True,
    )
