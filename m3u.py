#!/usr/bin/env python
 
#
# MP3 playlist generator for XBMC
#
# Generate an mp3 playlist file (.m3u), sorted by filename.
#
# USAGE
#
#	$ m3u.py playlistname /full/path/to/mp3s_directory
#
# OR if you have musicbasepath set up in conf.py as /full/path/to/
#
#	$ m3u.py playlistname mp3s_directory
#
# You can pass multiple directories as arguments
#
#   $ m3u.py playlistname /full/path/to/mp3s_directory /some/more /has\ space\ in\ name/path another "one more with spaces"
#
# The above example would add all mp3s found in the following folders:
#
#	/full/path/to/mp3s_directory
#	/some/more
#	/has space in name/path
#   /full/path/to/another
#	/full/path/to/one more with spaces

import os, sys, glob
from itertools import chain
from conf import * # we use the setting for playlistpath from conf.py

def create_m3u(dir, playlist, app):
	
	if not playlist.endswith(".m3u"):
		playlist = playlist + ".m3u"

	try:
		print "Adding mp3s from directory '%s' to '%s'" % (dir, playlist)
 
		mp3s = []
		glob_pattern = "*.[mM][pP]3"
 
		os.chdir(dir)
 
		for file in glob.glob(glob_pattern):
			print file
			mp3s.append(file)

		mp3s = sorted(mp3s)
		if not dir.endswith("/"):
			dir = dir + "/"
 
		if len(mp3s) > 0:
			print "Writing playlist '%s'..." % playlist
			# write the playlist
			if os.path.isfile(playlistpath + playlist) and app == False:
				print "Overwritting file %s%s" % (playlistpath, playlist)
				of = open(playlistpath + playlist, 'w+')
				of.write("#EXTM3U\n")
			elif os.path.isfile(playlistpath + playlist) and app == True:
				print "Appending file %s%s" % (playlistpath, playlist)
				of = open(playlistpath + playlist, 'a')
			else:
				print "Creating file %s%s" % (playlistpath, playlist)
				of = open(playlistpath + playlist, 'w')
				of.write("#EXTM3U\n")
 
			# sorted by track number
			for mp3 in mp3s:
				print "An mp3 file: " + mp3
				of.write(dir + mp3 + "\n")
 
			of.close()
		else:
			print "No mp3 files found in '%s'." % dir
 
	except:
		print "ERROR occured when processing directory '%s'. Ignoring." % dir
		print "Text: ", sys.exc_info()[0]
 
def main(argv=None):
	if argv is None:
		argv = sys.argv
 
	# directories containing music files
	dirs = []
 
	if len(sys.argv) < 3:
	# we do not have command line arguments
		print "Usage: $ m3u.py playlistname /path/to/mp3s"
	elif len(sys.argv) == 3:
	# 1 dir passed on the command line
		playlist = sys.argv[1]
		dir = sys.argv[2]
		if dir.startswith("/"):
			create_m3u(dir, playlist, False)
		else:
			create_m3u(musicbasepath + dir, playlist, False)
	else:
	# passed in directories on the command line
		playlist = sys.argv[1]
		for dir in sys.argv[2:]:
			dirs.append(dir)
		
		for dir in dirs:
			if dir == sys.argv[2]:
				if dir.startswith("/"):
					# if this is the 1st dir, we don't append
					create_m3u(dir, playlist, False)
				else:
					create_m3u(musicbasepath + dir, playlist, False)
			else:
				if dir.startswith("/"):
					create_m3u(dir, playlist, True)
				else:
					create_m3u(musicbasepath + dir, playlist, True)
 
	return 0
 
# if name == "main":
sys.exit(main())