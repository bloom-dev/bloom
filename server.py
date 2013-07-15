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


#---------- Parameters
#setup for web.py
_config = Configuration.read("settings.json")
_db = web.database(dbn='sqlite',db='bloom.db')
_render = web.template.render('templates/',base='wrapper')
_render_naked = web.template.render('templates/')



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
			try:
				result = tag_search.search_tags(tags_string)
				_render.images(result)
			except Exception as exc:
				#Search error page needs to go here.
				raise
			#return tag_search.sqlite_is_bad(tags_string)
			#return tag_search.search_good_db(tags_string) #-do this is you're using postgre, MSSQL, or oracle

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
		jtable = _config['tables']['image_tag']['name']
		imagetable = _config['tables']['image']['name']
		tagtable = _config['tables']['tag']['name']
		tag_list = _db.query(' SELECT '+jtable+'.tags_id, '+tagtable+'.name, count(*) as count FROM '+jtable+' INNER JOIN tags ON '+jtable+'.tags_id = '+tagtable+'.id GROUP BY '+tagtable+'.id')
		#tag_list = _db.select('tags')
		return _render.tags(tag_list)
	
class image:
	def GET(self,imageID):
		image_data = _db.select('images',where='ID = '+imageID)
		image_tags = _db.query('SELECT Images_ID,Tags_ID,Name FROM images_tags INNER JOIN tags ON images_tags.tags_ID = tags.ID WHERE images_ID = '+imageID)
		for image_d in image_data:
			return _render.image(image_d, image_tags)
	def POST(self,imageID):
		i = web.input();
		tagc = _db.query('SELECT COUNT(*) as count FROM tags WHERE name = \"'+i.tag+'\"')

		for tag in tagc:
			if tag.count > 0:
				_db.insert('tags',name='\"'+i.tag+'\"',display='yes')
				break
		tagnum = _db.query('SELECT id FROM tags WHERE id = \"'+i.tag+'\"')
		for tagn in tagnum:
			tagnum = tagn.id
			break
		_db.insert('images_tags', images_id=i.imagenum, tags_id=tagnum)
		web.seeother('/image/'+i.imagenum)

		
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
			something = _db.insert('images',current_path=filename)
			make_thumbnail(filename)
		raise web.seeother('/list')

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
	os.system('convert \"'+os.path.normpath('static/archive/'+ filename) +'\" -auto-orient -thumbnail 150x150 -unsharp 0x.5 \"'+os.path.normpath('static/archive/thumbnails/'+filename)+'\"')


if __name__ == "__main__":
	mySearch = search()
	mySearch.GET('%')
	print(tag_search.search_tags('asfkljl3%44123-*3kl+lk_'))
	print(tag_search.search_tags('boobs or icecream'))

