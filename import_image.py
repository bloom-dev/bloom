import os
import sqlite3 as sql
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
        

#@incomplete    
def import_image(image_path,cxn=None):
    if cxn is None:
        cxn = sql.connect(_config['image_database'])
        
    #[] Insert Image
    sql_insert = '''INSERT INTO {0}
    (file_path)
    VALUES ({1})'''.format(_config['image_index_table'],image_path)
    cxn.execute(sql_insert)
    


if __name__ == "__main__":
    _params = Configuration(in_dir= "raw images"+os.path.sep)    #~local configuration variables
    
    #Establish SQL connection and build DB
    cxn = sql.connect(_config['bloom_db'])
    
    
    setup_default_tables(cxn)

    #Get files - via generator list comprehension    
    files = (f for f in os.listdir(in_images_dir))      #The brackets make this into a generator ~delayed calculation
    for f in files:
        import_image(f,cxn)