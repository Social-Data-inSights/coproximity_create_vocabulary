'''
data configuration file. Give variables that should be easily accessible and static over multiple sessions, but that can be change by the user. There are 2:

- base_vocab_folder: The folder in which all the folder and files will be generated/downloaded/saved.

- set_allowed_download_projects: The set of all projects that will be considered for this usage. It is mostly used to know which project to keep in the count dumps (to use less space). If you want to add a project that was not in the .env, you need to add it, delete all the count from the {base folder}/dumps folder and re run the main. The format of this variable should be a string of all desired projects separated by '_'. i.e. if we want english, german, italian and french, we give it : en_de_it_fr 
'''
import os, coproximity_create_vocabulary, argparse
from pathlib import Path

env_file = str(Path(__file__).parent.absolute().resolve()) + '/.env'

#charge the data folder path and the allowed projects from the .env file
if os.path.exists(env_file) :
    from dotenv import load_dotenv
    load_dotenv(env_file)


parser = argparse.ArgumentParser()
parser.add_argument('--parent_folder_init', default=None,  help = 'The folder in which all the folder and files will be generated/downloaded/saved.')
parser.add_argument('--allowed_download_projects', default=None,  help = "The set of all projects that will be considered for this usage. It is mostly used to know which project to keep in the count dumps (to use less space). If you want to add a project that was not in the .env, you need to add it, delete all the count from the {base folder}/dumps folder and re run the main. The format of this variable should be a string of all desired projects separated by '_'. i.e. if we want english, german, italian and french, we give it : en_de_it_fr")
args, unknown = parser.parse_known_args()

#try to get the base vocab folder from the arguments, if it can't load it from the .env
if args.parent_folder_init :
    parent_folder_init = args.parent_folder_init
else :
    parent_folder_init = os.environ.get('parent_folder_init')

assert not parent_folder_init is None, 'set the data folder, either in the data_conf folder or  by adding a --parent_folder_init argument'

#try to get the allowed projects from the arguments, if it can't load it from the .env
if args.allowed_download_projects :
    set_allowed_download_projects = { project.encode('utf8') for project in args.allowed_download_projects.split('_') }
else :
    set_allowed_download_projects = { project.encode('utf8') for project in os.environ.get('set_allowed_download_projects').split('_') }

base_module = os.path.relpath((coproximity_create_vocabulary.__path__)._path[0]).replace('\\', '/') + '/'
if os.path.isabs(parent_folder_init) :
    base_vocab_folder = parent_folder_init
    abs_base_vocab_folder = parent_folder_init
else :
   base_vocab_folder = os.path.relpath((coproximity_create_vocabulary.__path__)._path[0]).replace('\\', '/') + '/' + parent_folder_init
   abs_base_vocab_folder = os.path.dirname(__file__).replace('\\', '/') + '/' + parent_folder_init

