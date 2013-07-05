#= The web server aspect of bloom

import web
import sqlite3 as sql
from organizers import Configuration     #Used to read JSON/XML configuration files.

#setup for web.py
_config = Configuration.read("settings.json")
_db = web.database(dbn='sqlite',db='bloom.db')
_render = web.template.render('templates/')

_urls = (
	'/','index',
	'/images','images',
)

class index:
	def GET(self):
		i = web.input(name=None)
		return _render.index(i.name)

class images:
	def GET(self):
		image_list = _db.select('images')
		return _render.images(image_list)

def start():
	app = web.application(_urls,globals())
	app.run()