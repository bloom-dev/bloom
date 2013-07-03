import os
import json
from datetime import datetime
import warnings

#------
import utility



#===============================================================================
# Configuration class
#    For project-wide configuration files imported as dict-style objects.
#===============================================================================
class Configuration(object):
    '''
    Essentially, an elaborate dict for configuration parameters, with some additional
    functionality.
    '''
    '''Example:
    config = Configuration(db="chemicals",table_names=['pubchem','native'])
    config.user = "root"
    
    print(config)
    #{'table_names': ['pubchem', 'native'], 'db': 'chemicals', 'user': 'root'}         
    config.write("test_config.json")
    file_config = Configuration.read("test_config.json")
    actually_a_dict = file_config.dict()
    print(actually_a_dict)
    #{'table_names': ['pubchem', 'native'], 'db': 'chemicals', 'user': 'root'}
    print(config.pretty())
    #{
    #'table_names', list [2] = ['pubchem', 'native']
    #'db', str [9] = chemicals
    #'user', str [4] = root
    #}
    '''
    @staticmethod
    def read(file_name,file_type=None):
        '''Read a file exported by Configuration().write(). Can also read many JSON/XML files. 
        '''
        if file_type == None:   
            _, ext = os.path.splitext(file_name.lower())#Try to get file type from extension
            file_type = ext[1:] #remove the '.' at the front
        
        #[] Turn the file contents into a dict
        if file_type == "json":
            conf_dict = utility.convert_to_string(json.load(open(file_name,'r')))    #this should actually return a dict
        elif file_type == "xml":
            conf_dict = utility.import_xml_config(file_name)
        else:
            warnings.warn("Could not read Configuration file: Configuration.read({0})".format(),
                          Warning,
                          stacklevel=2)
        
        return Configuration(**conf_dict)
    @staticmethod
    def read_config(file_name,file_type=None):
        '''Read a config file, by remove the root node (which is usually just 'configuration'.'''
        config = Configuration.read(file_name,file_type)
        conf_dict = config.dict().itervalues().next()    #remove root node
        return Configuration(**conf_dict)
    #--------
    def __init__(self,**kwargs):
        for key,val in kwargs.items():
            self.__setattr__(key,val)
    def __getitem__(self,key):          #make self['key'] ==> self.key
        return self.__getattribute__(key)       #__getattribute__() should be defined by default for anything inheriting from object
    def __setitem__(self,key,value):    #make self['key']=x  ==> self.key = x
        #Note: This can cause problems if user overwrites method names
        self.__setattr__(key,value)
    def __setattr__(self, name, value):
        if name in utility.get_method_names(self):
            raise IndexError("'{0}' is a method name (Configuration().{0}), and should not be overwritten.\n".format(name))
        #super(Configuration,self).__setattr__(name, value)
        self.__dict__[name] = value
        #self.__dict__[name] = repr(value)[1:-1]     #Escape characters, but do not include extra quotes
        
        #return object.__setattr__(self, *args, **kwargs)
    def new(self,file_name):
        self = Configuration.read(file_name)
    def write(self,file_name,file_type=None):
        if file_type == None:   
            _, ext = os.path.splitext(file_name.lower())#Try to get file type from extension
            file_type = ext[1:] #remove the '.' at the front
        conf = utility.get_attributes(self)
        if file_type == "json":
            json.dump(conf,open(file_name,"w"))
        elif file_type == "xml":
            with open(file_name,"w") as f:
                f.write(utility.dict2xml(conf))
        else:
            print("Unrecognized file_type in {0}.write({1},{2}).".format(self.__class__,file_name,file_type))
    def __repr__(self):
        return str(utility.get_attributes(self))
    def __str__(self):      #Prints more formally then it's dict form.
        str_form = "{\n"
        for key,val in utility.get_attributes(self).items():
            if type(val) is str:
                str_form += "{0}: '{1}'\n".format(key,val)
            else:
                str_form += "{0}: {1}\n".format(key,val)
        str_form += "}\n"
        return str_form
    def __iter__(self):
        for attr in utility.get_attributes(self):
            yield attr
    def items(self):
        for attr,val in utility.get_attributes(self).items():
            yield attr,val
    def dict(self):
        return dict(list(self.items()))
    def json(self):
        return json.dumps(utility.get_attributes(self))
    def xml(self):
        return utility.dict2xml(utility.get_attributes(self))
    def pretty(self,sep="\n"):
        #@todo: make recursive, and account for indentation.
        string_lines = []
        #string_form = "{\n"
        
        #If I wanted to make this recursive, it would go here:
        #for key,val in self.dict().items():
        #    string_lines.append(pretty_recurse(val,tab_depth=0)
#        def pretty_recurse(val,tab_depth,string_lines)
#            if isinstance(val,collections.Iterable) and not isinstance(val,str):
#                #Actually... need to account for dict-type vs list/tuple-type
#                #dict-type:
#                if hasattr(
#                string_lines.append( pretty_recurse(val,tab_depth+1,string_lines) )
#            else:
#                
#                return "'{0}', type: {1} ({2}), value = '{3}'".format(key,val_type,val_len,val)
        string_lines.append( "{" )
        for key,val in self.dict().items():

            try:
                val_type = str(type(val)).split("\'")[1]
                val_len = len(val)
            except:
                val_type = "Unknown type"
                val_len = "NA"
            #string_form += "'{0}', type: {1} ({2})".format(key,val_type,val_len) 
            if type(val) is str:
                #string_form += ", value = '{3}'\n".format(val)      #Add string quotes
                line_string = "'{0}', type: {1} ({2}), value = '{3}'".format(key,val_type,val_len,val)
            else:
                #string_form += ", value = {3}\n".format(val)
                line_string = "'{0}', type: {1} ({2}), value = {3}".format(key,val_type,val_len,val)
            string_lines.append( line_string )
        string_lines.append("}")
        #string_form += "}\n"
        
        string_form = sep.join(string_lines)
        return string_form
        #if return_string:
        #    return string_form
        #else:
        #    print(string_form)



#@in-development:
def pretty_recursive(obj,string_form="",indent=0,sep_str="\n",ind_str="\t\t"):
    #@todo: account for more nuanced rules for when to place newlines
    #        (~think of HTML tags)
    #        ~ whenever a complex object does NOT only contain simple things (strings, numbers)
    #        OR at end of complex object (dict,list)
    #@todo: insert {} and []
    
    #[] Priority sequence: strings, numbers, dict-like, iterable
    #[] Complex object --> iterate

    if isinstance(obj,(str,)):
        #string_form += "'"+obj+"'"
        return "'"+obj+"'"
    elif isinstance(obj,(int,long,float,complex)):
        #string_form += str(obj)
        return str(obj)
    elif hasattr(obj,"items"):  #dict-like items
#        string_form += sep_str + ind_str * indent
        string_form = sep_str + ind_str * indent + "{"      #open bracket
        for key,value in obj.items():
            string_form += ind_str * indent + "'" + str(key) + "': "
            string_form += pretty_recursive(value,string_form,indent+1,sep_str,ind_str) + ", "
        string_form += sep_str + ind_str * indent + "}" +sep_str        #Close bracket
        return string_form
    elif hasattr(obj,"__iter__"):
        #string_form += sep_str + ind_str * indent
        string_form = sep_str + ind_str * indent + "["      #open bracket
        temp = ", ".join(pretty_recursive(value,string_form,indent+1,sep_str,ind_str)
                for value in obj)
        string_form += temp     #Content
        string_form += "]" + sep_str       #Close bracket
        return string_form
    else: #Unrecognized type
        #string_form += str(obj)
        return str(obj)
    #return string_form

def pretty(d,indent=0):
    for key, value in d.iteritems():
        print '\t' * indent + str(key)
        if isinstance(value, dict):
            pretty(value, indent+1)
        else:
            print '\t' * (indent+1) + str(value)


class Organizer(object):
    '''Simple object allowing you to add your own attributes.
    Also see similar State_Organizer() class in generator_utility.py, which
    has altered functions for handling generator-pipeline functions.
    
    See the related Configuration() class, which is a similar class with more features.'''
    def __init__(self,**kwargs):
        for key,val in kwargs.items():
            self.__setattr__(key,val)
    def __repr__(self):
        return str(self.__dict__)
    def __str__(self):
        return str(self.__repr__())
    def update(self,**kwargs):
        '''Adds or updates a series of keyword parameters to the attributes of this object.'''
        for k,v in kwargs.items():
            self.__setattr__(k,v)
    def apply(self,attr_name,func):
        if hasattr(self,attr_name):
            self.__setattr__(attr_name,func(self.__getattr__(attr_name)))
    def add(self,attr_name,attr_value=None):
        if not hasattr(self,attr_name):         #if attribute already exists - do not add it
            self.__setattr__(attr_name,attr_value)

class File_Organizer(object):
    pass

class Table(object):
    '''Simply used to organize table data. Depends on mysql_connection.py.
    >>>'''
    #@note: Consider making mysql_con an instance variable. Currently, it's passed to several functions seperately
    def __init__(self,mysql_con=None,db=None,table=None):
        #mysql_con - instance of class MySQL_Connection() from custom package mysql_connection
        if (mysql_con is not None) and (db is not None) and (table is not None):  #if all 3 not specified - leave setting them to the user
            self.set_fields(mysql_con, db, table)
    def set_fields(self,mysql_con,db,table):
        self.db = db
        self.table = table
        self.qualified = self.db + "." + self.table
        #if mysql_con.table_exists(self.qualified):    #was not working
        if mysql_con.table_exists(self.table,self.db):
            self.columns = mysql_con.get_column_names(self.table,self.db)
        else:
            self.columns = None
        #self.mapped_columns = [map_inclusive(elm,_cmap) for elm in self.columns]    #@deprecated: 
        #self.size = mysql_con.table_size(self.db+"."+self.table)
        
    def find_size(self,mysql_con):
        self.size = mysql_con.table_size(self.db+"."+self.table)
        return self.size
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        string_form = "Name: {0}\nColumns: {1}".format(self.qualified,self.columns)#", ".join(self.columns)
        string_form += "\n-----"
        return string_form
    def primary_key(self,mysql_con):
        for column_dict in mysql_con.run("DESCRIBE {0}".format(self.db+"."+self.table)):
            #Results: one tuple per column, each tuple contains a dict
            #Example column dict: {'Extra': 'auto_increment', 'Default': None, 'Field': 'cd_id', 'Key': 'PRI', 'Null': 'NO', 'Type': 'int(11)'}
            if column_dict['Key'] == 'PRI':
                self.primary_key = column_dict['Field']
                return column_dict['Field']
    
        
class Debug(object):
    '''Just a C-style struct object used simply to group debugging variables.'''
    def __init__(self,flag=True):
        self.flag = flag
        self.log_files = []
    def __nonzero__(self):
        return self.flag
    def set_log(self,log_file):
    #    Associates a log file with this debug object.
        self.log_files.append( log_file )
    def log(self,message,log_file=None):
        '''
        Writes to a log file associated with this debug object.
        If no log file name supplied, uses the first log_file in self.log_files.
        '''
        if log_file is None:
            try:
                log_file = self.log_files[0]
            except IndexError:      #if empty
                print "A log file name is not specified."
                self.set_log("debug_default.log")
                log_file = self.log_files[0]
        with open(log_file,'a') as logf:
            logf.write("{0}\n{1}".format(datetime.datetime.now(),message))
    #       #... append message to log file, along with date information. 



#actually, could probably just use:
# = file_utility.File_Reader(in_path,mode=None)
class FilePath(object):
    def __init__(self,in_path):
        self.in_path = in_path
        self.exists = os.path.exists(in_path)
        self.ftype = 'dir' if os.path.isdir(in_path) else 'file'
        (self.dir,self.full_name) = os.path.split(in_path)   
        (self.name,self.ext) = os.path.splitext(self.full_name)
        
        
        self.dir_parts = (self.dir).split(os.path.sep)
        #For directories:
        #   self.full_name == self.name    the final directory (~after the last '/')
        #   self.ext                        blank
        #For files:
        #   self.full_name                  NAME.EXT
        #   self.name                       NAME        self.ext        ".EXT"
    def check(self):
        self.exists = os.path.exists(self.in_path)
        if self.exists is False:
            raise IOError("No such file or directory: '{0}'".format(input.in_path))
        

