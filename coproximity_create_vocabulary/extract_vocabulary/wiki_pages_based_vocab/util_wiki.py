# put the first letter in uppercase
unwikititle = lambda x : (x[0].lower() + x[1:]) if x else x
# put the first letter in lowercase
rewikititle = lambda x : (x[0].upper() + x[1:] ) if x else x