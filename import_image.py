import os
import sqlite3 as sql
#----- Custom Modules
from organizers import Configuration     #Used to read JSON/XML configuration files.

#[] Global Configuration Variables
_config = Configuration.read("settings.json")

def setup_image_database(cxn=None):
    if cxn is None:
        cxn = sql.connect(_config['image_database'])
    
    #[] Check if table exists
    index_table = cxn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{image_index_table}';".format(**_config))
    
    #[] Setup index table
    if not index_table:
        sql_create = '''CREATE TABLE {image_index_table}
                        (id INTEGER NOT NULL AUTO_INCREMENT,
                        file_path varchar(255),
                        CONSTRAINT pk_id PRIMARY KEY (id)
                        )'''.format(**_config)
        cxn.execute(sql_create)
    
    return cxn

def table_exists(cxn,table_name):
    ret = cxn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{0}';".format(table_name))
    if (ret.fetchall()):   #if non-empty
        return True
    else:
        return False
    
def setup_default_tables(cxn=None):
    if cxn is None:
        cxn = sql.connect()
    
    
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
        
        #@deprecated: constraints not set up normally in SQLite
        #Add Constraints
#        constraints = [" ".join([const_name,const_type,const_targets])
#                       for const_name,const_type,const_targets
#                       in tinfo['constraints']]
        
        columns_spec.extend(cols)
        #columns_spec.extend(constraints)
        spec_string = ",".join(columns_spec)
        
        #Asemble SQL & execute
        sql_create = "CREATE TABLE {0} ({1});".format(table_name,spec_string)
        cxn.execute(sql_create)
        

#@incomplete    
def import_image(image_path,cxn=None):
    if cxn is None:
        cxn = setup_image_database()
        
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