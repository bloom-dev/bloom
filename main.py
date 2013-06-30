#Paarth Chadha (Slate Rose)
#Bloom beginnings
import os
import glob

#load settings
settingsfile = open('settings.conf','r')
settingsdict = {}
for line in settingsfile:
	print(line)
	tl = line.split('=')
	settingsdict[ tl[0].strip() ] = tl[1].strip()

print(settingsdict['basedir'])
print(os.listdir(settingsdict['basedir']))
