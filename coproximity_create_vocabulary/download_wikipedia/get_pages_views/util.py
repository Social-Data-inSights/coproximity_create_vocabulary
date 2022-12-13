

import requests

def download_page(page_file, url ) :
    '''
    Download an internet page at {url} and save it in file {page_file}
    '''
    dump = requests.get(url, stream=True)
    with open(page_file, 'wb') as f :
        for chunk in dump.raw.stream(1024 * 1024 * 100, decode_content=False):
            if chunk:
                f.write(chunk)