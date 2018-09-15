#!/usr/bin/env python

import sys
import spotipy
import spotipy.util as util

scope = 'user-library-read'
username = '1295552060'

token = util.prompt_for_user_token(username, scope)

if not token:
    sys.exit()

sp = spotipy.Spotify(auth=token)

tracks = []
artists = []

i = 0
while(True):
    results = sp.user_playlist_tracks(username, playlist_id='0UGlsRHlwdrsnYcgty9dCR', offset=i, limit=1)
    results = results['items'][0]['track']
    tracks.append(results['name'])
    artists.append(results['artists'][0]['name'])
    i+=1


print(tracks)
