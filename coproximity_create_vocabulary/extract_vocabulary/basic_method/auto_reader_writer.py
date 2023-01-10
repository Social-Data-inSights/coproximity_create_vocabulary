'''
Iterate over and write different type of extension. 

For now there are 3 extensions :
- .csv: csv files. By default the csv is considered as having of 2 columns: article id , their contents Their default arguments are delimiter=';' and default quotechar='"'
- .json : dictionary or list of a json file. By default considered the json as {article id: theirs contents}
- .jsons: file containing for each line a json. By default considered each line to be [article id, their contents]

To use the readers, you only need to iterate on them and close them at the end.

To use the writer, you can add elements by using writer.write_row, and once everything was written use writer.close.
'''

import json, csv
csv.field_size_limit(100000000)

def reader_len(it) :
    '''
    Given a reader iterator, get the number of element in it
    '''
    count = 0
    for _ in it :
        count += 1
    return count

def auto_reader(filepath, list_select = None, **args) :
    
    '''
    takes a path to a file {filepath} and some arguments {args}. Choose automatically the reader based on the file extension 
    and return it initialized with the arguments {args}

    list_select: can give a list of elements to read from each iteration, for more details see each class.
    '''
    extension = filepath.split('.')[-1]
    if extension == 'json' :
        return read_json(filepath, list_select=list_select)
    elif extension == 'csv' :
        return read_csv(filepath, list_select=list_select, csv_args = args.get('csv_args', dict(delimiter=';', quotechar='"')), has_header= args.get('has_header'))
    elif extension == 'jsons' :
        return read_jsons(filepath, list_select=list_select)
    else :
        raise Exception('unkown extension: ' + extension)

class read_csv :
    '''
    iterator reading a csv
    '''
    def __init__ (self, filepath, list_select=None, csv_args=dict(delimiter=';', quotechar='"'), has_header=None, **args) :
        '''
        filepath: path of the csv file to load
        list_select: list of the columns to read. Can be a list of index in that case, we take the ith elements for all i in the list
            If  we have the names of the column (i.e. if has_header is True), we can give a list of the names of the column to read
            If none is given read the whole line at each iteration
        csv_args: args to give to the csv.reader , mostly set the delimiter and the quote character (quotechar)
        has_header: If True, the first line is considered a header and is used to give a name for each column
        '''
        self.filepath = filepath
        self.csv_args = csv_args
        self.list_select = list_select
        self.has_header = has_header if not has_header is None else (not list_select is None)
        self.file = None
        self.reader = None
    
        self.header = None
        self.header_str2int = None

    def __iter__(self) :
        if self.file :
            self.file.close()
            self.file=None

        #check that the element of the list is a int or if this is a string assert we have the column names
        if self.list_select :
            for elem_select in self.list_select :
                assert  (not type(elem_select) is str or self.has_header) or type(elem_select) is int

        self.file = open(self.filepath, encoding='utf8')
        self.reader = csv.reader(self.file, **self.csv_args )
        self.iter = iter(self.reader)

        if self.has_header  :
            self.header = next(self.iter)
            self.header_str2int = { col_name: i for i, col_name in enumerate(self.header) }
            if self.list_select :
                self.list_select = [self.header_str2int[elem_select] if type(elem_select) is str else elem_select for elem_select in self.list_select]
        else :
            self.header = None
            self.header_str2int = None

        return self
        
    def __next__(self) :
        try :
            if self.list_select is None :
                return next(self.iter)
            else :
                next_line = next(self.iter)
                return tuple(next_line[elem_select] for elem_select in self.list_select)
        except Exception as e :
            self.file.close()
            self.file=None
            self.reader = None
            raise e

    def close(self) :
        if self.file:
            self.file.close()
            self.file=None

class read_json :
    '''
    iterator reading a json. The json is expected to be a list or a dict,
        the elements of the iterated should be either string, lists or dictionaries but should not alternate.
    '''
    def __init__ (self, filepath, list_select=None, **args) :
        '''
        filepath: path of the json file to load
        list_select: list of the elements to read from each iteration. 
            An element can have a special value:
                __index__ : if dict, the index of the iteration, if list the indice of the element in the list
                __value__ : the whole value of the iterated (without the index), typically used for iteration on dict {str : str}
            Depending on the elements to iterate on, you should give it a different format
                If the elements of the iteration are lists, should be a list of indexes (+ 2 special values)
                If the elements of the iteration are dicts, should be a list of index names of the dicts (+ 2 special values)
                If the elements of the iteration are strings, should be one of the special values
            If none is given, read all the values and the index(for a list this the position of the element in the list) at each iteration
        '''
        self.filepath = filepath
        self.list_select = list_select
        self.type_values = None
    
    def __iter__(self) :
        with open(self.filepath, encoding='utf8') as f :
            self.json_content = json.load(f)
        self.json_type = type(self.json_content)
        self.type_values = type(next(iter(self.json_content.values()))) if self.json_type is dict else type(self.json_content[0])
        if not self.list_select is None :
            for elem_select in self.list_select :
                if self.type_values is dict :
                    assert type(elem_select) is str
                elif self.type_values is list :
                    assert type(elem_select) is int or elem_select in ('__index__', '__value__')
                else :
                    assert elem_select in ('__index__', '__value__')
        if self.json_type is dict :
            self.iter = iter(self.json_content.items())
        elif self.json_type is list :
            self.iter = iter(enumerate(self.json_content))
        else :
            raise Exception(f'read_json.json_content should be a dict or a list, is {self.type_values}')
        return self
        
    def __next__(self) :
        try :
            if self.list_select is None :
                if self.json_type is dict :
                    return next(self.iter)
                elif self.json_type is list :
                    return next(self.iter)[1]
            else :
                next_idx, next_value = next(self.iter)
                return tuple(
                    next_idx if elem_select == '__index__' else (next_value if elem_select == '__value__' else next_value[elem_select]) 
                    for elem_select in self.list_select
                )
        except Exception as e :
            del self.json_content
            self.json_content=None
            raise e

    def close(self) :
        if self.json_content:
            del self.json_content
            self.json_content=None

class read_jsons :
    '''
    iterator reading a jsons file. a jsons file is a file in which, each line is a json dump
    '''
    def __init__ (self, filepath, list_select=None, **args) :
        '''
        filepath: path of the jsons file to load
        list_select: list of the elements to read from each iteration. 
            Depending on the elements to iterate on, you should give it a different format
                If the elements of the iteration are lists, should be a list of indexes
                If the elements of the iteration are dicts, should be a list of index names of the dicts
            If none is given read the whole line at each iteration
        '''
        self.filepath = filepath
        self.list_select = list_select
        self.file = None
        self.type_values = None
        
    def __iter__(self) :
        if self.file :
            self.file.close()
        self.file = open(self.filepath, encoding='utf8')
        return self
        
    def __next__(self) :
        try :
            if self.list_select is None :
                return json.loads(next(self.file))
            else :
                next_line = json.loads(next(self.file))
                if self.type_values is None :
                    self.type_values = type(next_line)
                    for elem_select in self.list_select :
                        if self.type_values is dict :
                            assert type(elem_select) is str
                        elif self.type_values is list :
                            assert type(elem_select) is int 
                        else :
                            raise Exception('if jsons lines are not iterable, use list_select=None')
                return tuple(next_line[elem_select] for elem_select in self.list_select)
        except StopIteration as e:
            self.file.close()
            self.file=None
            raise e

    def close(self) :
        if self.file:
            self.file.close()
            self.file=None

def auto_writer(filepath, list_select=None, open_mode='w', csv_args= dict(delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL), **args) :
    '''
    takes a path to a file {filepath} and some arguments {args}. Choose automatically the writer based on the file extension 
    and return it initialized with the arguments {args}.
    Also take an mode for  the open file {open_mode}, should be either 'a' (append) or 'w' (write)
    You need to close the writer to be sure the result is really saved.

    list_select: List of the names of the elements to write, for more details see the specifics class
    csv_args: used only if writing a csv, args to give to the csv.reader , mostly set the delimiter and the quote character (quotechar)
    '''
    extension = filepath.split('.')[-1]
    if extension == 'json' :
        return write_json(filepath, open_mode, list_select, **args)
    elif extension == 'csv' :
        return write_csv(filepath, open_mode, list_select, csv_args = csv_args, **args)
    elif extension == 'jsons' :
        return write_jsons(filepath, open_mode, list_select, **args)
    else :
        raise Exception('unkown extension: ' + extension)

class write_json :
    '''
    a writer for a json dictionary
    '''
    def __init__ (self, filepath, open_mode = 'w', list_select=None, **args) :
        '''
        filepath: path where to write the json
        open_mode: if 'w' overwrite the data at path {filepath}(if there was any), if 'a' append the new data to the old one without deleting it
        list_select: names of the elements to write from each iteration. If one is given, each iteration creates a dict as a value with the name given by {list_select}
            An element can have a special value:
                __index__ : indicate this is to be used as the index
                __value__ : indicate this is to be used as the whole value
            If none is given, the first element of the list to write is used as an index and the remainder is used as a list in the value
        '''
        self.filepath = filepath
        self.open_mode = open_mode
        self.list_select = list_select

        if not self.list_select is None :
            self.list_select_i_index = [i for i, elem_select in enumerate(self.list_select) if '__index__' == elem_select][0] if '__index__' in self.list_select else None
            self.list_select_i_value = [i for i, elem_select in enumerate(self.list_select) if '__value__' == elem_select][0] if '__value__' in self.list_select else None
            self.len_list_select = len(list_select)
 
        else :
            self.list_select_i_index = None
            self.list_select_i_value = None

        if self.open_mode == 'w' :
            self.json_content = {}
        elif self.open_mode == 'a' :
            with open(self.filepath, encoding='utf8') as f :
                self.json_content = json.load(f)
            assert type(self.json_content) is dict
        else :
            raise Exception(f'unknown open mode: {self.open_mode}')
        
    def writerow(self, *content) :
        if self.list_select is None :
            if len(content) == 2 :
                self.json_content[content[0]] = content[1]
            else :
                self.json_content[content[0]] = list(content[1:])

        else :
            assert len(content) == self.len_list_select, (len(content) , self.len_list_select)
            if self.list_select_i_value is None :
                self.json_content[content[self.list_select_i_index]] = { name: cont for name, cont in zip (self.list_select, content) if name != '__index__' and name != '__value__' } 
            else :
                self.json_content[content[self.list_select_i_index]] = content[self.list_select_i_value]
    def close(self) :
        with open(self.filepath, 'w', encoding='utf8') as f :
            json.dump(self.json_content, f)
        del self.json_content

class write_json_list :
    '''
    a writer for a json list
    '''
    def __init__ (self, filepath, open_mode = 'w', list_select=None, **args) :
        '''
        filepath: path where to write the json
        open_mode: if 'w' overwrite the data at path {filepath}(if there was any), if 'a' append the new data to the old one without deleting it
        list_select: names of the elements to write from each iteration. If one is given, each iteration creates a dict with the name of the indexes given by {list_select}
            If none is given, write each iteration as a list of the given data
        '''
        self.filepath = filepath
        self.open_mode = open_mode
        self.list_select = list_select

        if not self.list_select is None :
            self.len_list_select = len(list_select)
        else :
            self.len_list_select = None

        if self.open_mode == 'w' :
            self.json_content = []
        elif self.open_mode == 'a' :
            with open(self.filepath, encoding='utf8') as f :
                self.json_content = json.load(f)
            assert type(self.json_content) is list
        else :
            raise Exception(f'unknown open mode: {self.open_mode}')
        
    def writerow(self, *content) :
        if self.list_select is None :
            self.json_content.append(content)
            
        else :
            assert len(content) == self.len_list_select, (len(content) , self.len_list_select)
            self.json_content.append({ name: cont for name, cont in zip (self.list_select, content) })
            
    def close(self) :
        with open(self.filepath, 'w', encoding='utf8') as f :
            json.dump(self.json_content, f)
        del self.json_content

class write_csv :
    '''
    a writer for a csv
    '''
    def __init__ (self, filepath, open_mode = 'w', list_select=None, csv_args = dict(delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL), **args) :
        ''''
        filepath: path where to write the csv
        open_mode: if 'w' overwrite the data at path {filepath}(if there was any), if 'a' append the new data to the old one without deleting it
        list_select: if one is given, creates an header with this list
        '''
        self.filepath = filepath
        self.open_mode = open_mode
        self.csv_args = csv_args
        self.list_select = list_select
                
        self.file = open(self.filepath, self.open_mode, encoding='utf8' , newline='')
        self.writer = csv.writer(self.file, **self.csv_args )
        
        if not list_select is None :
            self.writer.writerow(list_select)
            self.len_list_select = len(list_select)
    
    def writerow(self, *content) :
        if not self.list_select is None :
            assert len(content) == self.len_list_select, (len(content) , self.len_list_select)
        self.writer.writerow(content)

    def close(self) :
        self.writer = None
        self.file.close()

class write_jsons :
    
    '''
    a writer for a jsons file
    '''
    def __init__ (self, filepath, open_mode = 'w', list_select=None, **args) :
        '''
        filepath: path where to write the json
        open_mode: if 'w' overwrite the data at path {filepath}(if there was any), if 'a' append the new data to the old one without deleting it
        list_select: names of the elements to write from each iteration. 
            If one is given, each iteration creates a dict with the name of the indexes given by {list_select}
            If none is given, write each iteration as a list of the given data
        '''
        self.filepath = filepath
        self.open_mode = open_mode
        self.file = open(self.filepath, self.open_mode, encoding='utf8')
        self.list_select = list_select
        if not list_select is None :
            self.len_list_select = len(list_select)
        
    def writerow(self, *content) :
        if self.list_select is None :
            self.file.write(json.dumps(list(content))+'\n')
        else :
            assert len(content) == self.len_list_select, (len(content) , self.len_list_select)
            self.file.write(json.dumps({ name: cont for name, cont in zip (self.list_select, content)})+'\n')

    def close(self) :
        self.file.close()

if __name__ =='__main__':
    #test
    import os
    data = [(str(i), 'a' * i) for i in range(10)]
    data2 = [(str(i), 'f', 'a' * i, ) + tuple('ake') for i in range(10)]
    data3 = [('f', 'a' * i, str(i)) for i in range(10)]

    list_json_write2 = ['__index__', 'f', '__value__', 'a', 'k', 'e']

    list_json_write3  = ['__index__', 'f', 'nb_a', 'a', 'k', 'e']
    list_select_write3 = ['it', 'f', 'nb_a', 'a', 'k', 'e']

    list_json_read4 = ['__index__', 'nb_a']
    list_select_read4 = ['it', 'nb_a']

    list_select_data3 = [ 'f', 'nb_a', 'it',]


    for i, (extension, list_select_write, write_data, list_select_read, good_result_list, args_read) in enumerate([
        #0
        ('csv', None, data, None, data, {},),
        ('json', None, data, None, data, {}, ),
        ('jsons', None, data, None, data, {}, ),
        ('json', list_json_write2, data2, None, data, {}, ),
        ('json', None, data, ['__index__', '__value__'], data, {}, ),
        #5
        ('csv', list_select_write3, data2, None, data2, {'has_header': True}, ),
        ('json', list_json_write3, data2, list_json_write3, data2, {}, ),
        ('jsons', list_select_write3, data2, list_select_write3, data2, {}, ),
        
        #8
        ('csv', list_select_write3, data2, list_select_read4, data, {}, ),
        ('json', list_json_write3, data2, list_json_read4, data, {}, ),
        ('jsons', list_select_write3, data2, list_select_read4, data, {}, ),
        
        #11
        ('csv', list_select_write3, data2, [0, 2], data, {}, ),
        ('json', None, data2, ['__index__',] + list(range(5)), data2, {}, ),
        ('jsons', None, data2, None, data2, {}, ),
        ('jsons', None, data2, list(range(6)), data2, {}, ),
        
        #15
        ('csv', list_select_write3, data2, list_select_data3, data3, {}, ),
        ('jsons', list_select_write3, data2, list_select_data3, data3, {}, ),
    ]) :
        filename = f'test{i}.{extension}'
        print(filename)
        
        write_it = auto_writer (filename, list_select=list_select_write)
        for cont in write_data :
            write_it.writerow(*cont)
        write_it.close()
            
        
        reader = auto_reader(filename, list_select=list_select_read, **args_read)
        for good_result, test_it in zip(good_result_list, reader) :
            print(test_it, tuple(test_it))
            assert good_result == tuple(test_it), (good_result, test_it)
        reader.close()

    extension = 'json'
    for i, (list_select_write, write_data, list_select_read, good_result_list, args_read) in enumerate([
        #0
        (None, data, None, data, {}, ),
        (None, data, [0,1], data, {}, ),
        (list_select_write3, data2, list_select_write3, data2, {}, ),
        (None, data2, [0,2], data, {}, ),
        (None, data2, list(range(len(data2[0]))), data2, {}, ),
    ]) :
        filename = f'test{i}.{extension}'
        print(filename)
        
        write_it = write_json_list (filename, list_select=list_select_write)
        for cont in write_data :
            write_it.writerow(*cont)
        write_it.close()
            
        
        reader = auto_reader(filename, list_select=list_select_read, **args_read)
        for good_result, test_it in zip(good_result_list, reader) :
            print(test_it, tuple(test_it))
            assert good_result == tuple(test_it), (good_result, test_it)
        reader.close()

    
    for filename in os.listdir('.') :
        if filename.startswith('test') and not filename.split('.')[-1] in ('py', 'ipynb') :
            print(filename)
            os.remove(filename)