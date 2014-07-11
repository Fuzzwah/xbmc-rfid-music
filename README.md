XBMC RFID Music
===============

#### Trigger playback in XBMC by swiping RFID cards.

This python script listens for input from an RFID reader. When a card is swiped it checks a flatfile database to find the playlist which is assigned to the card. Playback of the playlist is triggered in XBMC.

You need to configure a few things in the conf.py file.

The card to playlist database is managed by the addcard.py script.

I have also included a shell script named m3u.sh and a visual basic script named m3u.vbs which you might find useful to make the m3u playlists.

The whole system was created for use on a Raspberry Pi running XBian. If you're running XBMC on top of a different system, you may run into problems. I'm sorry but I can't really help you with support.

While the primary focus of the project is to trigger playback of music, the system can easily be modified to trigger anything on the system including any XBMC command or executing any shell script. I personally have cards which will kick off photo slideshows, restart XBMC, reboot the whole system and send sms messages.

### Hardware

As mentioned above, I use a Raspberry Pi set up. I've created a list of the parts in an Amazon list called [Raspberry Pi XBMC Media Player](http://www.amazon.com/Raspberry-Pi-XBMC-Media-Player/lm/R2B7HG8WFE2FON) if you're interested.

I purchased the following from ent-mart.com:

* [125Khz RFID EM410X Reader](http://www.ent-mart.com/catalog/product_info.php/cPath/49/products_id/108) US$5.50
* [50x 125khz RFID ID Cards 0.8mm](http://www.ent-mart.com/catalog/product_info.php/cPath/40_41_56/products_id/140) US$14.00

I also purchased the following from Amazon.com:

* [Adhesive Name Badges](http://www.amazon.com/gp/product/B00007LVCN/ref=oh_details_o00_s00_i00?ie=UTF8&psc=1) US$16.72
* [Business Card Magnets](http://www.amazon.com/gp/product/B002YNQ8OI/ref=oh_details_o00_s01_i00?ie=UTF8&psc=1) US$9.21
* [22" x 35" Magnetic Dry Erase Board](http://www.amazon.com/Board-Dudes-Decor-Magnetic-87060UN-4/dp/B001G60IT0) US$29.99

![hardware](rfid-music.jpg?raw=true)

That particular RFID reader doesn't require any drivers for use with Windows or Linux. When a card is swipted it simply seems as though the card number has been entered from a keyboard, followed by the enter key.

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

3) Copy the files from this repo into a directory under this new user's homedir, ie: `/home/xbian/xbmc-rfid-music`

4) Connect your RFID reader to the system running XBMC. Use lsusb to get the required details of your RFID reader.

    sudo lsusb

You're looking for something similar to `ID 076b:532a OmniKey AG`. The 1st four characters of the ID are the Vendor ID, the last four characters after the colon are the Device ID. You'll need these for the next step.

5) Set up a udev rule to grant only this user access to your RFID reader:

    sudo nano /etc/udev/rules.d/80-rfid.rules
    
This will create a new emtpy file, into this you're going to put:

    SUBSYSTEMS=="usb" ATTRS{idVendor}=="076b" ATTRS{idProduct}=="532a" MODE:="0600" SYMLINK+="RFID" OWNER="root"

Where `ATTRS{idVendor}=="076b" ATTRS{idProduct}=="532a"` contain the details you found in the previous step.

6) Confirm that the settings in the `conf.py` file are correct for your setup

7) Build your card to playlist database using the `addcard.py` script:

    python addcard.py ~/.xbmc/userdata/Playlists/music/PlayListFile.m3u

Run the above command, you'll be prompted to swipe the card you wish to assign this playlist to. Repeat for all your cards / playlists.

8) Run the `rfid-music.py` script and give it a test.

    python rfid-music.py

You should see a notification in XBMC that RFID Music has connected. Swipe a card and it should kick off playback of your playlist. Hit `Ctrl+c` to kill off your test run.
    
9a) If you want to run the system as a service do the following:

    sudo chmod 755 rfid-music.py
    sudo cp xbmc-rfid-music /etc/init.d/
    sudo chmod 755 /etc/init.d/xbmc-rfid-music
    sudo update-rc.d xbmc-rfid-music defaults

Reboot the machine and the service should start up. You can confirm this via:

    sudo service xbmc-rfid-music status

9b) Or you can run the python script in the background using screen:

    sudo apt-get install screen
    screen -dmS rfid-music python rfid-music.py

Then you can attach to screen using `screen -r rfid-music` and detach with `Ctrl+a Ctrl+d`.
