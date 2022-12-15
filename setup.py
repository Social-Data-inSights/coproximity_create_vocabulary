from setuptools import setup

setup(
      name='coproximity_create_vocabulary',
      version='0.1',
      description='The funniest joke in the world',
      url='http://github.com/storborg/funniest',
      author='MatthieuDev',
      author_email='matthieu.devaux@alumni.epfl.ch',
      license='MIT',
      packages=['coproximity_create_vocabulary'],
      install_requires=['flask', 'spacy', 'requests', 'fasttext', 'mwparserfromhell'],
      zip_safe=False
)