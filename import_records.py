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
        

def import_testing_db(cxn=None):
    if cxn==None:
        cxn = SQLite(_config['bloom_db'])
    _testing = Configuration.read('configs/test_data.json')
    
    for file_name,tags in _testing['images']:
        path = _testing['in_dir']+'/'+file_name
        #path = _testing['in_dir']+os.path.sep+file_name
        if not os.path.exists(path):
            print("Image file not found at {0}, skipping.".format(path))
            continue
        #[] Import image
        image_id = import_image(path,cxn)
    
        #[] Import tags
        tags.append('all')  #Add an 'all' tag - for searching purposes
        tag_ids = apply_tags(image_id,tags,cxn)
#        tag_ids = []
#        tags.append('all')  #Add an 'all' tag - for searching purposes
#        for tag in tags:
#            tag_id = import_tag(tag,cxn)
#            #[] Get tag ids
#            tag_ids.append( tag_id )
#            #[] Create images_tags record
#            import_image_tag(image_id,tag_id,cxn)
        
    cxn.commit()

def apply_tags(image_id,tags,cxn=None):
    if cxn == None:
        cxn = SQLite(_config['bloom_db'])
    #[] Import tags
    #    be sure to add: 'all'
    tag_ids = []
    for tag in tags:
        tag_id = import_tag(tag,cxn)
        #[] Get tag ids
        tag_ids.append( tag_id )
        #[] Create images_tags record
        import_image_tag(image_id,tag_id,cxn)
    return tag_ids

def import_image_tag(image_id,tag_id,cxn=None):
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
        
        
    
    
def import_tag(tag,cxn=None):
    '''Adds tag to db (it not already present), and returns it's tag_id.'''
    if cxn is None:
        cxn = SQLite(_config['bloom_db'])
    
    #[] Check if tag already exists
    if cxn.record_exists({'name':tag},_naming['tags_table']):
        print("Tag named '{0}' already exists".format(tag))
    else:
        #[] If not, add it
        cxn.insert({'name':tag},_naming['tags_table'])

    #[] Return tag_id
    sql_select = '''SELECT {tags_id_col} FROM {tags_table}
                    WHERE {tags_name_col} = '{tag}';'''.format(
                        tag=tag,**_naming.dict())
    results = cxn.run(sql_select)
    tag_id = results[0][0]
    return tag_id

def import_image(old_full_path,cxn=None):
    '''Adds image to db (if it doesn't exist), and returns it's image_id.'''
    if cxn is None:
        cxn = SQLite(_config['bloom_db'])
    
    #[] Copy file to archive
    old_path, original_name = os.path.split(old_full_path)
    current_path = _config['image_archive'] + '/' + original_name
    
    #[] Calculate values for image record:
    #    hash, date_uploaded, original_name, current_path
    hash = hash_file(old_full_path)
    upload_date = unicode(datetime.datetime.now())
    
    #[] Confirm that hash is not already in the db
    if cxn.record_exists({'hash':hash},_naming['images_table']):
        #@todo: Loging: This should really be a logging step
        print("Hash ({0}) for file named {1} already exists".format(hash,original_name))
    else:
        #[] Copy into archive
        shutil.copyfile(old_full_path,current_path)
        
        #[] Make thumbnail
        #current_dir,file_name = os.path.sep(current_path)
        #make_thumbnail(current_path)
        thumbnail(current_path)
        
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
    image_id = results[0][0]
    return image_id

def hash_file(file_path):
    with open(file_path,'rb') as f:
        data = f.read()
    filesize = os.path.getsize(file_path)
    #this is how git does it
    sha1 = hashlib.sha1("blob "+str(filesize)+"\0"+str(data))
    return sha1.hexdigest()

def make_thumbnail(current_path):
    current_dir,file_name = os.path.split(current_path)
    source = _config['image_archive']+file_name
    destination = _config['image_thumbnails']+file_name
    convert_cmd = '''convert {archive}{file_name} -auto-orient -thumbnail 150x150 \
        -unsharp 0x.5 {thumbnails}{file_name}'''.format(
            archive=_config['image_archive'].replace('/','\\'),
            file_name=file_name,
            thumbnails=_config['image_thumbnails'].replace('/','\\'))
    os.system(convert_cmd)   
    #os.system(r'convert {archive}{file_name} -auto-orient -thumbnail 150x150 \
    #    -unsharp 0x.5 {thumbnails}{file_name}'.format(
    #    archive=_config['image_archive'],
    #    file_name=file_name,
    #    thumbnails=_config['image_thumbnails']))


def thumbnail(current_path):
    from PIL import Image
    current_dir,file_name = os.path.split(current_path)
    source = _config['image_archive']+file_name
    destination = _config['image_thumbnails']+file_name

    size = 150, 150
    im = Image.open(source)
    im.thumbnail(size)
    im.save(destination,"jpg")
    
    print(destination)
#    for infile in sys.argv[1:]:
#        outfile = os.path.splitext(infile)[0] + ".thumbnail"
#        if infile != outfile:
#            try:
#                im = Image.open(infile)
#                im.thumbnail(size)
#                im.save(outfile, "JPEG")
#            except IOError:
#                print "cannot create thumbnail for", infile

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

