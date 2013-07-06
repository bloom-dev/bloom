#= The web server aspect of bloom

import web
import sqlite3 as sql
import os
import re
from organizers import Configuration     #Used to read JSON/XML configuration files.

#setup for web.py
_config = Configuration.read("settings.json")
_db = web.database(dbn='sqlite',db='bloom.db')
_render = web.template.render('templates/',base='wrapper')
_render_naked = web.template.render('templates/')

_urls = (
	'/','index',
	'/tags','tags',
	'/collections','comingsoon',
	'/upload','upload',
	'/image/(.+)','image',
	'/list/(.+)','search',
	'/list(/)?', 'search'
)
def make_thumbnail(filename):
	os.system(r'convert static/archive/'+ filename +' -auto-orient -thumbnail 150x150 -unsharp 0x.5 static/archive/thumbnails/'+filename)

def get_tagID(tagname):
	rows = _db.select('tags',where='name='+tagname)
	for r in rows:
		return r.id


def transform_to_sql(searchstr=''):
	working_string = searchstr
	pattern = re.compile(re.escape('and'), re.IGNORECASE)
	working_string = pattern.sub (' INTERSECT ', searchstr)
	pattern = re.compile(re.escape('or'), re.IGNORECASE)
	working_string = pattern.sub (' UNION ', working_string)
	print("working string")
	print(working_string)

	pieces = working_string.split('_')
	for piece in pieces:
		if piece.strip() != 'INTERSECT' and piece.strip() != 'UNION':
			clean_piece = piece.replace('(','').replace(')','')
			working_string = working_string.replace(clean_piece, 'SELECT ImageID FROM ImageTags INNER JOIN Tags ON ImageTags.tagID = Tags.ID WHERE Tags.name = \''+clean_piece+'\'')
	return working_string.replace('_','')

def search_good_db(self, tags):
	wherestring = ""
	rowset = _db.query(transform_to_sql(tags));
	for row in rowset:
		print('row')
		print(row)
		if len(wherestring) > 0:
			wherestring += ' OR '
		wherestring += ('id = ' + str(row.ImageID))
	print (wherestring)
	if len(wherestring) == 0:
		wherestring="null"
	result = _db.select('images',where=wherestring)
	return _render.images(result)

def sqlite_needs_help(searchstr,itags):
	searchstr = searchstr.strip()
	searchstr = searchstr.replace('_',' ').encode('ascii','ignore')
	print("search string: "+searchstr)
	print(type(searchstr))
	eval_list = []
	print('Entering SQLNH: '+searchstr)
	if '(' in searchstr or ')' in searchstr:
		print('parens search '+searchstr)
		inner = re.search( "\((.*)\)" ,searchstr).group(1)
		eval_list.append(sqlite_needs_help(inner, itags))
		searchstr = searchstr.replace(inner,"",1)
	if not ' ' in searchstr.strip():
		if searchstr.strip() in itags:
			return itags[searchstr]
		else:
			raise NameError('invalid tag: '+searchstr)
	else:
		pieces = searchstr.split(' ')
		while 'and' in pieces:
			inf_index = pieces.index('and')
			if inf_index == 0 or inf_index == (len(pieces) -1):
				raise NameError('and is infix')
			print(pieces[inf_index-1])
			print(pieces[inf_index])
			print(pieces[inf_index+1])
			print(type(pieces[inf_index-1]))
			if type(pieces[inf_index-1]) is str:
				if '()' in pieces[inf_index-1]:
					pieces[inf_index-1] = eval_list[0]
					del eval_list[0]
				else:
					pieces[inf_index-1] = sqlite_needs_help(pieces[inf_index-1],itags)
			if type(pieces[inf_index+1]) is str:
				if '()' in pieces[inf_index+1]:
					pieces[inf_index+1] = eval_list[0]
					del eval_list[0]
				else:
					pieces[inf_index+1] = sqlite_needs_help(pieces[inf_index+1],itags)
			combined = pieces[inf_index-1] & pieces[inf_index+1]
			pieces[inf_index-1] = combined
			del pieces[inf_index]
			del pieces[inf_index]

		while 'or' in pieces:
			inf_index = pieces.index('or')
			if inf_index == 0 or inf_index == (len(pieces) -1):
				raise NameError('or is infix')
			if type(pieces[inf_index-1]) is str:
				if '()' in pieces[inf_index-1]:
					pieces[inf_index-1] = eval_list[0]
					del eval_list[0]
				else:
					pieces[inf_index-1] = sqlite_needs_help(pieces[inf_index-1],itags)
			if type(pieces[inf_index+1]) is str:
				if '()' in pieces[inf_index+1]:
					pieces[inf_index+1] = eval_list[0]
					del eval_list[0]
				else:
					pieces[inf_index+1] = sqlite_needs_help(pieces[inf_index+1],itags)
			combined = pieces[inf_index-1] | pieces[inf_index+1]
			pieces[inf_index-1] = combined
			del pieces[inf_index]
			del pieces[inf_index]
		if len(pieces) == 1:
			return pieces[0]


def filter_by_tags(self,searchstr):
	#Oakland's code: in progress
	#searchstr is a renaming of 'tags' from class search

	#Proposed structure:
	#[] Parse; searchstr --> tag_names[] list
	#[] Get: image_ids for tag_names --> image_ids['tagname'] = [id1,id2,...]
	#[] .... something about seperating this into two variables: positive tags and negative tags
	#[] 
	#----

	#EXPAND THIS - TO COVER THE WHOLE RANGE OF BOOLEAN LOGIC
	#INCLUDING NESTING
	#Quantifiably different results from examples:
	#'boobs or (parasite and icecream)'
	#'(boobs or parasite) and icecream'


	#Need more complicated tag string processing
	#Example: 'boobs and icecream and not parasites'
	positive_tag_names, negative_tag_names = tag_string_processing(searchstr)
	raw_tag_names = searchstr.split('/')	#might need to escape this

	#?? how are positive/negative tags distinguished?
	positive_tags = (get_image_ids(tag_name) for tag_name in positive_tag_names)
	negative_tags = (get_image_ids(tag_name) for tag_name in negative_tag_names)

	search_results = (image_id for image_id in positive_tags.pop())

	for pos_tag in positive_tags:		#positive or: TAG1 or TAG2
		search_results = (image_id for image_id in search_results
									if image_id in pos_tag)
		
	for neg_tag in negative_tags:		#negative and: TAG3 and not TAG4
		search_results = (image_id for image_id in search_results
									if image_id not in neg_tag)

	return _render.images(list(search_result))		#list(result) is necessary to collapse the delayed execution of the generator.

	#OR: In one line - to show off big epeen
	#Note this code uses 'in' for two very different operations - iteration and set inclusion
	search_results = (image_id 
						for image_id in positive_tags[0]
							if all((image_id in pos_tag) for pos_tag in positive_tags[1:])
							if not all((image_id in neg_tag) for neg_tag in negative_tags))

def get_image_ids(tag_name):
	#Oakland's code: in progress
	#@todo: 
	#Note to self - fuck with the formmating
	imageset = set()
	tagdata = _db.query(' SELECT ImageID FROM ImageTags INNER JOIN Tags ON ImageTags.tagID = Tags.ID WHERE Tags.name = \''+tag+'\' ')
	#this is not actualy formatted correctly
	for t in tagdata:
		imageset.add(t.ImageID)

def sqlite_is_bad(self,searchstr):

	pattern = re.compile(re.escape('and'), re.IGNORECASE)
	working_string = pattern.sub ('', searchstr.replace('_',' '))
	pattern = re.compile(re.escape('or'), re.IGNORECASE)
	working_string = pattern.sub ('', working_string)
	working_string = working_string.replace('(','').replace(')','')
	itags = {}
	working_string = ' '.join(working_string.split())
	tags = working_string.split(' ')
	for tag in tags:
		print('sqlib tag: '+tag)
		tagdata = _db.query(' SELECT ImageID FROM ImageTags INNER JOIN Tags ON ImageTags.tagID = Tags.ID WHERE Tags.name = \''+tag+'\' ')
		imageset = set()
		for t in tagdata:
			imageset.add(t.ImageID)
		itags[tag] = imageset
	print("processed imageset beginning with " +searchstr)
	processed_imageset = sqlite_needs_help(searchstr.replace('_',' '),itags)
	print("processed imageset: ")
	print(processed_imageset)
	wherestring = ''
	for imageid in processed_imageset:
		if len(wherestring) > 0:
			wherestring += ' OR '
		wherestring += ('id = ' + str(imageid))
	# print (wherestring)
	if len(wherestring) == 0:
		wherestring="null"
	result = _db.select('images',where=wherestring)
	return _render.images(result)

class search:
	def GET(self,tags=''):
		if tags == '' or tags == None or tags == '/':
			result = _db.select('images')
			return _render.images(result)
		else:
			return sqlite_is_bad(self,tags)
			#return search_good_db(self,tags) #-do this is you're using postgre, MSSQL, or oracle

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

def import_file(filename):
	filepath=f.filename.replace('\\','/')
	filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
	fout = open(filedir +'/'+ filename,'wb') # creates the file where the uploaded file should be stored
	fout.write(f.file.read()) # writes the uploaded file to the newly created file.
	fout.close() # closes the file, upload complete.
	something = _db.insert('images',file_path=filename)
	make_thumbnail(filename)

class comingsoon:
	def GET(self):
		return _render.comingsoon()

def start():
	app = web.application(_urls,globals())
	app.run()


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
	print(sqlite_is_bad(None,'boobs or icecream'))


