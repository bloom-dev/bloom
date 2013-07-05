import sqlite3 as sql
#----- Custom Modules
from organizers import Configuration     #Used to read JSON/XML configuration files.
#[] Global Configuration Variables
_config = Configuration.read("settings.json")
#========
#This file should simply print info on the contents of the tables.
#Table name, table size, table columns, first 5 or so records.

if __name__=="__main__":
    pass
