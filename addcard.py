import sys, shelve

try:
   outdb = shelve.open( "playlists.db" )
except IOError:
   print >> sys.stderr, "File could not be opened"
   sys.exit( 1 )

outdb['0006794466'] = 'playlist.m3u'

outdb.close()   # close shelve file