#= The web server aspect of bloom

import web
import sqlite3 as sql
import os
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
def make_thumbnail(filename):
	os.system(r'convert static/archive/'+ filename +' -auto-orient -thumbnail 150x150 -unsharp 0x.5 static/archive/thumbnails/'+filename)

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

		# x = web.input(userimage={})
		# filedir = 'static/archive' # change this to the directory you want to store the file in.
		# if 'userimage' in x: # to check if the file-object is created
		# filepath=x.userimage.filename.replace('\\','/')
		# filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
		# fout = open(filedir +'/'+ filename,'wb') # creates the file where the uploaded file should be stored
		# fout.write(x.userimage.file.read()) # writes the uploaded file to the newly created file.
		# fout.close() # closes the file, upload complete.
		# something = _db.insert('images',file_path=filename)
		# make_thumbnail(filename)
		# 	print(something)
		# raise web.seeother('/images')

class comingsoon:
	def GET(self):
		return _render.comingsoon()

def start():
	app = web.application(_urls,globals())
	app.run()