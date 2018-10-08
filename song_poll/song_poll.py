#!/usr/bin/env python

import sys
import spotipy
import spotipy.util as util
import random
import Tkinter as tk
import json
from subprocess import Popen
import time


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
score = [] # how many times thesong has been chosen
at_bat = [] # how many times the song has been available to vote on

# Extract the track info from the playlist. Each item is in a very specific position of ...
# the data structure returned by the sp.user_playlist_tracks() function
# Only run this if there is not already a results file available
try:
    # If there is already a score file, grab the data
    read_file = open('poll_results.json', 'r')
    data = json.load(read_file)
    for row in data:
        tracks.append(row[0])
        artists.append(row[1])
        track_ids.append(row[2])
        score.append(row[3])
        at_bat.append(row[4])
    print('file found')
except IOError:
    # If there is no score file, extract the tracks from spotify
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
    score = [0]*len(tracks)
    at_bat = [0]*len(tracks)
    print('file not found')

# Start playing the playlist to activate the device, then immediately puase it
# time.sleep(10)
# context = "spotify:playlist:" + playlist
# sp.start_playback(context_uri=context)
# sp.pause_playback()

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

    # Update the at_bat list to show these two songs have been selected
    at_bat[ind1] += 1
    at_bat[ind2] += 1

    # Change the button text and pass the track info into the button_command
    button1.config(text=entry1, command=lambda: button_command(ind1))
    button2.config(text=entry2, command=lambda: button_command(ind2))
    play_button1.config(command=lambda: play_command(id1))
    play_button2.config(command=lambda: play_command(id2))

# When the button is pressed, the score for the winning song increments
def button_command(ind):
    global score
    score[ind] += 1
    voting_loop(button1, button2)

# Define the function to play the songs using the play buttons
def play_command(song_id):
    new_id_list = [song_id]
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

