#Paarth Chadha (Slate Rose)
#Bloom beginnings
import os
import glob

def loadSettings (settingsfilename):
	settingsfile = open(settingsfilename,'r')
	settingsdict = {}
	for line in settingsfile:
		print(line)
		tl = line.split('=')
		settingsdict[ tl[0].strip() ] = tl[1].strip()
	return settingsdict

settingsdict = loadSettings ('settings.conf')

print(settingsdict['basedir'])
print(os.listdir(settingsdict['basedir']))


for filetoadd in os.listdir(settingsdict['basedir']):
	inputstring = 'raw'
	os.system("start " + settingsdict['basedir'] + filetoadd)
	while inputstring != 'next':
		inputstring = input("command?")
		if inputstring == 'tag':
			print("okay...")
			#add tag to image
		

print("Completed");