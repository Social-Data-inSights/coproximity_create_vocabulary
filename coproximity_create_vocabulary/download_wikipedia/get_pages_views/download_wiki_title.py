'''
Download the pageviews by article (by default start the count in January 2016)

Pageviews from 2015 : https://dumps.wikimedia.org/other/pageview_complete/ 
'''
import json, os, bz2, csv
from datetime import datetime

from multiprocessing import Pool
from collections import Counter

from coproximity_create_vocabulary.extract_vocabulary.basic_method.util_vocab import download_page

from coproximity_create_vocabulary.data_conf import base_vocab_folder, set_allowed_download_projects

class iter_month :
    '''
    Create an iterator of a tuple representing: (year, month) that return the result month by month, between the {start} and {end} of the __init__.

    Ex: if we are given start = (2017, 11) and end = (2018, 6), the iteration will return: (2017, 11), (2017, 12), (2018, 1), (2018, 2), ... (2018, 5)
    '''
    def __init__ (self, begin = None, end=None) :
        min_date = ( 2015, 5)
        if not begin :
            self.begin = min_date
        else :
            self.begin = begin
            
        if end :
            self.end = end
        else :
            self.end = (datetime.now().year, datetime.now().month)
            
    def __iter__ (self) :
        self.it = (self.begin[0], self.begin[1] - 1)
        return self
        
    def __next__(self):
        it_year, it_month = self.it
        it_month += 1
        if (it_year, it_month) >= self.end :
            raise StopIteration
        if it_month > 12 :
            it_year, it_month = it_year + 1, 1
            
        self.it = it_year, it_month
        return self.it

class download_and_save_factory :
    '''
    class used to download and save the pageviews by month
    '''
    def __init__ (self, base_url, dump_folder, count_folder, project, set_allowed_projects) :
        '''
        base_url : base of the url from which the SQL dumps will be saved
        dump_folder : folder in which the results will be saved
        project, set_allowed_projects: TODOC
        '''
        self.base_url = base_url
        self.dump_folder = dump_folder
        self.count_folder = count_folder
        self.project = project
        self.set_allowed_projects = set_allowed_projects
        
    def download_and_save (self, it_year_month ) :
        '''
        Download the dump from the month represented in {it_year_month} as (year, month) where month is an int i representing the ith month 
        (i.e. 1 = January, 2 = February ..., 12 = December)
        '''
        it_year, it_month = it_year_month
        dump_name = 'pageviews-%d%02d-user.bz2' % (it_year, it_month)
        id_count_save_file = dump_name.replace('.bz2', '_id_count.json')
        title_count_save_file = dump_name.replace('.bz2', '_title_count.json')

        print(dump_name, 'start')
        #if we already got the pageviews extracted from the SQL dump, we don't need to download it again
        if os.path.exists(self.dump_folder + id_count_save_file) and os.path.exists(self.dump_folder + title_count_save_file) :
            print(dump_name, 'count: already done')
            return
        
        save_filename = self.dump_folder + dump_name
        reduced_save_filename = save_filename.replace('.bz2', '_reduce.bz2')
        if os.path.exists(save_filename) or os.path.exists(reduced_save_filename) :
            print(dump_name, 'already done')
        else :
            suffix_url = '%d/%d-%02d/' % (it_year, it_year, it_month,) + dump_name
            download_page(save_filename, url = self.base_url + suffix_url)
            print(dump_name, 'done')

        reduce_size_dump(save_filename, reduced_save_filename, self.set_allowed_projects)
        count_title_id(reduced_save_filename, self.count_folder, self.project, )

def reduce_size_dump(save_filename, reduced_save_filename, set_allowed_projects) :
    '''
    TODOC
    '''
    if os.path.exists(reduced_save_filename) :
        return

    already_project = set()
    count_project = None

    counter = Counter()

    with bz2.open( save_filename) as f_in  :
        with bz2.open( reduced_save_filename, 'w') as f_out  :
            for line in f_in :
                line = line.strip().split(b' ')
                project_type = line[0].split(b'.')
                if len(line) == 6 and len(project_type) == 2 and project_type[0] and project_type[1] == b'wikipedia' and line[2] != b'null':
                    project, typ = project_type
                    
                    if count_project != project :
                        assert not project in already_project
                        if counter :
                            f_out.write(b'\n'.join(
                                b'%b %b %b %i'%(count_project, title, id_, count) 
                                for (title, id_), count in counter.items() )
                            )

                        already_project.add(project)
                        counter = Counter()
                        count_project = project
                        
                    if project in set_allowed_projects :
                        counter[(line[1], line[2])] += int(line[4])
                        
            if counter:
                f_out.write(b'\n'.join(
                    b'%b %b %b %i'%(count_project, title, id_, count) 
                    for (id_, title), count in counter.items() )
                )
    os.remove(save_filename)


def count_title_id(save_file, count_folder, project) :
    '''
    Take a SQL dump of the pageviews and transform it into dicts {id: pageview} and {title: pageviews}
    TODOC project
    '''    
    id_count_save_file = count_folder + save_file.split('/')[-1].replace('.bz2', '_id_count.json')
    title_count_save_file = count_folder + save_file.split('/')[-1].replace('.bz2', '_title_count.json')

    if os.path.exists(id_count_save_file) and os.path.exists(title_count_save_file) :
        print(save_file.split('/')[-1], 'done')
        return

    print(save_file.split('/')[-1],'start')

    #pageviews are SQL dumps, but it is faster to directly parse it by reading which values were supposed to be inserted.
    id_count = Counter()
    title_count = Counter()
    string_byte = project.encode('utf8')
    with bz2.open( save_file) as f  :
        for line in f :
            if line.strip() and line.startswith(string_byte) :
                line = line.decode('utf-8').strip().split(' ')

                if len(line) == 4 :
                    count, title, id_, count = line
                    title_count[title] += int(count)
                    id_count[id_] += int(count)
                else :
                    print('reduced count line != 4', line)
                
    with open(id_count_save_file, 'w', encoding='utf8') as f :
        json.dump(dict(id_count), f)
    with open(title_count_save_file, 'w', encoding='utf8') as f :
        json.dump(dict(title_count), f)

    print(save_file.split('/')[-1],'done')

def get_title_count_sorted(sorted_view_file, dump_folder, begin_month, id2title_file, synonyms_file) :
    '''
    Prerequisite: Need to have downloaded the pageviews by month and have applied count_title_id on them

    Take the folder {dump_folder} in which the pageviews were saved and merge them by getting the mean views over the years where the page existed
    (i.e. if a page was created in 2018, if that page has X cumulated pageview and if we are currently in 2022, its merge score is X / (2022-2018))

    sorted_view_file: file into which toi save the result
    begin_month: month (as formatted in iter_month) from which to start to get the pageviews
    id2title_file: file containing the dictionary {wikipedia id: wikipedia title} of all main pages. Used to filter pages whose namespaces are not "Main"
    synonyms_file: file containing the redirects, used to merge the redirect pageview to their main pages
    '''
    #load the titles of the main pages and the redirects
    with open(id2title_file, encoding='utf8') as f :
        set_titles = set(json.load(f).values())

    synonyms = {}
    with open(synonyms_file, encoding='utf8' ) as f :
        reader = csv.reader(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for from_word, to_word in reader :
            synonyms[from_word] = to_word
    synonyms = { from_word: to_word for from_word, to_word in synonyms.items() if not to_word in synonyms }

    #merge the pageview
    sum_word, nb_word_by_year = Counter(), Counter()
    current_year = None
    curr_year_set_word = set()
    for it_year, it_month in iter_month(begin_month) :
        print('merging count', it_year, it_month)
        #If we change year, update the number of years in of the article which were in the prior year and reset the set of articles used in the current year
        if current_year != it_year :
            current_year = it_year
            nb_word_by_year.update(curr_year_set_word)
            curr_year_set_word = set()
        
        title_file = dump_folder + 'pageviews-%d%02d-user_reduce_title_count.json' % (it_year, it_month)
        with open(title_file, encoding='utf8') as f :
            curr_title_count = json.load(f)
        #filter the non main pages and cast the count as int
        curr_title_count = { title: int(count) for title, count in curr_title_count.items() if title in set_titles }
        #update the cumulative pageviews
        parsed_title_count = Counter()
        for title, count in curr_title_count.items() :
            #if the title is a synonym, add it to the count of its main page
            if title in synonyms :
                parsed_title_count[synonyms[title]] += count
            elif title in set_titles :
                parsed_title_count[title] += count
        sum_word.update(parsed_title_count)
        #update the set of articles used in the current year
        curr_year_set_word.update(set(parsed_title_count))
    nb_word_by_year.update(curr_year_set_word)

    mean_word = {title: sum_count / nb_word_by_year[title] for title, sum_count in sum_word.items() }
    #save result as a csv
    with open(sorted_view_file , 'w' , encoding='utf8' , newline='' ) as f :
        writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for word, count in sorted(mean_word.items(), key = lambda x : x[1], reverse=True) :
            writer.writerow((word, count))

def main_download_wiki_title(project, vocab_folder_name, set_allowed_projects=set_allowed_download_projects, begin_month = None, use_multiprocessing = True, save_parent_folder=base_vocab_folder) :
    '''
    Download the pageviews by article

    TODOC project vocab_folder_name set_allowed_projects
    begin_month: month (as formatted in iter_month) from which to start to get the pageviews
    use_multiprocessing: if True use multiprocessing
    '''
    count_folder = save_parent_folder + vocab_folder_name + '/count_dump/'

    extent_list = count_folder.split('/')
    folder_to_create = ''
    for new_folder in extent_list :
        folder_to_create += new_folder + '/'
        if not os.path.exists(folder_to_create) :
            os.mkdir(folder_to_create)

    dump_folder = save_parent_folder + 'dumps/'
    meta_folder = save_parent_folder + vocab_folder_name + '/meta/'
    for folder in [dump_folder, meta_folder] :
        if not os.path.exists(folder) :
            os.mkdir(folder)
    sorted_view_file = meta_folder + 'sorted_view_wiki_over_years.csv'
    id2title_file = meta_folder + 'id2title.json'
    synonyms_file = meta_folder + 'synonyms.csv'

    base_url = 'https://dumps.wikimedia.org/other/pageview_complete/monthly/'
    downloader_and_saver = download_and_save_factory(base_url, dump_folder, count_folder, project, set_allowed_projects)
    
    if use_multiprocessing :
        with Pool(3) as p:
            p.map(downloader_and_saver.download_and_save, iter_month(begin_month))
    else :
        for it_year_month in iter_month(begin_month) :
            downloader_and_saver.download_and_save(it_year_month)

    get_title_count_sorted(sorted_view_file, count_folder, begin_month, id2title_file, synonyms_file)

if __name__ == '__main__' : 
    main_download_wiki_title(begin_month = (2016, 1))
