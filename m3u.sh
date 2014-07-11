#!/bin/bash
dir="$1"
echo "Create playlist for $1 ..."
if [[ $2 ]]; then list="$2"; else list="$1"; fi
 
pushd "$dir" 2>&1 >/dev/null
find "$dir" -type f -name "*.mp3" | sort >> "/home/xbian/.xbmc/userdata/playlists/music/$list.m3u"
echo "Found these files:"
cat "/home/xbian/.xbmc/userdata/playlists/music/$list.m3u"
popd 2>&1 >/dev/null
