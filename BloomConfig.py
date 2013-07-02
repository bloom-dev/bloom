#BloomConfig.py

def loadSettings (settingsfilename):
	settingsfile = open(settingsfilename,'r')
	settingsdict = {}
	for line in settingsfile:
		print(line)
		tl = line.split('=')
		settingsdict[ tl[0].strip() ] = tl[1].strip()
	return settingsdict