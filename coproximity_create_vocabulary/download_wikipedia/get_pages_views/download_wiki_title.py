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
    def __init__ (self, base_url, dump_folder, project, set_allowed_projects) :
        '''
        base_url : base of the url from which the SQL dumps will be saved
        dump_folder : folder in which the results will be saved
        project: project (=language) from which we want the counts. Must be in the set {set_allowed_projects} when the dumps were downloaded 
            (i.e. if this is launched a first time, without the project, you will need to delete the dumps and this class will redownload them)
        set_allowed_projects: set of the allowed projects, once the dumps are downloaded, only keep the pageviews of those projects. 
            If {project} was not in this variable when the dumps were downloaded, it will not return any count.
        '''
        self.base_url = base_url
        self.dump_folder = dump_folder
        self.project = project
        self.set_allowed_projects = set_allowed_projects
        
    def download_and_save (self, it_year_month ) :
        '''
        Download the dump from the month represented in {it_year_month} as (year, month) where month is an int i representing the ith month 
        (i.e. 1 = January, 2 = February ..., 12 = December)
        '''
        it_year, it_month = it_year_month
        dump_name = 'pageviews-%d%02d-user.bz2' % (it_year, it_month)

        print(dump_name, 'start')
        
        save_filename = self.dump_folder + dump_name
        reduced_save_filename = save_filename.replace('.bz2', '_reduce.bz2')
        if os.path.exists(save_filename) or os.path.exists(reduced_save_filename) :
            print(dump_name, 'already done')
        else :
            suffix_url = '%d/%d-%02d/' % (it_year, it_year, it_month,) + dump_name
            download_page(save_filename, url = self.base_url + suffix_url)
            print(dump_name, 'done')

        reduce_size_dump(save_filename, reduced_save_filename, self.set_allowed_projects)

def reduce_size_dump(save_filename, reduced_save_filename, set_allowed_projects) :
    '''
    reduce the size of the pageview dumps, only keep the project from the set of project {set_allowed_projects}

    save_filename: load the pageview dump from path
    reduced_save_filename: save the reduced-size pageview dump from path
    '''
    if os.path.exists(reduced_save_filename) :
        return

    already_project = set()
    count_project = None

    counter = Counter()

    try :
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
    except OSError:
        print('could not load', save_filename)
    os.remove(save_filename)

def get_title_count_sorted(sorted_view_file, dump_folder, project, begin_month, id2title_file, synonyms_file) :
    '''
    Take the folder {dump_folder} in which the pageview dumps were saved and merge them by getting the mean views over the years where the page existed
    (i.e. if a page was created in 2018, if that page has X cumulated pageview and if we are currently in 2022, its merge score is X / (2022-2018))

    sorted_view_file: file into which toi save the result
    project: project of the pages from which to extract the view counts
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
        
        count_file = dump_folder + 'pageviews-%d%02d-user_reduce.bz2' % (it_year, it_month)

        #get the title count from the SQL dumps
        string_byte = project.encode('utf8')
        curr_title_count = Counter()
        with bz2.open(count_file) as f  :
            for line in f :
                if line.strip() and line.startswith(string_byte) :
                    line = line.decode('utf-8').strip().split(' ')

                    if len(line) == 4 :
                        count, title, id_, count = line
                        curr_title_count[title] += int(count)
                    else :
                        print('reduced count line != 4', line)

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

def main_download_wiki_title(project, language_folder, set_allowed_projects=set_allowed_download_projects, begin_month = None, use_multiprocessing = True, save_parent_folder=base_vocab_folder) :
    '''
    Download the pageviews by article for the project (=language) {project} and save them.

    The dumps (reduced by size depending on the projects from {set_allowed_projects}) will be saved into "{save_parent_folder}dumps/"    
    and the result, a csv of the sorted list of the articles with its mean views, will be saved in
        "{save_parent_folder}{language_folder}/meta/sorted_view_wiki_over_years.csv" 


    project: project (=language) from which we want the counts. Must be in the set {set_allowed_projects} when the dumps were downloaded 
        (i.e. if this is launched a first time, without the project, you will need to delete the dumps and this class will redownload them)
    language_folder: name of the language to extract, will be used as the name of the language folder. 
    set_allowed_projects: set of the allowed projects, once the dumps are downloaded, only keep the pageviews of those projects. 
        If {project} was not in this variable when the dumps were downloaded, it will not return any count.
    begin_month: month (as formatted in iter_month) from which to start to get the pageviews
    use_multiprocessing: if True, speed up using multiprocessing (max 3 threads because of the threshold over Wikipedia downloading)
    save_parent_folder: parent folder in which all the vocabulary files/folder will be saved/created (vocabulary base folder)
    '''
    count_folder = save_parent_folder + language_folder + '/count_dump/'

    extent_list = count_folder.split('/')
    folder_to_create = ''
    for new_folder in extent_list :
        folder_to_create += new_folder + '/'
        if not os.path.exists(folder_to_create) :
            os.mkdir(folder_to_create)

    dump_folder = save_parent_folder + 'dumps/'
    meta_folder = save_parent_folder + language_folder + '/meta/'
    for folder in [dump_folder, meta_folder] :
        if not os.path.exists(folder) :
            os.mkdir(folder)
    sorted_view_file = meta_folder + 'sorted_view_wiki_over_years.csv'
    id2title_file = meta_folder + 'id2title.json'
    synonyms_file = meta_folder + 'synonyms.csv'

    #download the views
    base_url = 'https://dumps.wikimedia.org/other/pageview_complete/monthly/'
    downloader_and_saver = download_and_save_factory(base_url, dump_folder, project, set_allowed_projects)
    
    if use_multiprocessing :
        with Pool(3) as p:
            p.map(downloader_and_saver.download_and_save, iter_month(begin_month))
    else :
        for it_year_month in iter_month(begin_month) :
            downloader_and_saver.download_and_save(it_year_month)

    #merge the views
    get_title_count_sorted(sorted_view_file, dump_folder, project, begin_month, id2title_file, synonyms_file)

if __name__ == '__main__' : 
    main_download_wiki_title(begin_month = (2016, 1))
