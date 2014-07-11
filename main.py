#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, shelve, logging, logging.handlers, argparse
from conf import *
from xbmcclient import XBMCClient
from evdev import InputDevice, categorize, ecodes
from random import randrange

# set up all the logging stuff
LOG_FILENAME = "/tmp/xbmc-rfid-music.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"
 
# Define and parse command line arguments
parser = argparse.ArgumentParser(description="XBMC RFID Music")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")
 
# If the log file is specified on the command line then override the default
args = parser.parse_args()
if args.log:
	LOG_FILENAME = args.log
 
# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)
# Set the log level to LOG_LEVEL
logger.setLevel(LOG_LEVEL)
# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
# Attach the formatter to the handler
handler.setFormatter(formatter)
# Attach the handler to the logger
logger.addHandler(handler)
 
# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
	def __init__(self, logger, level):
		"""Needs a logger and a logger level."""
		self.logger = logger
		self.level = level
 
	def write(self, message):
		# Only log if there is a message (not just a new line)
		if message.rstrip() != "":
			self.logger.log(self.level, message.rstrip())
 
# Replace stdout with logging to file at INFO level
sys.stdout = MyLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
sys.stderr = MyLogger(logger, logging.ERROR)

def tracknum(pl):
	"""
		Returns a random track number from a playlist
	"""
	with open(pl) as f:
		for i, l in enumerate(f):
			pass
		return i

def shuffleplay(pl):
	"""
		Launches playback of the playlist in a random order
	"""
	# pick a random line number from our playlist
	randomtrack = randrange(tracknum(playlistpath + pl))
	# start playing back this playlist, starting at the random track
	xbmc.send_action("XBMC.PlayMedia(%(plpath)s%(pl)s,playoffset=%d(track))" % {'plpath': playlistpath, 'pl': pl, 'track': randomtrack})
	# enable random playback
	xbmc.send_action("XBMC.PlayerControl(RandomOn)")

def normalplay(pl):
	"""
		Launches playback of the playlist in order
	"""
	xbmc.send_action("XBMC.PlayerControl(RandomOff)")
	xbmc.send_action("XBMC.PlayMedia(%(plpath)s%(pl)s)" % {'plpath': playlistpath, 'pl': pl})

if __name__ == '__main__':

	dev = InputDevice(rfidreader)
	PROGRAM = "RFID Music"
	RUNDIR = os.path.dirname(os.path.realpath(__file__))
	ICON = RUNDIR + "/rfid-music.png"

	# create an XBMCClient object and connect
	xbmc = XBMCClient(PROGRAM, ICON)
	try:
		xbmc.connect()
	except:
		 print >> sys.stderr, "Could not connect to XBMC"
		 sys.exit( 1 )  

	# grab the rfid reader device
	try:
		dev.grab()
	except:
		 print >> sys.stderr, "Unable to grab RFID reader"
		 sys.exit( 1 )  

	# create an empty list for the card number
	cardnumber = []

	# load in our playlists from the shelve database file
	try:
		 db = shelve.open('playlists.db')
	except IOError:
		 print >> sys.stderr, "File could not be opened"
		 sys.exit( 1 )

	for event in dev.read_loop():
		# if we get a "key pressed down" event
		if event.type == ecodes.EV_KEY and event.value == 1:
			# if it is the enter key we've hit the end of a card number
			if event.code == 28:
				# merge the list in to a string
				card = ''.join(str(num) for num in cardnumber)
				# get the playlist which is assigned to this card number
				# if it doesn't have one assigned, set up the error message flag
				playlist = db.get(card,None)
				if playlist.endswith('.m3u'):
					print "Card's playlist has m3u extension"
				else:
					print "Card's playlist didn't have m3u extension"
					playlist = playlist + '.m3u'
				# if the card didn't have a playlist assigned, fire api call to display msg in xbmc
				if playlist == None:
					xbmc.send_notification(PROGRAM, "Card has no playlist assigned", "3000")
					print >> sys.stderr, "Card {c} has no playlist assigned".format(c=card)
				# check if this playlist is one of the "special" ones
				elif playlist == "shuffle":
					print "Card {c} is assigned to {p}".format(c=card, p=playlist)
					xbmc.send_action("XBMC.PlayerControl(Random)")
				elif playlist == "reboot":
					print "Card {c} is assigned to {p}".format(c=card, p=playlist)
					xbmc.send_action("XBMC.Reset")
				# if we do have a playlist we use send_action to fire off the PlayMedia command
				else:
					print "Card {c} is assigned to {p}".format(c=card, p=playlist)
					# check the shuffling options, none? just play it
					if shuffle_string is None and no_shuffle_string is None:
						normalplay(playlist)
					elif shuffle_string is not None:
						# does this playlist name contain our shuffle_string?
						if shuffle_string in playlist:
							print "%s contains the shuffle string %s" % (playlist, shuffle_string)
							shuffleplay(playlist)
						else:
							normalplay(playlist)
					elif no_shuffle_string is not None:
						# does this playlist name NOT contain our no_shuffle_string?
						if no_shuffle_string not in playlist:
							print "%s contains the shuffle string %s" % (playlist, no_shuffle_string)
							shuffleplay(playlist)
						else:
							normalplay(playlist)
				# empty out our list to be ready for the next swipe
				cardnumber = []
			else:
				# the event code is 1 more than the actual number key
				number = event.code - 1
				# except for event id 10, which is actually KP_0
				if number == 10:
					number = 0
				# stick the number onto the end of our list
				cardnumber.append(number)
			
	# close the playlists shelve database file
	db.close()