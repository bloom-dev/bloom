#testweb.py

import web
import sqlite3 as sql
from organizers import Configuration     #Used to read JSON/XML configuration files.


_config = Configuration.read("settings.json")
db = web.database(dbn='sqlite',db='bloom.db')


render = web.template.render('templates/')

urls = (
	'/','index',
	'/images','images',
)

class index:
	def GET(self):
		i = web.input(name=None)
		return render.index(i.name)

class images:
	def GET(self):
		images = db.select('images')
		return render.images(images)



if __name__ == '__main__':

	app = web.application(urls,globals())
	app.run()



