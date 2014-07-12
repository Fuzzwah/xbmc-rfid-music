# which device is your RFID reader?
rfidreader = "/dev/input/event0"

# path to playlist files, ensure you have the trailing slash
playlistpath = "/home/xbian/.xbmc/userdata/playlists/music/"

# base path of where your music is stored 
# (this is only used by the playlist creator m3u.py)
musicbasepath = "/media/Media/music/"

# auto shuffling options
# you can set either of these variable to a string of character(s)
# if both settings are blank, nothing is ever shuffled
# if both are set, shuffle string over rules
# if a playlist contains this string it will be shuffled (randomized):
shuffle_string = None

# alternatively, all playlists will be shuffled unless the name contains this string:
no_shuffle_string = "-"

# I personally use no_shuffle_string = "-" and name playlists for albums like this:
# artist-album_title.m3u

# For genre playlists or playlists containing many albums for an artist I name them:
# jazz.m3u
# artist.m3u