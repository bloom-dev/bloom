#----------- Standard Library 
import re
#----------- Semi-Standard Library
import web                    #web.py code, includes db access
#import sqlite3 as sql        #can easily be replaced with other SQL
#----------- Custom Library
from organizers import Configuration     #Used to read JSON/XML configuration files.
import lexical_parser                    #Parses Abstract Syntax Tree, for tokens in ('and','or','not','TAG_NAME')



#setup for web.py
_config = Configuration.read("settings.json")
_db = web.database(dbn='sqlite',db='bloom.db')
_render = web.template.render('templates/',base='wrapper')
_render_naked = web.template.render('templates/')




#[] Flow-Control: function which calls all of the parts in sequence
    #[] v1: Uses Paarth's code only
#[] Abstract: function to build itags dict
#[] Work Paarth's code into


#============================
#  Workhorse Functions
#============================
#Function Sequence: enters at sqlite_is_bad, or search_good_db

def search_tags():
    pass


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

def sqlite_needs_help(searchstr,itags):
    # REAL TERROR
    # This class take in the original search string that the user input and a dictionary
    # that lists tags and the set of images associated with that tag. Using them, it returns
    # the set of images that the search string evaluates to.
    #
    # This function is both iterative and recursive. #xYOLOx420xGGx

    # This function has two special cases: 
    #    If there are parenthesis, it executes itself on the inner string first
    #    If there is only one word then it returns the set associated with that tag
    #
    #    If it comes to the rest of the function, that means that we are left with a flat
    #    string with only tags and the 'and'/'or' keywords. We can now process the string.
    #    This happens by looping while there are 'and's in the string, and then while there
    #    are 'or'. In each loop step we combine the 'and' term with its neighbors (its operands)
    #    and then delete the other two terms so that the result may be used with the next tag.
    #
    #    For example:
    #
    #    set AND set OR set
    #
    #            will become..
    #
    #    set OR set
    #
    #    eventually we will be left with one set, which is returned.
    #    the and step happens before the OR to enforce the order of operations where AND
    #    is more tightly binding.
    searchstr = searchstr.strip()
    searchstr = searchstr.replace('_',' ').encode('ascii','ignore') # for some reason it was in unicode which didn't play nice with the db
    print("search string: "+searchstr)
    print(type(searchstr))


    eval_list = []
    # so eval list is somewhat creative and somewhat fucking stupid. I did not want
    # to replace the string that used to be in the search string with something 
    # arbitrary because that could collide with the tag that the user inputs. Instead,
    # I made it so that the content that is inside parenthesis is removed and we are 
    # left with a '()' where it used to be. When the evaluator (the iterative part) of
    # the function reaches one of those ()'s, it pulls the entry off the front of the
    # eval_list (which works like a queue) and uses it in the set operation. 


    print('Entering SQLNH: '+searchstr)

    # recurse if there are parenthesis in the string.
    if '(' in searchstr or ')' in searchstr:
        print('parens search '+searchstr)
        inner = re.search( "\((.*)\)" ,searchstr).group(1)
        eval_list.append(sqlite_needs_help(inner, itags))
        searchstr = searchstr.replace(inner,"",1)

    #return the set of images associated with a tag if that tag is the only thing there.
    if not ' ' in searchstr.strip():
        if searchstr.strip() in itags:
            return itags[searchstr]
        else:
            raise NameError('invalid tag: '+searchstr)

    #begin the evaluating process, otherwise.
    else:
        pieces = searchstr.split(' ')

        while 'and' in pieces: # while there are still unprocessed and_tags, deal with them.
            inf_index = pieces.index('and')
            if inf_index == 0 or inf_index == (len(pieces) -1):
                # if the and is at the beginning or the end of a list it is malformed and an
                # exception should be raised.
                raise NameError('and is infix')
            print(pieces[inf_index-1])
            print(pieces[inf_index])
            print(pieces[inf_index+1])
            print(type(pieces[inf_index-1]))

            # if the operands are strings, evaluate them into imagesets.
            if type(pieces[inf_index-1]) is str:
                if '()' in pieces[inf_index-1]:
                    pieces[inf_index-1] = eval_list[0]
                    del eval_list[0]
                else:
                    pieces[inf_index-1] = sqlite_needs_help(pieces[inf_index-1],itags)
            if type(pieces[inf_index+1]) is str:
                if '()' in pieces[inf_index+1]:
                    pieces[inf_index+1] = eval_list[0]
                    del eval_list[0]
                else:
                    pieces[inf_index+1] = sqlite_needs_help(pieces[inf_index+1],itags)

            #perform the set operation.
            combined = pieces[inf_index-1] & pieces[inf_index+1]
            pieces[inf_index-1] = combined
            #remove the extraneous entries.
            del pieces[inf_index]
            del pieces[inf_index]

        # the same thing as the and, but for or. 
        while 'or' in pieces:
            inf_index = pieces.index('or')
            if inf_index == 0 or inf_index == (len(pieces) -1):
                raise NameError('or is infix')
            if type(pieces[inf_index-1]) is str:
                if '()' in pieces[inf_index-1]:
                    pieces[inf_index-1] = eval_list[0]
                    del eval_list[0]
                else:
                    pieces[inf_index-1] = sqlite_needs_help(pieces[inf_index-1],itags)
            if type(pieces[inf_index+1]) is str:
                if '()' in pieces[inf_index+1]:
                    pieces[inf_index+1] = eval_list[0]
                    del eval_list[0]
                else:
                    pieces[inf_index+1] = sqlite_needs_help(pieces[inf_index+1],itags)
            combined = pieces[inf_index-1] | pieces[inf_index+1]
            pieces[inf_index-1] = combined
            del pieces[inf_index]
            del pieces[inf_index]
        if len(pieces) == 1:
            return pieces[0]




def sqlite_is_bad(self,searchstr):
    # As said in the function name, SQLite is bad and so we need to do the set operations ourselves
    # (it doesn't support nesting). This function accomplishes this.
    # 

    # working string eventually becomes the a flat string of tags separated by spaces
    # the working string is then looped thorugh to generate the {tag:imageset} dict, itags
    pattern = re.compile(re.escape('and'), re.IGNORECASE)
    working_string = pattern.sub ('', searchstr.replace('_',' '))
    pattern = re.compile(re.escape('or'), re.IGNORECASE)
    working_string = pattern.sub ('', working_string)
    working_string = working_string.replace('(','').replace(')','')


    #---------- Crucial Variable
    #itags: dict of 'tag_name':[tag_ids,...] 
    itags = {}

    working_string = ' '.join(working_string.split()) #make sure that there is only one space between each entry
    tags = working_string.split(' ') # tags is now a list of tag names.

    for tag in tags:
        print('sqlib tag: '+tag) # REAL MAN.
        tagdata = _db.query(' SELECT ImageID FROM ImageTags INNER JOIN Tags ON ImageTags.tagID = Tags.ID WHERE Tags.name = \''+tag+'\' ')
        imageset = set() #the set of images associated with the tag.
        for t in tagdata:
            imageset.add(t.ImageID) # add images to the set.
        itags[tag] = imageset # list it in the dict.
    print("processed imageset beginning with " +searchstr)

    # MAGIC FUNCTION TIME. sqlite_needs_help is called which takes the original statement and the tag dictionary
    # and does magic on it to condense the result into a set of images
    processed_imageset = sqlite_needs_help(searchstr.replace('_',' '),itags)

    print("processed imageset: ")
    print(processed_imageset)

    # each of the images are used to assemble a wherestring, similarly to how it is done in search_good_db.
    # the same process is used twice and this should probably be its own function.
    wherestring = ''
    for imageid in processed_imageset:
        if len(wherestring) > 0:
            wherestring += ' OR '
        wherestring += ('id = ' + str(imageid))

    if len(wherestring) == 0:
        wherestring="null"
    result = _db.select('images',where=wherestring)
    return _render.images(result)