#----------- Standard Library 
import re,sys
#----------- Semi-Standard Library
import web                    #web.py code, includes db access
import sqlite3 as sql        #can easily be replaced with other SQL
#----------- Custom Library
sys.path.append('modules/') #Put the modules directory in the pythonpath
from organizers import Configuration     #Used to read JSON/XML configuration files.
import lexical_parser as lex             #Parses Abstract Syntax Tree, for tokens in ('and','or','not','TAG_NAME')



#setup for web.py
_config = Configuration.read("configs/settings.json")
_db = web.database(dbn='sqlite',db='bloom.db')
_render = web.template.render('templates/',base='wrapper')
_render_naked = web.template.render('templates/')
_naming = Configuration.read("configs/sql_naming.json")
#_naming = {
#    'tags_table':'tags',
#    'images_table':'images',
#    'join_table':'images_tags',
#    'join_table_id_col':'images_tags_id',
#    'images_id_col':'images_id',
#    'tags_id_col':'tags_id',
#    'tags_name_col':'name'
#    }


#[] Flow-Control: function which calls all of the parts in sequence
    #[] Split: sqlite_is_bad around the line: processed_imageset = sqlite_needs_help
#[] Refactor: lexical_parser - to feed the content = ids in explicitly in calling code
    #[] Remove the test data from the Token() 
#[] Abstract: function to build itags dict
#[] Work Paarth's code into


#============================
#  Workhorse Functions
#============================
#Function Sequence: enters at sqlite_is_bad, or search_good_db

def search_tags(tags_string):
    if tags_string == "" or tags_string == []:
        return []
    
    if _config['sql_engine']=="sqlite":
        return search_sqlite(tags_string)
        #return search_sqlite(tags_string)
    elif _config['sql_engine'] in ["postgre","postgresql","mssql","oracle"]:
        return search_good_db(tags_string)
    else:
        raise Exception("Unrecognized sql_engine: "+_config['sql_engine'])


def search_sqlite(searchstr):
    #Used to be 'sqlite_is_bad()'
    tokens = [lex.Token(name) for name in lex.tokenize(searchstr)]
    try:
        lex.validate(tokens)    #bitches if token names are wrong
    except Exception as exc:
        #This should be turned into an error page.
        raise exc
    tags = [t.name for t in tokens
            if t.type == 'tag']
    itags = get_image_ids(tags)
    
    lex.set_tag_ids(tokens,itags)
    processed_ids = lex.evaluate(tokens)
    return render_image_ids(processed_ids)

def get_image_ids(tags):
    '''Returns dict of tag_name:[image_ids].'''
    #CODE SPLIT FROM sqlite_is_bad()
    itags = {}
    for tag in tags:
        #@todo: this will need to be changed for the new table structure
        #@todo: project this from SQL injection via the vars={} parameter
        sql_select = '''SELECT {images_id_col} 
                        FROM {join_table} INNER JOIN {tags_table} 
                            ON {join_table}.{tags_id_col} = {tags_table}.{tags_id_col}
                        WHERE {tags_table}.{tags_name_col} = '{tag_val}';'''.format(
                            tag_val=tag,**_naming.dict())
        #sql_select = ' SELECT ImageID FROM ImageTags INNER JOIN Tags ON ImageTags.tagID = Tags.ID WHERE Tags.name = \''+tag+'\' '
        tagdata = _db.query(sql_select)
        itags[tag] = set(t.__getitem__(_naming['images_id_col']) for t in tagdata)
        #itags[tag] = set(t.ImageID for t in tagdata)
    return itags

def render_image_ids(processed_ids):
    wherestring = ''
    for image_id in processed_ids:
        if len(wherestring) > 0:
            wherestring += ' OR '
        wherestring += (_naming['images_id_col']+" = "+str(image_id))
        #wherestring += ('id = ' + str(image_id))

    if len(wherestring) == 0:
        wherestring="null"
    result = _db.select('images',where=wherestring)
    return result




##@deprecated: 
#def search_sqlite(searchstr):
#    #Used to be called: sqlite_is_bad()
#    itags = get_image_ids(searchstr)
#    processed_imageset = sqlite_needs_help(searchstr.replace('_',' '),itags)
#
#    print("processed imageset: ")
#    print(processed_imageset)
#
#    # each of the images are used to assemble a wherestring, similarly to how it is done in search_good_db.
#    # the same process is used twice and this should probably be its own function.
#    wherestring = ''
#    for imageid in processed_imageset:
#        if len(wherestring) > 0:
#            wherestring += ' OR '
#        wherestring += ('id = ' + str(imageid))
#
#    if len(wherestring) == 0:
#        wherestring="null"
#    result = _db.select('images',where=wherestring)
#    return _render.images(result)
#
#
#    
##@deprecated: 
#def old_get_image_ids(searchstr):
#    #CODE SPLIT FROM sqlite_is_bad()
#    pattern = re.compile(re.escape('and'), re.IGNORECASE)
#    working_string = pattern.sub ('', searchstr.replace('_',' '))
#    pattern = re.compile(re.escape('or'), re.IGNORECASE)
#    working_string = pattern.sub ('', working_string)
#    working_string = working_string.replace('(','').replace(')','')
#
#
#    #---------- Crucial Variable
#    #itags: dict of 'tag_name':[tag_ids,...] 
#    itags = {}
#
#    working_string = ' '.join(working_string.split()) #make sure that there is only one space between each entry
#    tags = working_string.split(' ') # tags is now a list of tag names.
#
#    for tag in tags:
#        #NOTE: this will need to be changed for the new table structure
#        sql_select = ' SELECT ImageID FROM ImageTags INNER JOIN Tags ON ImageTags.tagID = Tags.ID WHERE Tags.name = \''+tag+'\' '
#        tagdata = _db.query(sql_select)
#        
#        itags[tag] = set(t.ImageID for t in tagdata)
#    return itags
#
#def sqlite_needs_help(searchstr,itags):
#    # REAL TERROR
#    # This class take in the original search string that the user input and a dictionary
#    # that lists tags and the set of images associated with that tag. Using them, it returns
#    # the set of images that the search string evaluates to.
#    #
#    # This function is both iterative and recursive. #xYOLOx420xGGx
#
#    # This function has two special cases: 
#    #    If there are parenthesis, it executes itself on the inner string first
#    #    If there is only one word then it returns the set associated with that tag
#    #
#    #    If it comes to the rest of the function, that means that we are left with a flat
#    #    string with only tags and the 'and'/'or' keywords. We can now process the string.
#    #    This happens by looping while there are 'and's in the string, and then while there
#    #    are 'or'. In each loop step we combine the 'and' term with its neighbors (its operands)
#    #    and then delete the other two terms so that the result may be used with the next tag.
#    #
#    #    For example:
#    #
#    #    set AND set OR set
#    #
#    #            will become..
#    #
#    #    set OR set
#    #
#    #    eventually we will be left with one set, which is returned.
#    #    the and step happens before the OR to enforce the order of operations where AND
#    #    is more tightly binding.
#    searchstr = searchstr.strip()
#    searchstr = searchstr.replace('_',' ').encode('ascii','ignore') # for some reason it was in unicode which didn't play nice with the db
#    print("search string: "+searchstr)
#    print(type(searchstr))
#
#
#    eval_list = []
#    # so eval list is somewhat creative and somewhat fucking stupid. I did not want
#    # to replace the string that used to be in the search string with something 
#    # arbitrary because that could collide with the tag that the user inputs. Instead,
#    # I made it so that the content that is inside parenthesis is removed and we are 
#    # left with a '()' where it used to be. When the evaluator (the iterative part) of
#    # the function reaches one of those ()'s, it pulls the entry off the front of the
#    # eval_list (which works like a queue) and uses it in the set operation. 
#
#
#    print('Entering SQLNH: '+searchstr)
#
#    # recurse if there are parenthesis in the string.
#    if '(' in searchstr or ')' in searchstr:
#        print('parens search '+searchstr)
#        inner = re.search( "\((.*)\)" ,searchstr).group(1)
#        eval_list.append(sqlite_needs_help(inner, itags))
#        searchstr = searchstr.replace(inner,"",1)
#
#    #return the set of images associated with a tag if that tag is the only thing there.
#    if not ' ' in searchstr.strip():
#        if searchstr.strip() in itags:
#            return itags[searchstr]
#        else:
#            raise NameError('invalid tag: '+searchstr)
#
#    #begin the evaluating process, otherwise.
#    else:
#        pieces = searchstr.split(' ')
#
#        while 'and' in pieces: # while there are still unprocessed and_tags, deal with them.
#            inf_index = pieces.index('and')
#            if inf_index == 0 or inf_index == (len(pieces) -1):
#                # if the and is at the beginning or the end of a list it is malformed and an
#                # exception should be raised.
#                raise NameError('and is infix')
#            print(pieces[inf_index-1])
#            print(pieces[inf_index])
#            print(pieces[inf_index+1])
#            print(type(pieces[inf_index-1]))
#
#            # if the operands are strings, evaluate them into imagesets.
#            if type(pieces[inf_index-1]) is str:
#                if '()' in pieces[inf_index-1]:
#                    pieces[inf_index-1] = eval_list[0]
#                    del eval_list[0]
#                else:
#                    pieces[inf_index-1] = sqlite_needs_help(pieces[inf_index-1],itags)
#            if type(pieces[inf_index+1]) is str:
#                if '()' in pieces[inf_index+1]:
#                    pieces[inf_index+1] = eval_list[0]
#                    del eval_list[0]
#                else:
#                    pieces[inf_index+1] = sqlite_needs_help(pieces[inf_index+1],itags)
#
#            #perform the set operation.
#            combined = pieces[inf_index-1] & pieces[inf_index+1]
#            pieces[inf_index-1] = combined
#            #remove the extraneous entries.
#            del pieces[inf_index]
#            del pieces[inf_index]
#
#        # the same thing as the and, but for or. 
#        while 'or' in pieces:
#            inf_index = pieces.index('or')
#            if inf_index == 0 or inf_index == (len(pieces) -1):
#                raise NameError('or is infix')
#            if type(pieces[inf_index-1]) is str:
#                if '()' in pieces[inf_index-1]:
#                    pieces[inf_index-1] = eval_list[0]
#                    del eval_list[0]
#                else:
#                    pieces[inf_index-1] = sqlite_needs_help(pieces[inf_index-1],itags)
#            if type(pieces[inf_index+1]) is str:
#                if '()' in pieces[inf_index+1]:
#                    pieces[inf_index+1] = eval_list[0]
#                    del eval_list[0]
#                else:
#                    pieces[inf_index+1] = sqlite_needs_help(pieces[inf_index+1],itags)
#            combined = pieces[inf_index-1] | pieces[inf_index+1]
#            pieces[inf_index-1] = combined
#            del pieces[inf_index]
#            del pieces[inf_index]
#        if len(pieces) == 1:
#            return pieces[0]

#==========================================
#  Non-sqlite Functions
#==========================================
#postgresql, oracle, mssql
def transform_to_sql(searchstr=''):
    #This is the helper function for when a database that supports nested intersects is used. 
    #Conveniently, the tag set op structure we have (x and y or z) can translate directly 
    #to sql by translating x to selecting for X and the 'and' and 'or' functions to INTERSECT/UNION

    #working_string is the string that we use for converting searchstr.
    working_string = searchstr
    pattern = re.compile(re.escape('and'), re.IGNORECASE)
    working_string = pattern.sub (' INTERSECT ', searchstr)
    pattern = re.compile(re.escape('or'), re.IGNORECASE)
    working_string = pattern.sub (' UNION ', working_string)
    #working_string now has all 'and' and 'or' replaced properly.

    #for my own debugging purposes
    print("working string")
    print(working_string)

    #takes apart the string to work on tags individually
    pieces = working_string.split('_')

    #for each word in the string that is not 'intersect' or 'union' replace it with the query searching
    #for the images related to that term.
    for piece in pieces:
        if piece.strip() != 'INTERSECT' and piece.strip() != 'UNION':
            clean_piece = piece.replace('(','').replace(')','') #if the word is 'tag)' then the parens need to be removed before querying for it.
            working_string = working_string.replace(clean_piece, 'SELECT ImageID FROM ImageTags INNER JOIN Tags ON ImageTags.tagID = Tags.ID WHERE Tags.name = \''+clean_piece+'\'')
    return working_string.replace('_','') 

def search_good_db(self, tags):
    # used with either PostgreSQL, MS SQL Server, or Oracle
    #
    # takes in a user-entered string of tag and set operations. It returns the rendered page which can
    # be directly sent back by the server. This is probably bad design and it should be changed to 
    # instead return an imageset.
    #
    #
    wherestring = ""
    rowset = _db.query(transform_to_sql(tags)); #convert the string to a valid query
    for row in rowset:
        print('row')
        print(row) #debugging.

        #assemble the wherestring, so we can do a SELECT WHERE name=tag1 OR name=tag2 ... name=tagN
        if len(wherestring) > 0:
            wherestring += ' OR '
        wherestring += ('id = ' + str(row.ImageID))
    print (wherestring) #bad debugging.
    if len(wherestring) == 0:
        wherestring="null"
    result = _db.select('images',where=wherestring) #get the imageset and place it in result
    return _render.images(result) #render the page and return the templated string.




#============================
# Oakland's Code In Progress
#============================

#@Incomplete
def get_tag_ids(tags):
    '''Returns a dict of lists of tag ids.'''
    paging_size = 20
    for section in grouper(tags,paging_size):
        _db.select('tags',where='name='+tag_name)
        
def grouper(iterable, n, fillvalue=None):
    '''Collect data into fixed-length chunks or blocks.'''
    # grouper('ABCCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue,*args)   

if __name__ == "__main__":
    #print(search_tags('asfkljl3%44123-*3kl+lk_'))
    result = search_tags('boobs or icecream')
    print(list(result))
