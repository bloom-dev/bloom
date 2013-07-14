import os
import sqlite3 as sql
import shutil
import hashlib
import datetime
#----- Custom Modules
from organizers import Configuration     #Used to read JSON/XML configuration files.

#[] Global Configuration Variables
_config = Configuration.read("settings.json")

def table_exists(cxn,table_name):
    results = cxn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{0}';".format(table_name))
    if (results.fetchall()):   #if non-empty
        return True
    else:
        return False
    
def setup_default_tables(cxn=None):
    if cxn is None:
        cxn = sql.connect(_config['image_database'])
    
    
    #For each table
    for tkey,tinfo in _config['tables'].items():
        table_name = tinfo['name']
        if table_exists(cxn,table_name):
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
        sql_create = "CREATE TABLE {0} ({1});".format(table_name,spec_string)
        cxn.execute(sql_create)

def import_testing_db():
    #original_file_location
    #copy to ./images/
    #add entry to bloom.db:images:[id,file_path]
    _testing = Configuration.read('test_data.json')
    for path,tags in _testing['images']:
        id = import_image(path)
        

#@incomplete    
def import_image(old_full_path,cxn=None):
    if cxn is None:
        cxn = sql.connect(_config['bloom_db'])
    
    #[] Copy file to archive
    old_path, original_name = os.path.split(old_full_path)
    current_path = _config['image_archive'] + image_name
    
    shutil.copyfile(image_path,current_path)
    
    hash = hash_file(current_path)
    upload_date = unicode(datetime.datetime.now())
    
    #[] Insert Image
    sql_insert = '''
        INSERT INTO {0}
        (original_name,current_path,hash,date_uploaded)
        VALUES ({1},{2},{3},{4})'''.format(
            _config['tables']['image']['name'],
            original_name,current_path,hash,date_uploaded)
    cxn.execute(sql_insert)
    
    sql_select = '''SELECT id FROM {0}
                    WHERE hash = {1}'''.format(
                        _config['tables']['image']['name'],
                        hash)
    result = cxn.execute(sql_select)
    print(result[0]['id'])
    
    #[] Calculate values for image record:
    #    hash, date_uploaded, original_name, current_path
    #[] Create image record
    #[] Get image id
    #[] Import tags
    #    be sure to add: 'all'
    #[] Get tag ids
    #[] Create images_tags record
    #Set 

def file_hash(file_path):
    with open(file_path,'rb') as f:
        data = f.read()
    filesize = os.path.getsize(file_path)
    #this is how git does it
    sha1 = hashlib.sha1("blob "+filesize+"\0"+data)
    return sha1.hexdigest()

if __name__ == "__main__":
    _params = Configuration(in_dir= "raw images"+os.path.sep)    #~local configuration variables
    
    #Establish SQL connection and build DB
    cxn = sql.connect(_config['bloom_db'])
    
    
    setup_default_tables(cxn)

    import_testing_db()

    #Get files - via generator list comprehension    
    files = (f for f in os.listdir(in_images_dir))      #The brackets make this into a generator ~delayed calculation
    for f in files:
        import_image(f,cxn)