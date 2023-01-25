import os
from setuptools import setup, find_packages

def recursive_get_sub_packages(path):
    res = []
    for folder in os.listdir(path):
        rec_path = f'{path}{folder}/'
        if os.path.isdir(rec_path) and folder != '__pycache__' and not folder.startswith('.') :
            res.append(rec_path.replace('/', '.').strip('.'))
            res.extend(recursive_get_sub_packages(rec_path))
    return res

setup(
      name='coproximity_create_vocabulary',
      version='0.1',
      description='Wikipedia: allow to download the views of the wikipedia pages and create a vocabulary from them. Contains the structure used for the vocabulary of https://github.com/matthieuDev/Projet_AdE-IMI/. Also allows to get the Wikipedia dumps. ',
      url='https://github.com/matthieuDev/coproximity_create_vocabulary',
      author='MatthieuDev',
      author_email='matthieu.devaux@alumni.epfl.ch',
      license='MIT',
      packages=['coproximity_create_vocabulary'] + recursive_get_sub_packages('coproximity_create_vocabulary/'),
      install_requires=['flask', 'spacy', 'requests', 'fasttext', 'mwparserfromhell', 'python-dotenv', 'scp', 'beautifulsoup4'],
      zip_safe=False
)