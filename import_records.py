import os,sys
import sqlite3 as sql
import shutil
import hashlib
import datetime


#import sys
#----- Custom Modules
sys.path.append('modules/') #Put the modules directory in the pythonpath
from organizers import Configuration     #Used to read JSON/XML configuration files.
from sql_tools import SQLite


#[] Global Configuration Variables
_config = Configuration.read("configs/settings.json")

#[] Naming for SQL commands: Use like
#Example: sql_cmd = "SELECT {images_id_col} FROM {images_table};".format(**_naming.dict())
#_naming = {
#    'tags_table':'tags',
#    'images_table':'images',
#    'join_table':'images_tags',
#    'join_table_id_col':'images_tags_id',
#    'images_id_col':'images_id',
#    'tags_id_col':'tags_id',
#    'tags_name_col':'name'
#    }
_naming = Configuration.read("configs/sql_naming.json")

#@deprecated: by new SQLite object
#def table_exists(cxn,table_name):
#    
#    results = cxn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{0}';".format(table_name))
#    if (results.fetchall()):   #if non-empty
#        return True
#    else:
#        return False
    
def setup_default_tables(cxn=None,overwrite=True):
#    if cxn is None:
#        cxn = sql.connect(_config['image_database'])
#    cursor = cxn.cursor()
    if cxn == None:
        cxn = SQLite(_config['bloom_db'])
    
    #For each table
    for tkey,tinfo in _config['tables'].items():
        table_name = tinfo['name']
        
        if (overwrite==True) and cxn.table_exists(table_name):
            sql_drop = "DROP TABLE "+table_name
            cxn.execute(sql_drop)
        
        columns_spec = []
        
        #Add columns
        cols = [" ".join([col_name,col_type,col_traits]) 
                       for col_name,col_type,col_traits 
                       in tinfo['columns']]

        columns_spec.extend(cols)
        #columns_spec.extend(constraints)
        spec_string = ",".join(columns_spec)
        
        #Asemble SQL & execute
        sql_create = "CREATE TABLE {0} ({1});".format(
                table_name,spec_string)
        cxn.execute(sql_create)
        

def import_testing_db():
    _testing = Configuration.read('configs/test_data.json')
    cxn = SQLite(_config['bloom_db'])
    for file_name,tags in _testing['images']:
        path = _testing['in_dir']+os.path.sep+file_name
        if not os.path.exists(path):
            print("Image file not found at {0}, skipping.".format(path))
            continue
        #[] Import image
        image_id = import_image(path,cxn)
    
        #[] Import tags
        #    be sure to add: 'all'
        tag_ids = []
        tags.append('all')  #Add an 'all' tag - for searching purposes
        for tag in tags:
            tag_id = import_tag(tag,cxn)
            #[] Get tag ids
            tag_ids.append( tag_id )
            #[] Create images_tags record
            import_image_tag(image_id,tag_id,cxn)
        
    cxn.commit()

def apply_tags(image_id,tags,cxn):
    #[] Import tags
    #    be sure to add: 'all'
    tag_ids = []
    tags.append('all')  #Add an 'all' tag - for searching purposes
    for tag in tags:
        tag_id = import_tag(tag,cxn)
        #[] Get tag ids
        tag_ids.append( tag_id )
        #[] Create images_tags record
        import_image_tag(image_id,tag_id,cxn)

def import_image_tag(image_id,tag_id,cxn):
    #[] Check if it already exists

    #@deprecated: This variable is no longer needed    
    sql_select = '''SELECT {join_table}.{images_id_col},{join_table}.{tags_id_col}
                    FROM {join_table}
                    WHERE {images_id_col} = {image_id}
                    AND {tags_id_col} = {tags_id};'''.format(
                        image_id=image_id,tags_id=tag_id,**_naming.dict())
    record = {_naming['images_id_col']:image_id,
              _naming['tags_id_col']:tag_id}
    if not cxn.record_exists(record,_naming['join_table']):
        #[] If not, create it
        cxn.insert(record,_naming['join_table'])
    else:
        print("Record for image_id={0}, tag_id={1} already exists in table {2}".format(image_id,tag_id,_naming['join_table']))
        
        
    
    
def import_tag(tag,cxn):
    '''Adds tag to db (it not already present), and returns it's tag_id.'''
    if cxn is None:
        cxn = SQLite(_config['bloom_db'])
    #cxn = sql.connect(_config['bloom_db'])
    #cursor = cxn.cursor()
    
    #[] Check if tag already exists
    #sql_select = "SELECT name from tags\
    #                WHERE name = '{0}';".format(tag)
    #cursor.execute()
    #if (cursor.fetchone()):
    if cxn.record_exists({'name':tag},_naming['tags_table']):
        print("Tag named '{0}' already exists".format(tag))
    else:
        #[] If not, add it
        #cursor.execute("INSERT INTO tags (name)\
        #                VALUES ({0});".format(tag))
        #sql_insert = '''INSERT INTO tags (name)
        #                 VALUES ({0});'''.format(tag)
        #cxn.run(sql_insert)
        cxn.insert({'name':tag},_naming['tags_table'])

    #[] Return tag_id
    sql_select = '''SELECT {tags_id_col} FROM {tags_table}
                    WHERE {tags_name_col} = '{tag}';'''.format(
                        tag=tag,**_naming.dict())
    results = cxn.run(sql_select)
    #results = cxn.run("id FROM tags WHERE name = '{0}';".format(tag))
    #cursor.execute("SELECT id FROM tags WHERE name = '{0}';".format(tag))
    #result = cursor.fetchone()
    return results[0][0]

def import_image(old_full_path,cxn=None):
    '''Adds image to db (if it doesn't exist), and returns it's image_id.'''
    if cxn is None:
        cxn = SQLite(_config['bloom_db'])
    
    #[] Copy file to archive
    old_path, original_name = os.path.split(old_full_path)
    current_path = _config['image_archive'] + os.path.sep+original_name
    
    #[] Calculate values for image record:
    #    hash, date_uploaded, original_name, current_path
    hash = hash_file(old_full_path)
    upload_date = unicode(datetime.datetime.now())
    
    #[] Confirm that hash is not already in the db
#    sql_select_hash = "SELECT hash from images\
#                        WHERE hash = '{0}';".format(hash)     
#    cursor.execute(sql_select_hash)
#    result = cursor.fetchone()
#    if result:
    if cxn.record_exists({'hash':hash},_naming['images_table']):
        #@todo: Loging: This should really be a logging step
        print("Hash ({0}) for file named {1} already exists".format(hash,original_name))
    else:
        shutil.copyfile(old_full_path,current_path)
        
        #[] Create image record
        sql_insert = '''
            INSERT INTO {0}
            (original_name,current_path,hash,upload_date)
            VALUES ('{1}','{2}','{3}','{4}')'''.format(
                _naming['images_table'],
                original_name,current_path,hash,upload_date)
        cxn.execute(sql_insert)
        #cursor.execute(sql_insert)
    
    #[] Return image id
    sql_select = '''SELECT {images_id_col} FROM {images_table}
                    WHERE hash = '{hash}';'''.format(
                        hash=hash,**_naming.dict())
    results = cxn.run(sql_select)
    #cursor.execute(sql_select)
    #results = cursor.fetchone()
    return results[0][0]

def hash_file(file_path):
    with open(file_path,'rb') as f:
        data = f.read()
    filesize = os.path.getsize(file_path)
    #this is how git does it
    sha1 = hashlib.sha1("blob "+str(filesize)+"\0"+str(data))
    return sha1.hexdigest()


#------------------- Functions in Development
def import_directory(dir_path,tags=None):
    '''Imports all files in dir_path, and optionally adds 'tags' to each.''' 
    cxn = SQLite(_config['bloom_db'])
    #Get files - via generator list comprehension    
    files = (f for f in os.listdir(in_images_dir))      #The brackets make this into a generator ~delayed calculation
    for f in files:
        import_image(f,cxn)
        
def add_tags_to_files(file_list,tags=None):
    '''For each file in file_list, ensures it is imported,
    then applies all of 'tags'.'''
    pass

if __name__ == "__main__":
    #_params = Configuration(in_dir= "raw images"+os.path.sep)    #~local configuration variables
    
    #Establish SQL connection and build DB
    #cxn = sql.connect(_config['bloom_db'])
    cxn = SQLite(_config['bloom_db'])
    
    
    setup_default_tables(cxn)

    import_testing_db()

