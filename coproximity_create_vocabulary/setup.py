def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('create_vocab', parent_package, top_path)

    config.add_subpackage('analysis')
    config.add_subpackage('basic_method')
    config.add_subpackage('wiki_pages_based_vocab')
    config.add_subpackage('wordpiece_ngrams')
    return config 

if __name__ == '__main__' :
    from numpy.distutils.core import setup
    setup(configuration=configuration)