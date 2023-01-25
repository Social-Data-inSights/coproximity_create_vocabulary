'''
Send data to the static share

Warning: requires a valid ssl towards compascience in the .ssl
'''

from scp import SCPClient
from datetime import datetime
import paramiko

ssh_args_compascience = {
    'hostname':'84.16.79.220',
    'username':'debian',
}

def send_to_server(language_folder, to_send_folder, ssh_args=ssh_args_compascience) :
    '''
    From a language folder {language_folder}, get the main vocabulary and the meta folder, zip them and send them to the compascience static share
    in the folder {to_send_folder}

    The main vocabulary is considered the one made with a lexicon of size 1e5, with uppercase and accents
    The meta folder contains the list of articles sorted by views and the synonyms, those 2 files but with their processed (with the default methods) titles.
        Also contains the dictionary {wiki id: id title}
    
    ssh_args: arguments to give to the paramiko.SSHClient
    '''
    #connect to ssl
    #require a valid ssl towards compascience
    p = paramiko.SSHClient()
    p.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    p.connect(**ssh_args)

    #create folder on the server if they're missing
    for folder in [to_send_folder] :
        _, _, stderr = \
            p.exec_command ('if ! test -d %s; then mkdir %s;  fi' % (folder,folder))
        stderr =stderr.readlines()
        if stderr :
            print('erreur', stderr)

    #date string to add to the server filename 
    now = datetime.now()
    string_date = '%02d%02d%02d'%(now.year,now.month,now.day)

    # send the files
    scp = SCPClient(p.get_transport())
    for from_local_file, to_server_file in [
        ('main_vocab.zip', f'main_vocab-{string_date}.zip'),
        ('meta.zip', f'meta-{string_date}.zip'),
    ]:
        scp.put(language_folder + from_local_file, to_send_folder + to_server_file)
        latest_file = to_server_file.replace(string_date, "latest")
        p.exec_command(f'cd {to_send_folder}; rm {latest_file}; ln -s {to_server_file} {latest_file}')
