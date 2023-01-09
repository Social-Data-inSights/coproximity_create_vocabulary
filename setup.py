from setuptools import setup

setup(
      name='coproximity_create_vocabulary',
      version='0.1',
      description='Wikipedia: allow to download the views of the wikipedia pages and create a vocabulary from them. Contains the structure used for the vocabulary of https://github.com/matthieuDev/Projet_AdE-IMI/. Also allows to get the Wikipedia dumps. ',
      url='https://github.com/matthieuDev/coproximity_create_vocabulary',
      author='MatthieuDev',
      author_email='matthieu.devaux@alumni.epfl.ch',
      license='MIT',
      packages=['coproximity_create_vocabulary'],
      install_requires=['flask', 'spacy', 'requests', 'fasttext', 'mwparserfromhell', 'python-dotenv'],
      zip_safe=False
)