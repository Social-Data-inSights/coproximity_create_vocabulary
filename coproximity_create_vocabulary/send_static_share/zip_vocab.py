'''
TODOC
'''

import shutil
from coproximity_create_vocabulary.data_conf import base_vocab_folder

def zip_vocab(language_folder):
    shutil.make_archive(language_folder + 'meta', 'zip', language_folder + 'meta')
    shutil.make_archive(language_folder + 'main_vocab', 'zip', language_folder + 'ngram_title_wiki/wiki_title_best_100000/')

if __name__ == '__main__' :
    zip_vocab(base_vocab_folder + 'french/')