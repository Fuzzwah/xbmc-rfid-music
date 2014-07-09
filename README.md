XBMC RFID Music
===============

#### Trigger playback in XBMC by swiping RFID cards.

This python script listens for input from an RFID reader. When a card is swiped it checks a flatfile database to find the playlist which is assigned to the card. Playback of the playlist is triggered in XBMC.

You need to configure a few things in the conf.py file.

The card to playlist database is managed by the addcard.py script.

The whole system was created for use on a Raspberry Pi running XBian. If you're running XBMC on top of a different system, you may run into problems. I'm sorry but I can't really help you with support.

### Installation

1) Install dependancies:

    sudo sed -i '/_hashlib.so/d' /var/lib/dpkg/info/python2.7.list
    sudo sed -i '/_ssl.so/d' /var/lib/dpkg/info/python2.7.list
    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install python-dev python-setuptools python-pip build-essential evtest
    sudo pip install evdev
    
The first 4 commands are required because there is an issue with installing python-dev tools on XBian.

2) Create winamp m3u compatible playlists and store them in your XBMC's userdata/Playlists/music directory, on XBian this is `/home/xbian/.xbmc/userdata/Playlists/music/` (I have included a visualbasic script which I used to create my playlists)

3) Create a new user which will run the rfid-music.py script and have sole access to the RFID reader, we need to block XBMC's access to reader.

    adduser rfid

4) Copy the files from this repo into a directory under this new user's homedir, ie: `/home/rfid/xbmc-rfid-music`

5) Connect your RFID reader to the system running XBMC. Use lsusb to get the required details of your RFID reader.

    sudo lsusb

You're looking for something similar to `ID 076b:532a OmniKey AG`. The 1st four characters of the ID are the Vendor ID, the last four characters after the colon are the Device ID. You'll need these for the next step.

6) Set up a udev rule to grant only this user access to your RFID reader:

    sudo nano /etc/udev/rules.d/80-rfid.rules
    
This will create a new emtpy file, into this you're going to put:

    SUBSYSTEMS=="usb" ATTRS{idVendor}=="076b" ATTRS{idProduct}=="532a" MODE:="0600" SYMLINK+="RFID" OWNER="rfid"

Where `ATTRS{idVendor}=="076b" ATTRS{idProduct}=="532a"` contain the details you found in the previous step.

7) Confirm that the settings in the `conf.py` file are correct for your setup

8) Build your card to playlist database using the `addcard.py` script:

    python addcard.py ~/.xbmc/userdata/Playlists/music/PlayListFile.m3u

Run the above command, you'll be prompted to swipe the card you wish to assign this playlist to. Repeat for all your cards / playlists.

9) Run the `rfid-music.py` script and give it a test.

    python rfid-music.py

You should see a notification in XBMC that RFID Music has connected. Swipe a card and it should kick off playback of your playlist. Hit `ctrl+c` to kill off your test run.
    
10a) If you want to run the system as a service do the following:

    sudo chmod 755 rfid-music.py
    sudo cp xbmc-rfid-music /etc/init.d/
    sudo chmod 755 /etc/init.d/xbmc-rfid-music
    sudo update-rc.d xbmc-rfid-music defaults

10b) Or you can run the python script in the background using screen:

    sudo apt-get install screen
    screen -dmS rfid-music python rfid-music.py

Then you can attach to screen using `screen -r rfid-music` and detach with `Ctrl+a Ctrl+d`.
