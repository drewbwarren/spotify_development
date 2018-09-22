#!/usr/bin/env python

import sys
import spotipy
import spotipy.util as util
import random
import Tkinter as tk

## Button commands for ui
def show_button():
    print(song1)


## Take the tracks data from the playlist

scope = 'user-library-read'
username = '1295552060'
playlist = '0UGlsRHlwdrsnYcgty9dCR'

token = util.prompt_for_user_token(username, scope)

if not token:
    sys.exit()

sp = spotipy.Spotify(auth=token)

tracks = []
artists = []

i = 0
while(True):
    results = sp.user_playlist_tracks(username, playlist, offset=i, limit=100)
    results = results['items']

    for track in results:
        track = track['track']
        tracks.append(track['name'])
        artists.append(track['artists'][0]['name'])

    i+=100
    if len(results) < 100:
        break

## Set up the ui
root = tk.Tk()
root.title('Song Poll')


## Start the voting loop
N = len(tracks)
while(True):

    while(True):
        ind1 = random.randint(0,len(tracks)-1)
        ind2 = random.randint(0,len(tracks)-1)
        if ind1 != ind2:
            break

    song1 = tracks[ind1]
    song2 = tracks[ind2]
    artist1 = artists[ind1]
    artist2 = artists[ind2]

    print(song1 + " --- " + artist1)
    print(song2 + " --- " + artist2)

    button1 = tk.Button(root, text=song1, command=show_button).grid(row=0, column=1)
    button2 = tk.Button(root, text=song2, command=show_button).grid(row=1, column=1)
    button3 = tk.Button(root, text='Quit', command=root.destroy).grid(row=2, column=1)
    root.mainloop()


