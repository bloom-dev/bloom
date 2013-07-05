#= The web server aspect of bloom

import web
import sqlite3 as sql
from organizers import Configuration     #Used to read JSON/XML configuration files.

#setup for web.py
_config = Configuration.read("settings.json")
_db = web.database(dbn='sqlite',db='bloom.db')
_render = web.template.render('templates/',base='wrapper')
_render_naked = web.template.render('templates/')

_urls = (
	'/','index',
	'/images','images',
	'/tags','tags',
	'/collections','comingsoon',
	'/upload','upload',
	'/image/(.+)','image',
	'/list/(.+)','search'
)

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
		tag_list = _db.select('tags')
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
		x = web.input(userimage={})
		filedir = 'static/archive' # change this to the directory you want to store the file in.
		if 'userimage' in x: # to check if the file-object is created
			filepath=x.userimage.filename.replace('\\','/')
			filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
			fout = open(filedir +'/'+ filename,'wb') # creates the file where the uploaded file should be stored
			fout.write(x.userimage.file.read()) # writes the uploaded file to the newly created file.
			fout.close() # closes the file, upload complete.
			something = _db.insert('images',file_path=filename)
			print(something);
		raise web.seeother('/images')

class comingsoon:
	def GET(self):
		return _render.comingsoon()

def start():
	app = web.application(_urls,globals())
	app.run()