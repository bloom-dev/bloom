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
	'/upload','comingsoon',
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

class comingsoon:
	def GET(self):
		return _render.comingsoon()

def start():
	app = web.application(_urls,globals())
	app.run()