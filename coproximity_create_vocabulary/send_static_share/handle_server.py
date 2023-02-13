'''
Send data to the static share

Warning: requires a valid ssl towards compascience in the .ssl
'''

from scp import SCPClient
from datetime import datetime
import paramiko, os

ssh_args_compascience = {
    'hostname':'84.16.79.220',
    'username':'debian',
}

def connect_ssh_compascience(ssh_args=ssh_args_compascience):
    '''
    Connect to the ssl of compascience

    require a valid ssl towards compascience
    '''
    ssh_connect = paramiko.SSHClient()
    ssh_connect.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_connect.connect(**ssh_args)
    return ssh_connect

def server_create_folder_if_missing(ssh_connect, to_send_folder):
    '''
    Given an ssh connection and a folder path, create the folder if it is missing in the server
    '''
    #create folder on the server if they're missing
    for folder in [to_send_folder] :
        _, _, stderr = \
            ssh_connect.exec_command ('if ! test -d %s; then mkdir %s;  fi' % (folder,folder))
        stderr =stderr.readlines()
        if stderr :
            print('erreur', stderr)

def get_string_date():
    #date string to add to the server filename 
    now = datetime.now()
    return '%02d%02d%02d'%(now.year,now.month,now.day)

def send_vocab_to_server(language_folder, to_send_folder, ssh_args=ssh_args_compascience) :
    '''
    From a language folder {language_folder}, get the main vocabulary and the meta folder, zip them and send them to the compascience static share
    in the folder {to_send_folder}

    The main vocabulary is considered the one made with a lexicon of size 1e5, with uppercase and accents
    The meta folder contains the list of articles sorted by views and the synonyms, those 2 files but with their processed (with the default methods) titles.
        Also contains the dictionary {wiki id: id title}
    
    ssh_args: arguments to give to the paramiko.SSHClient
    '''
    ssh_connect = connect_ssh_compascience(ssh_args)
    server_create_folder_if_missing(ssh_connect, to_send_folder)
    string_date = get_string_date()

    # send the files
    scp = SCPClient(ssh_connect.get_transport())
    for from_local_file, to_server_file in [
        ('main_vocab.zip', f'main_vocab-{string_date}.zip'),
        ('meta.zip', f'meta-{string_date}.zip'),
    ]:
        scp.put(language_folder + from_local_file, to_send_folder + to_server_file)
        latest_file = to_server_file.replace(string_date, "latest")
        ssh_connect.exec_command(f'cd {to_send_folder}; rm {latest_file}; ln -s {to_server_file} {latest_file}')

def send_wiki_plain_to_server(wiki_plain_folder, to_send_folder, ssh_args=ssh_args_compascience) :
    '''
    Given a folder containing the plain wikipedia folder {wiki_plain_folder} and a path {to_send_folder} to send them in a server, upload the main Wikipedia plain dump on the server.
    
    ssh_args: arguments to give to the paramiko.SSHClient
    '''
    ssh_connect = connect_ssh_compascience(ssh_args)
    server_create_folder_if_missing(ssh_connect, to_send_folder)
    string_date = get_string_date()

    scp = SCPClient(ssh_connect.get_transport())
    for from_local_file in os.listdir(wiki_plain_folder) :
        #if from_local_file.startswith('best_avg_') and from_local_file.endswith('.zip'):
        if from_local_file== 'best_avg_100.zip' :
            *filename_base, filename_extension = from_local_file.split('.')
            to_server_file = f"{'.'.join(filename_base)}-{string_date}.{filename_extension}"

            scp.put(wiki_plain_folder + from_local_file, to_send_folder + to_server_file)
            latest_file = to_server_file.replace(string_date, "latest")
            ssh_connect.exec_command(f'cd {to_send_folder}; rm {latest_file}; ln -s {to_server_file} {latest_file}')