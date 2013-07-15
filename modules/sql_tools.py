import sys,os
#sqlite3 & MySQLdb are imported inside their respective classes

#------ Custom Modules
from iter_utility import find_next,find_last

#@todo: make these classes have the same function listing


class SQLite():
    def __init__(self,database_path):
        import sqlite3
        self._cxn = sqlite3.connect(database_path)
        self._cursor = self._cxn.cursor()
    def execute(self,sql_command):
        return self._cursor.execute(sql_command)
    def run(self,sql_command):
        '''Sugar for combining .execute(sql_command) and .get_results() for simplicity of writing.'''
        self._cursor.execute(sql_command)
        return self._cursor.fetchall()
    def commit(self):
        self._cxn.commit()
    def _db_spec(self):
        rows = cxn.run('''SELECT * FROM sqlite_master WHERE type = 'table';''')
        spec = {}
        for row in rows:
            table_name = row[1]
            create_table_sql = row[4]
            
            F = find_next(create_table_sql,'(')
            L = find_last(create_table_sql,')')
            col_spec = create_table_sql[F+1:L]
            
            for tag_spec in col_spec.split(','):
                spec_parts = tag_spec.split(' ')
                spec[table_name] = {'name':spec_parts[0],
                                    'type':spec_parts[1],
                                    'extras':spec_parts[2:]
                                    }
        return spec
    def table_names(self):
        self._cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        rows = self._cursor.fetchall()
        table_names = [row[0].encode('ascii') for row in rows]
        return table_names
    def column_names(self,table_name):
        self._cursor.execute("SELECT * FROM '{0}' LIMIT 1;".format(table_name))
        self._cursor.fetchone()
        rows = self._cursor.description
        column_names = [row[0] for row in rows]
        return column_names
    def table_exists(self,table_name):
        self._cxn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{0}';".format(table_name))
        if (self._cursor.fetchone()):    #if non-empty
            return True
        else:
            return False
    def column_types(self,table_name=None):
        if table_name == None:  #Return all tables
            return [(table['name'],table['type']) for table in self._db_spec()]
        else:
            spec = self._db_spec()
            for table_spec in spec:
                if table_spec['name'] == table_name:
                    return table_spec['type']
            else:   #If table not found
                return None
            
    def record_exists(self,record,table):
        ''' record: should be a dict. '''
        where_clause = " AND ".join("{0} = '{1}'".format(column,value) for column,value in record.items())
        sql_select = '''SELECT * FROM {0} WHERE {1};'''.format(table,where_clause)
        
        self._cursor.execute(sql_select)
        if (self._cursor.fetchone()):
            return True
        else:
            return False
    def insert(self,record,table):
        sql_insert = '''INSERT INTO {0} ({1}) VALUES ({2});'''.format(
            table,
            ",".join(record.keys()),
            ",".join("'{0}'".format(val) for val in record.values()))
        self.execute(sql_insert)
        
    #----------- Unfinished functions
    def select(self,record,tables,where=None):
        '''Presently this does not handle joins.
        record: a list of column names
        where: a dictionary defining records'''
        raise Exception("This function is unfinished")
        #[] Build WHERE clause
        #@todo: make this an abstracted, private-module function to construct where clauses
        if where == None:
            where_clause = ''
        elif type(where) == str:
            if where_clause[0:6] != 'WHERE':
                where_clause = ' WHERE '+where
            else:
                where_clause = ' '+where
        elif type(where) == dict:
            where_clause = " WHERE "+" AND ".join("{0} = '{1}'".format(column,value) for column,value in record.items())
            
        
        sql_select = '''{0} {1}{2};'''.format(
            select_columns,from_clause,where_clause)

class MySQL:
    def __init__(self,host=None,user=None,passwd=None,default_db=None,mysql_config_file=None,unix_socket=None):
        '''Supplying mysql_config_file is an alternative to directly supplying host,user,passwd,default_db.
        warnings: whether or not warnings will be shown when executing SQL via .run() or .execute()
        '''
        #(self.curs,self.cxn) = initialize(mysql_config_file)
        #(self.mysql_cursor,self.mysql_cxn) = initialize()
        if mysql_config_file is None:
            (class_dir,class_file_name) = os.path.split(__file__)
            mysql_config_file = class_dir + "/mysql_connection_config.json"
        if not os.path.exists(mysql_config_file):
            raise Exception("File not found: {0}".format(mysql_config_file))
        
        self._parameters = {}
        self._parameters = self._get_connection_parameters(host=host, user=user, passwd=passwd, default_db=default_db, unix_socket=unix_socket,mysql_config_file=mysql_config_file)
        
        if 'linux' in sys.platform:
            (self.mysql_cursor,self.mysql_cxn) = self.initialize(self._parameters['host'],self._parameters['user'],self._parameters['passwd'],self._parameters['default_db'],unix_socket=self._parameters['unix_socket'])
        else:
            (self.mysql_cursor,self.mysql_cxn) = self.initialize(self._parameters['host'],self._parameters['user'],self._parameters['passwd'],self._parameters['default_db'])
    
    def initialize(self,host,user,passwd,database,unix_socket=None):
        #@todo: Update this to use defaults read from self._parameters['host'],'user','passwd','default_db'
        import MySQLdb
        mysql_cxn = MySQLdb.connect(host,user,passwd,unix_socket=unix_socket)
        mysql_cursor = mysql_cxn.cursor(MySQLdb.cursors.DictCursor)
        mysql_cursor.execute("USE {0}".format(database))
        return (mysql_cursor,mysql_cxn)
    def close(self):
        self.mysql_cursor.close()
        self.mysql_cxn.close()
    def execute(self,sql_command):
        ret_val = self.mysql_cursor.execute(sql_command)
        return ret_val
    def run(self,sql_command):
        '''Sugar for combining .execute(sql_command) and .get_results() for simplicity of writing.'''
        self.mysql_cursor.execute(sql_command)
        return self.mysql_cursor.fetchall()
    def get_results(self):
        results = self.mysql_cursor.fetchall()
        return results
    def commit(self):
        self.mysql_cxn.commit()
    def _get_connection_parameters(self,host=None,user=None,passwd=None,default_db=None,unix_socket=None,mysql_config_file='mysql_connection_config.json'):
        '''Often reads from mysql_config_file='mysql_connection_config.json'.
        This function is kludge-y and very inelegant....
        Example mysql_connection_config.json:
        {
        "host":"localhost",
        "user":"USER",
        "passwd":"PASSWORD",
        "unix_socket":"/tmp/mysql.sock",
        "default_db":"DB_NAME"
        }
        Another common "unix_socket":"/var/lib/mysql/mysql.sock"
        '''
        _parameters = {}

        #Check for parameters being set - with optional config file to be used if any individual parameter not specified
        config_exists = os.path.isfile(mysql_config_file)
        if config_exists:
            json_data = json.load(open(file_name))
            _config = convert_to_string(json_data)
            #_config = utility.read_json(mysql_config_file)
        #Check param 'host'
        if host is None:
            if config_exists is False:
                raise Exception("MySQL connection config file ({0}) not found.".format(os.getcwd() + '/'+mysql_config_file))
            else:
                _parameters['host'] = _config['host']   #use connection file for host
        else:
            _parameters['host'] = host      #use parameter for host
        #Check param 'user'
        if user is None:
            if config_exists is False:
                raise Exception("MySQL connection config file not found.")
            else:
                _parameters['user'] = _config['user']   #use connection file for user
        else:
            _parameters['user'] = user      #use parameter for user
        #Check param 'passwd'
        if passwd is None:
            if config_exists is False:
                raise Exception("MySQL connection config file not found.")
            else:
                _parameters['passwd'] = _config['passwd']   #use connection file for passwd
        else:
            _parameters['passwd'] = passwd      #use parameter for passwd
        #Check param 'default_db'
        if default_db is None:
            if config_exists is False:
                raise Exception("MySQL connection config file not found.")
            else:
                _parameters['default_db'] = _config['default_db']   #use connection file for passwd
        else:
            _parameters['default_db'] = default_db      #use parameter for passwd
        #if 'linux' in sys.platform[0:5]:
        if unix_socket is None:
            if config_exists is False:
                raise Exception("MySQL connection config file not found.")
            else:
                _parameters['unix_socket'] = _config['unix_socket']   #use connection file for unix_socket
        else:
            _parameters['unix_socket'] = unix_socket      #use parameter for passwd
        
        return _parameters

    def get_table_names(self,database_name=None):
        if database_name is None:
            self.mysql_cursor.execute("SHOW TABLES")
        else:
            self.mysql_cursor.execute("SHOW TABLES in {0}".format(database_name))
        
        rows = self.mysql_cursor.fetchall()
        table_names = [row.values()[0] for row in rows]
        return table_names

    def get_column_names(self,table_name,database_name=None):
        try:
            if database_name is None:
                self.execute("DESCRIBE {0}".format(table_name))
            else:
                self.execute("DESCRIBE {1}.{0}".format(table_name,database_name))
        except Exception:
            print "Could not find the table called {0}.".format(table_name)
            raise
        results = self.get_results()
        column_names = [row['Field'] for row in results]
        return column_names
    def get_column_types(self,table_name,database_name=None):
        try:
            if database_name is None:
                self.mysql_cursor.execute("SHOW FIELDS FROM {0}".format(table_name))
            else:
                self.mysql_cursor.execute("SHOW FIELDS FROM {0}.{1}".format(database_name,table_name,database_name))
        except Exception:
            print "Could not find the table called {0}.".format(table_name)
            raise
        results = self.mysql_cursor.fetchall()
        columns_and_types = {}
        for res in results:
            #column_names.append(res['Field'])
            #column_types.append(res['Type'])
            columns_and_types[res['Field']] = res['Type']
        return columns_and_types

    def table_exists(self,table_name,database=None):
        if database is None:
            self.execute("SHOW TABLES LIKE '{0}'".format(table_name))
        else:
            self.execute("SHOW TABLES IN {0} LIKE '{1}'".format(database,table_name))
        results = self.get_results()
        if len(results) > 0:
            return True
        else:
            return False
    def table_size(self,table_name):
        sql_size = "SELECT count(*) FROM {0};".format(table_name)
        self.execute(sql_size)
        results = self.get_results()
        
        if not len(results):
            return "0"      #if no results found
        else:
            for key,value in results[0].items():
                count_cache = value     #for some reason, it requires wrangling to get the result in a simple format.
                return int(count_cache)
    def drop_table(self,table_name):
        if not self.table_exists(table_name):
            return "Table {0} does not exist in db {1}".format(table_name,self._parameters['default_db'])
        try:
            self.execute("DROP TABLE {0}".format(table_name))
            return ""
        except Exception as Ex:
            return "Error while attempting to drop table {0}.\nReceived exception: {1}.".format(table_name,Ex)
    def find_primary_key(self,mysql_cursor,db,table):
        '''Finds a primary key in db.table, using mysql_cursor. Assumes only one primary key.'''
        #mysqlConnection.run()
        mysql_cursor.execute("DESCRIBE {0}".format(db+"."+table))
        results = mysql_cursor.fetchall()   
        #Results: one tuple per column, each tuple contains a dict
        #Example column dict: {'Extra': 'auto_increment', 'Default': None, 'Field': 'cd_id', 'Key': 'PRI', 'Null': 'NO', 'Type': 'int(11)'}
        for column_dict in results:
            if column_dict['Key'] == 'PRI':
                return column_dict['Field']
    
    def insert_dict(self,table_name,data_dict):
        '''Adds contents of dictionary to a table. keys() define columns.'''        
        table_columns = self.get_column_names(table_name)   #get columns of table
        valid_data_dict = dict((k,v) for k,v in data_dict.items()
                               if k in table_columns)   #Filter out data keys(~columns) not in the table
        if valid_data_dict == {}:
            return None
        else:
            sql_insert = '''INSERT INTO {table} ({columns})
                            VALUES ('{values}');'''.format(
                                                        table   = table_name,
                                                        columns = ', '.join(valid_data_dict.keys()),
                                                        values  = "', '".join(valid_data_dict.values()))
            self.run(sql_insert)
            return sql_insert
    
    def row_exists(self,table_name,data_dict):
        where_parts = ["{0} = '{1}'".format(col,val) for col,val in data_dict.items()]
        where_clause = ' AND '.join(where_parts) 
        sql_select = '''SELECT * FROM {0}
                        WHERE {1}
                        LIMIT 1;'''.format(table_name,where_clause)        
        results = self.run(sql_select)
        if len(results) != 0:
            return True
        else:
            return False
    
    def create_database(self,new_name):
        self.run("CREATE DATABASE {0}".format(new_name))
    def drop_database(self,db_name):
        self.run("DROP DATABASE {0};".format(db_name))
    def database_exists(self,db_name):
        sql_check = '''SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{0}';'''.format(db_name)
        results = self.run(sql_check)
        if len(results) != 0:
            return True
        else:
            return False
    def rename_database(self,old_name,new_name):
        if self.database_exists(new_name):
            raise Exception("Cannot rename {0} to {1}, because database {1} already exists.".format(old_name,new_name))
        else:
            self.create_database(new_name)
        if not self.database_exists(old_name):
            raise Exception("Cannot rename {0} to {1}, because database {0} does not exist.".format(old_name,new_name))
        table_names = self.get_table_names(old_name)
        
        for table in table_names:       #Rename each table
            sql_rename = '''RENAME TABLE {0}.{2} TO {1}.{2};'''.format(old_name,new_name,table)
            self.run(sql_rename)
            
        self.drop_database(old_name)
        
        
    #def call_linux(self):
    #    pass
    #def get_column_names(self):
    #    pass
    #def get_table_names(self):
    #    pass
    



#import unidecode
#unidecode.unidecode()
if __name__=="__main__":
    cxn = SQLite("../bloom.db")
    print(cxn.table_names())
    print(cxn.column_names('tags'))
    
    print(cxn._db_spec())
    print(cxn.run('''SELECT *
    FROM sqlite_master
    WHERE type = 'table';'''))