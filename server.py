#= The web server aspect of bloom

#----------- Standard Library 
import os,sys
import re
#----------- Semi-Standard Library
import web					#web.py code, includes db access
import sqlite3 as sql		#can easily be replaced with other SQL
#----------- Custom Library
sys.path.append('modules/') #Put the modules directory in the pythonpath
from organizers import Configuration     #Used to read JSON/XML configuration files.
import tag_search


#---------- Parameters
#setup for web.py
_config = Configuration.read("configs/settings.json")
_db = web.database(dbn='sqlite',db='bloom.db')
_render = web.template.render('templates/',base='wrapper')
_render_naked = web.template.render('templates/')
_naming = Configuration.read("configs/sql_naming.json")
#_naming = {
#    'tags_table':'tags',
#    'images_table':'images',
#    'join_table':'images_tags',
#    'join_table_id_col':'images_tags_id',
#    'images_id_col':'images_id',
#    'tags_id_col':'tags_id',
#    'tags_name_col':'name'
#    }


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
				_render.images(list(result))
			except Exception as exc:
				#Search error page needs to go here.
				print("Error during tag search process.")
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
		sql_select = '''SELECT {join_table}.{tags_id_col}, {tags_table}.{tags_name_col}, count(*) as count
		FROM {join_table} INNER JOIN tags ON ImageTags.tagID = Tags.ID GROUP BY Tags.ID'''.format(
			**_naming.dict())
		tag_list = _db.query(sql_select)
		#tag_list = _db.query(' SELECT ImageTags.TagID, Tags.name, count(*) as count FROM ImageTags INNER JOIN tags ON ImageTags.tagID = Tags.ID GROUP BY Tags.ID')
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
		#directory to store the files in.
		archive = _naming['images_archive'] 
		#archive = 'static/archive' 
		i = web.webapi.rawinput()
		files = i.userimage
		if not isinstance(files, list):
			files = [files]
			
		for f in files:
			#[] This should call the import_records.py API here
			old_path=f.filename.replace('\\','/')
			
			image_id = import_image(old_path)
			
			#FUTURE CODE: to add tags to this record:
			#tag_ids = apply_tags(image_id,tags)
			
			#filename=old_path.split('/')[-1] # splits the and chooses the last part (the filename with extension)
			#fout = open(archive +os.path.sep+ filename,'wb') # creates the file where the uploaded file should be stored
			#fout.write(f.file.read()) # writes the uploaded file to the newly created file.
			#fout.close() # closes the file, upload complete.
			#something = _db.insert('images',file_path=filename)
			#something = _db.insert('images',file_path=filename)
			#make_thumbnail(old_path)
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

#@deprecated: This has been moved into the import_records.py API
def make_thumbnail(filename):
	os.system(r'convert {archive}{file_name} -auto-orient -thumbnail 150x150 \
		-unsharp 0x.5 {thumbnails}{filename}'.format(
		archive=_config['image_archive'],
		filename=filename,
		thumbnails=_config['image_thumbnails']))	
	#os.system(r'convert static/archive/'+ filename +' -auto-orient -thumbnail 150x150 -unsharp 0x.5 static/archive/thumbnails/'+filename)


if __name__ == "__main__":
	#print(tag_search.search_tags('asfkljl3%44123-*3kl+lk_'))
	#print(tag_search.search_tags('boobs or icecream'))
	test_strings = ['boobs',
					'boobs and tits',
					'boobs and (dicks or dildos)']
	
	myRequest = search()
	for searchstr in test_strings:
		results = myRequest.GET(searchstr)
		print(results)
		print('------')