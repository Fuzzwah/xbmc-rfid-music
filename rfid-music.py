#!/usr/bin/python
# -*- coding: utf-8 -*-

#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
							RFID Music
				******************************
This python script listens for input from an RFID reader. When a card
is swiped it checks a flatfile database to find the playlist which is
assigned to the card. Playback of the playlist is triggered in XBMC.

You need to configure a few things in the conf.py file.

The card to playlist database is managed by the addcard.py script.

The whole system was created for use on a Raspberry Pi running XBian.
If you're running XBMC on top of a different system, you may run into
problems. I'm sorry but I can't really help you with support.
			
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import os, sys, shelve
from conf import *
from xbmcclient import XBMCClient
from evdev import InputDevice, categorize, ecodes

dev = InputDevice(rfidreader)
PROGRAM = "RFID Music"
RUNDIR = os.path.dirname(os.path.realpath(__file__))
ICON = RUNDIR + "/rfid-music.png"

# create an XBMCClient object and connect
xbmc = XBMCClient(PROGRAM, ICON)
xbmc.connect()

# grab the rfid reader device
dev.grab()

# create an empty list for the card number
cardnumber = []

# load in our playlists from the shelve database file
try:
   db = shelve.open('playlists.db')
except IOError:
   print >> sys.stderr, "File could not be opened"
   sys.exit( 1 )

# wait for events from the rfid reader
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
			# debug - check that we've got the playlist
			print(playlist)
			# if the card didn't have a playlist assigned, fire api call to display msg in xbmc
			if playlist == None:
				xbmc.send_notification(PROGRAM, "Card has no playlist assigned", "5000")
			# check if this playlist is one of the "special" ones
			elif playlist == "shuffle":
				xbmc.send_action("XBMC.PlayerControl(Random)")
			elif playlist == "reboot":
				xbmc.send_action("XBMC.Reset")
			# if we do have a playlist we use send_action to fire off the PlayMedia command
			else:
				xbmc.send_action("XBMC.PlayMedia(%(plpath)s%(pl)s)" % {'plpath': playlistpath, 'pl': playlist})
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
