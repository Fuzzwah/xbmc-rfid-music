#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, shelve
from conf import *
from evdev import InputDevice, categorize, ecodes

# this is the rfid reader
dev = InputDevice(rfidreader)

# grab the rfid reader device
dev.grab()

cardnumber = []

try:
   db = shelve.open("playlists.db", writeback=True)
except IOError:
   print >> sys.stderr, "File could not be opened"
   sys.exit( 1 )

print 'Swipe the card you wish to assign to playlist: {pl}'.format(pl=sys.argv[1])

# wait for events from the rfid reader
for event in dev.read_loop():
	# if we get a "key pressed down" event
	if event.type == ecodes.EV_KEY and event.value == 1:
		# if it is the enter key we've hit the end of a card number
		if event.code == 28:
			# merge the list in to a string
			card = ''.join(str(num) for num in cardnumber)
			# add (or update) the entry 
			db[card] = sys.argv[1]
			# let the user know we're all good
			print 'Assigned card {cardnum} playlist {pl}'.format(cardnum=card, pl=sys.argv[1])
			# we're done so break out
			break
		else:
			# the event code is 1 more than the actual number key
			number = event.code - 1
			# except for event id 10, which is actually KP_0
			if number == 10:
				number = 0
			# stick the number onto the end of our list
			cardnumber.append(number)

db.close()   # close shelve file
