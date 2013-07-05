import os
import logging
import sqlite3 as sql
#----- Custom Modules
from organizers import Configuration     #Used to read JSON/XML configuration files.


#[] Global Configuration Variables
_config = Configuration.read("settings.json")


def add_basic_tags(image_name):
    #should add a tag for the file extension
    #Should also add any tags which are calculated/derived 
    #    from direct file data - if any exist
    pass

def add_tag(new_tag,image_name=None,image_id=None):
    if (image_name is None) and (image_id is None):
        raise Exception("Cannot add tag {0}-at least one of image_name or image_id must be provided.".format(new_tag))
    

if __name__=="__main__":
    pass