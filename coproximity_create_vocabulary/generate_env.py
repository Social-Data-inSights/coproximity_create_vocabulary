'''
File to generate .env based. Needs to give both the base folder with base_vocab_folder and the allowed download projects with allowed_download_projects.
If a .env already exists, it is used to give default values if one of the 2 arguments are missing. Otherwise, if 1 argument is missing, an error will be raised.

Example :
python generate_env.py --base_vocab_folder E:/UNIL/backend/data/whole/vocabulary/ --allowed_download_projects fr_en_it_de
'''

from coproximity_create_vocabulary.data_conf import base_vocab_folder, set_allowed_download_projects

import os
from pathlib import Path

env_file = str(Path(__file__).parent.absolute().resolve()) + '/.env'
with open(env_file, 'w', encoding='utf8') as f :
    f.write(f"base_vocab_folder = '{base_vocab_folder}'\nset_allowed_download_projects = '{b'_'.join(set_allowed_download_projects).decode('utf8')}'\n")