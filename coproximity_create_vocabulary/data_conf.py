'''
data configuration file. Give the base of the data folder (relative path (if given) and absolute path) and of the html folder.
'''
import os, coproximity_create_vocabulary, argparse

parser = argparse.ArgumentParser()
parser.add_argument('--parent_folder_init', default=None,  help = 'parent_folder_init')
args, unknown = parser.parse_known_args()

if args.parent_folder_init :
    parent_folder_init = args.parent_folder_init
else :
    parent_folder_init = None #change data folder path here
assert not parent_folder_init is None, 'set the data folder, either in the data_conf folder or  by adding a --parent_folder_init argument'

base_module = os.path.relpath((coproximity_create_vocabulary.__path__)._path[0]).replace('\\', '/') + '/'
if os.path.isabs(parent_folder_init) :
    base_vocab_folder = parent_folder_init
    abs_base_vocab_folder = parent_folder_init
else :
   base_vocab_folder = os.path.relpath((coproximity_create_vocabulary.__path__)._path[0]).replace('\\', '/') + '/' + parent_folder_init
   abs_base_vocab_folder = os.path.dirname(__file__).replace('\\', '/') + '/' + parent_folder_init

if args.conf_folder :
    base_conf_folder = args.conf_folder
else :
    base_conf_folder = base_module + 'imi_backend/html/conf_folder/'
