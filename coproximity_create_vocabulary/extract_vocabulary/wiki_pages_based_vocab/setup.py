def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('wiki_pages_based_vocab', parent_package, top_path)

    config.add_subpackage('get_pages_views')
    config.add_subpackage('word_info')
    return config 

if __name__ == '__main__' :
    from numpy.distutils.core import setup
    setup(configuration=configuration)