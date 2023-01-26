'''
create the zip to send to the static share
'''

import shutil, os
from coproximity_create_vocabulary.data_conf import base_vocab_folder

def zip_vocab(language_folder):
    '''
    create the zips to send to the static share for the language whose language folder is {language_folder}
    '''
    shutil.make_archive(language_folder + 'meta', 'zip', language_folder + 'meta')
    shutil.make_archive(language_folder + 'main_vocab', 'zip', language_folder + 'ngram_title_wiki/wiki_title_best_100000/')

def zip_wiki_plains(wiki_plain_folder):
    for from_local_file in os.listdir(wiki_plain_folder) :
        if from_local_file.startswith('best_avg_'):
            *filename_base, _ = from_local_file.split('.')
            filename_base = '.'.join(filename_base)

            shutil.make_archive(wiki_plain_folder + filename_base, 'zip', wiki_plain_folder, from_local_file)

if __name__ == '__main__' :
    zip_vocab(base_vocab_folder + 'french/')
    zip_wiki_plains(base_vocab_folder + 'extracted_wikipedia/french/')