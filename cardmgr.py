#!/usr/bin/env python

"""Manage tools for RFID cards in XMBC RFID Music system

	-a --add	Add a card to the playlist database
			example: cardmgr.py -a newplaylist

	-d --del	Delete a card from the playlist database
			example: cardmgr.py -d oldplaylist

	-l --list	List all card to playlist mappings
			example: cardmgr.py -l

	-e --export	Export your database to a text file
			example: cardmgr.py -e playlistdb.txt

	-i --import	Imports card to playlist mappings from text file
			example: cardmgr.py -i playlistdb.txt
"""

import sys, getopt, shelve, ConfigParser
from conf import *
from evdev import InputDevice, categorize, ecodes

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg

def main(argv=None):
	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(argv[1:], "hov:", ["help", "output="])
		except getopt.error, msg:
			 raise Usage(msg)

		# option processing
		for option, value in opts:
			if option == "-v":
				verbose = True
			if option in ("-h", "--help"):
				raise Usage(__doc__)
			if option in ("-a", "--add"):
				addcard(value)
			if option in ("-d", "--del"):
				delcard()
			if option in ("-l", "--list"):
				listcards()
			if option in ("-e", "--export"):
				exportcards(value)
			if option in ("-i", "--import"):
				importcards(value)

		 
	except Usage, err:
		print >>sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >>sys.stderr, "	 for help use --help"
		return 2

def swipe():
	# this is the rfid reader
	dev = InputDevice(rfidreader)
	# grab the rfid reader device
	dev.grab()
	cardnumber = []
	# wait for events from the rfid reader
	for event in dev.read_loop():
		# if we get a "key pressed down" event
		if event.type == ecodes.EV_KEY and event.value == 1:
			# if it is the enter key we've hit the end of a card number
			if event.code == 28:
				# merge the list in to a string
				card = ''.join(str(num) for num in cardnumber)
				# return the card number
				return card
			else:
				# the event code is 1 more than the actual number key
				number = event.code - 1
				# except for event id 10, which is actually KP_0
				if number == 10:
					number = 0
				# stick the number onto the end of our list
				cardnumber.append(number)

def addcard(pl):
	"""
		Prompts for a card to be swiped and assigns the provided playlist to the card
	"""

	print 'Swipe the card you wish to assign to playlist: {pl}'.format(pl=pl)
	card = swipe()

	try:
		db = shelve.open(playlistsdb, writeback=True)
	except IOError:
		print >> sys.stderr, "File could not be opened"
		sys.exit( 1 )
	
	db[card] = pl
	print 'Assigned card {cardnum} playlist {pl}'.format(cardnum=card, pl=pl)
	db.close()   # close shelve file

def delcard():
	"""
		Prompts for a card to be swiped and removes that card from the database
	"""

	print 'Swipe the card you wish to delete from the database'
	card = swipe()

	try:
		db = shelve.open(playlistsdb, writeback=True)
	except IOError:
		print >> sys.stderr, "File could not be opened"
		sys.exit( 1 )
	
	del db[card]
	print 'Card {cardnum} deleted from the database'
	db.close()   # close shelve file

def listcards():
	"""
		Returns a list of cards and their assigned playlists
	"""

	try:
		db = shelve.open(playlistsdb)
	except IOError:
		print >> sys.stderr, "File could not be opened"
		sys.exit( 1 )
	
	print "[Cards]"
	for card, playlist in db.iteritems():
		print card + ": " + playlist

	db.close()   # close shelve file

def exportcards(f):
	"""
		Writes the cards and assigned playlists to a text file
	"""

	try:
		db = shelve.open(playlistsdb)
	except IOError:
		print >> sys.stderr, "File could not be opened"
		sys.exit( 1 )
	
	Config = ConfigParser.ConfigParser()
	cfgfile = open(f,'w')
	Config.add_section('Cards')

	for card, playlist in db.iteritems():
		Config.set('Cards',card,playlist)

	Config.write(cfgfile)
	cfgfile.close()
	db.close()   # close shelve file

def importcards(f):
	"""
		Imports the cards and assigned playlists from a text file
	"""

	try:
		db = shelve.open(playlistsdb)
	except IOError:
		print >> sys.stderr, "File could not be opened"
		sys.exit( 1 )
	
	cards = ConfigParser.ConfigParser()
	cards.read(f)

	for card, pl in cards:
		db[card] = pl
		print 'Assigned card {cardnum} playlist {pl}'.format(cardnum=card, pl=pl)

	cfgfile.close()
	db.close()   # close shelve file

if __name__ == "__main__":
	sys.exit(main()) 
