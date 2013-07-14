#= The web server aspect of bloom

#----------- Standard Library 
import os
import re
#----------- Semi-Standard Library
import web					#web.py code, includes db access
import sqlite3 as sql		#can easily be replaced with other SQL
#----------- Custom Library
from organizers import Configuration     #Used to read JSON/XML configuration files.
import tag_search

#setup for web.py
_config = Configuration.read("settings.json")
_db = web.database(dbn='sqlite',db='bloom.db')
_render = web.template.render('templates/',base='wrapper')
_render_naked = web.template.render('templates/')
#---------- Parameters
_param = Configuration()


#============================
#  URL Redirection
#============================
_urls = (
	'/','index',
	'/tags','tags',
	'/collections','comingsoon',
	'/upload','upload',
	'/image/(.+)','image',
	'/list/(.+)','search',
	'/list(/)?', 'search'
)

#============================
#  Web-Handler Functions
#============================
# The folllowing are each classes with two potential methods. GET and POST. I should *probably* move
# some of the methods that are written above to instead be inside the appropriate class but fuck the
# rules (aka do it later)
#
# The classes are referred to by the _urls tuple. When a page is called with the path in the tuple,
# one of these classes is also called.
class search:
	def GET(self,tags_string=''):
		if tags_string == '' or tags_string == None or tags_string == '/':
			result = _db.select('images')
			return _render.images(result)
		else:
			return tag_search.sqlite_is_bad(self,tags_string)
			#return tag_search.sqlite_is_bad(self,tags_string)
			
			#return tag_search.search_good_db(self,tags_string) #-do this is you're using postgre, MSSQL, or oracle

	def POST(self,tags=''):
		x = web.input(searchstr='')
		web.seeother('/list/'+x.searchstr.replace(' ','_'))

class index:
	def GET(self):
		i = web.input(name=None)
		return _render.index(i.name)

class images:
	def GET(self):
		image_list = _db.select('images')
		return _render.images(image_list)

class tags:
	def GET(self):
		tag_list = _db.query(' SELECT ImageTags.TagID, Tags.name, count(*) as count FROM ImageTags INNER JOIN tags ON ImageTags.tagID = Tags.ID GROUP BY Tags.ID')
		#tag_list = _db.select('tags')
		return _render.tags(tag_list)
class image:
	def GET(self,imageID):
		image_data = _db.select('images',where='ID = '+imageID)
		image_tags = _db.query('SELECT ImageID,TagID,Name FROM ImageTags INNER JOIN Tags ON ImageTags.tagID = Tags.ID WHERE ImageID = '+imageID)
		for image_d in image_data:
			return _render.image(image_d, image_tags)
class upload:
	def GET(self):
		return _render.upload()
	def POST(self):
		filedir = 'static/archive' #directory to store the files in.
		i = web.webapi.rawinput()
		files = i.userimage
		if not isinstance(files, list):
			files = [files]
		for f in files:
			filepath=f.filename.replace('\\','/')
			filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
			fout = open(filedir +'/'+ filename,'wb') # creates the file where the uploaded file should be stored
			fout.write(f.file.read()) # writes the uploaded file to the newly created file.
			fout.close() # closes the file, upload complete.
			something = _db.insert('images',file_path=filename)
			make_thumbnail(filename)
		raise web.seeother('/images')

class comingsoon:
	def GET(self):
		return _render.comingsoon()

# run the server.
def start():
	app = web.application(_urls,globals())
	app.run()


#============================
#   Utility Functions
#============================
def make_thumbnail(filename):
	os.system(r'convert static/archive/'+ filename +' -auto-orient -thumbnail 150x150 -unsharp 0x.5 static/archive/thumbnails/'+filename)

#@deprecated: no longer used
def get_tagID(tagname):
	rows = _db.select('tags',where='name='+tagname)
	for r in rows:
		return r.id



#============================
# Oakland's Cleanup Code
#============================
def grouper(iterable, n, fillvalue=None):
    '''Collect data into fixed-length chunks or blocks.'''
    # grouper('ABCCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue,*args)
    
def get_section(page_sz=10):
    total = range(100)
    for section in grouper(total,page_sz):
        yield section

def get_tag_data(tag_name,column_name='id',page_size=None):
	_db.select('tags',where='name '+tag_name)
	while False:
		pass
	
def get_tag_ids(tag_name):
	'''Returns a list of tag ids associated with 'tag_name'.'''
	_db.select('tags',where='name='+tag_name)



if __name__ == "__main__":
	boobset = set()
	boobset.add(1)
	boobset.add(2)
	iceset = set()
	iceset.add(1)
	iceset.add(4)
	iceset.add(3)
	paraset = set()
	paraset.add(3)
	#print(sqlite_needs_help("(boobs or ice) and parasite",{'boobs':boobset, 'ice':iceset, 'parasite':paraset}))
	print(tag_search.sqlite_is_bad(None,'boobs or icecream'))


