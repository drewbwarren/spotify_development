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
label = tk.Label(root, text="Choose one: ", padx=100)

## Start the voting loop
def voting_loop(button1, button2):
    while(True):
        ind1 = random.randint(0,len(tracks)-1)
        ind2 = random.randint(0,len(tracks)-1)
        if ind1 != ind2:
            break

    song1 = tracks[ind1]
    song2 = tracks[ind2]
    artist1 = artists[ind1]
    artist2 = artists[ind2]
    entry1 = song1 + ' --- ' + artist1
    entry2 = song2 + ' --- ' + artist2

    button1.config(text=entry1)
    button2.config(text=entry2)
    button1.pack()
    button2.pack()

def button_command():
    voting_loop(button1, button2)
    print('song title')

N = len(tracks)
button1 = tk.Button(root, width=50, command=button_command)
button2 = tk.Button(root, width=50, command=button_command)
voting_loop(button1, button2)

tk.Button(root, text='Quit', command=root.quit)
tk.mainloop()

