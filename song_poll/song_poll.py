#!/usr/bin/env python

import sys
import spotipy
import spotipy.util as util
import random
import Tkinter as tk
import json
from subprocess import Popen


## Open Spotify so the songs can play
Popen("/usr/bin/spotify", shell=True)

## Take the tracks data from the playlist

# My personal Spotify info
scope = 'user-library-read streaming'
username = '1295552060'
playlist = '0UGlsRHlwdrsnYcgty9dCR'

# Authorization to use the Spotify SDK
token = util.prompt_for_user_token(username, scope)
if not token:
    sys.exit()
sp = spotipy.Spotify(auth=token)

# Initialize lists of information to be used
tracks = []
artists = []
track_ids = []

# Extract the track info from the playlist. Each item is in a very specific position of the data structure returned by the sp.user_playlist_tracks() function
i = 0
while(True):
    results = sp.user_playlist_tracks(username, playlist, offset=i, limit=100)
    results = results['items']

    for track in results:
        track = track['track']
        tracks.append(track['name'])
        artists.append(track['artists'][0]['name'])
        track_ids.append(track['uri'])

    # The function can only return 100 tracks at a time.
    i+=100
    if len(results) < 100:
        break

## Set up the ui
root = tk.Tk()
root.title('Song Poll')
label = tk.Label(root, text="Choose one: ", padx=100)
label.grid(row=0, column=1)

## Start the voting loop
def voting_loop(button1, button2):
    # Select two random and unique tracks from the playlist
    while(True):
        ind1 = random.randint(0,len(tracks)-1)
        ind2 = random.randint(0,len(tracks)-1)
        if ind1 != ind2:
            break

    # Collect the info about the tracks
    song1 = tracks[ind1]
    song2 = tracks[ind2]
    artist1 = artists[ind1]
    artist2 = artists[ind2]
    entry1 = song1 + ' --- ' + artist1
    entry2 = song2 + ' --- ' + artist2
    id1 = track_ids[ind1]
    id2 = track_ids[ind2]

    # Change the button text and pass the track info into the button_command
    button1.config(text=entry1, command=lambda: button_command(song1, artist1, id1))
    button2.config(text=entry2, command=lambda: button_command(song2, artist2, id2))
    play_button1.config(command=lambda: play_command(id1))
    play_button2.config(command=lambda: play_command(id2))

# When the button is pressed, this function is called
def button_command(song, artist, song_id):
    print(song, artist, song_id)
    voting_loop(button1, button2)

# Define the function to play the songs using the play buttons
def play_command(song_id):
    print(song_id)
    # new_id_list = track_ids[0:10]
    # new_id_list[0] = song_id
    new_id_list = [song_id]
    print(new_id_list)
    sp.start_playback(uris=new_id_list)

# Initialize the two song buttons
button1 = tk.Button(root, width=50, command=button_command)
button1.grid(row=1, column=0)
button2 = tk.Button(root, width=50, command=button_command)
button2.grid(row=2, column=0)

# Initialize the two play buttons
play_button1 = tk.Button(root, width=5, text='>')
play_button1.grid(row=1, column=2)
play_button2 = tk.Button(root, width=5, text='>')
play_button2.grid(row=2, column=2)

# Begin the voting
voting_loop(button1, button2)

# Create a button for quitting the program
tk.Button(root, text='Quit', command=root.quit).grid(row=3, column=1)
tk.mainloop()

