#Paarth Chadha (Slate Rose)
#Bloom beginnings
import os
import glob
import BloomServer
import BloomConfig

SETTINGS_FILENAME = 'settings.conf'

settingsdict = BloomConfig.loadSettings (SETTINGS_FILENAME)

BloomServer.bloomGo(int(settingsdict['port']))
print("Bloom Server Started")

for filetoadd in os.listdir(settingsdict['basedir']):
	inputstring = 'raw'
	os.system("start " + settingsdict['basedir'] + filetoadd)
	while inputstring != 'next':
		inputstring = input("command?")
		if inputstring == 'tag':
			print("okay...")
			#add tag to image


print("Completed");