#!/usr/bin/env python

import sys
import spotipy
import spotipy.util as util
import random
import Tkinter as tk
import json
from subprocess import Popen, call
import time
import numpy as np
import matplotlib.pyplot as plt
from operator import itemgetter


## Open Spotify so the songs can play
if len(sys.argv) == 1:
    spotify = Popen("/usr/bin/spotify")

# Set the environment variables through my alias
call(['/bin/bash', '-i', '-c', 'spotify_song_poll_env'])

# My personal Spotify info
scope = 'user-library-read streaming playlist-modify-public'
username = '1295552060'
playlist = '0UGlsRHlwdrsnYcgty9dCR'
results_playlist = '1cgMS7J9sCxKQ5vcvms4RM'

# Authorization to use the Spotify SDK
token = util.prompt_for_user_token(username, scope)
if not token:
    sys.exit()
sp = spotipy.Spotify(auth=token)


#
#****************************************************
# Data retreival - list of tracks
#****************************************************
#

# Initialize lists of information to be used
tracks = []
artists = []
track_ids = []
votes = [] # how many times thesong has been chosen
at_bat = [] # how many times the song has been available to vote on
scores = []


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
        votes.append(row[3])
        at_bat.append(row[4])
        scores.append(row[5])
    print('file found')
except IOError:
    print('file not found')


# Take the tracks from the playlist, check them agains the results file
i = 0
track_check = []
artist_check = []
id_check = []
while(True):
    results = sp.user_playlist_tracks(username, playlist, offset=i, limit=100)
    results = results['items']

    for track in results:
        track = track['track']
        track_check.append(track['name'])
        artist_check.append(track['artists'][0]['name'])
        id_check.append(track['uri'])

    # The function can only return 100 tracks at a time.
    i+=100
    if len(results) < 100:
        break

# Find the tracks in the playlist, then check if they are located in the results
for i,id in enumerate(id_check):
    # if track.upper() in (name.upper() for name in tracks):
    #     pass
    if id in track_ids or track_check[i] in tracks:
        pass
    else:
        tracks.append(track_check[i])
        artists.append(artist_check[i])
        track_ids.append(id)
        votes.append(0)
        at_bat.append(0)
        scores.append(0)
        print(track_check[i] + ' added')

# Clear unused variables
del i, track_check, artist_check, id_check




#
#****************************************************
# Voting loop and GUI
#****************************************************
#

# Run the voting on default script
if len(sys.argv) == 1:

    ## Set up the ui
    root = tk.Tk()
    root.title('Song Poll')
    label = tk.Label(root, text="Choose one: ", padx=100)
    label.grid(row=0, column=1)

    ## Start the voting loop
    def voting_loop(button1, button2):
        # Select two random and unique tracks from the playlist
        while(True):
            minimum_votes = min(at_bat)
            less_viewed_songs = [i for i,x in enumerate(at_bat) if x == minimum_votes]
            if len(less_viewed_songs) > 1: # check how many songs are left
                ind1 = random.choice(less_viewed_songs)  
                ind2 = random.choice(range(len(tracks))) 
                print(less_viewed_songs)
            else:
                ind1 = less_viewed_songs[0]
                ind2 = random.choice(range(len(tracks)))
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
        button1.config(text=entry1, command=lambda: button_command(ind1,ind2))
        button2.config(text=entry2, command=lambda: button_command(ind2,ind1))
        play_button1.config(command=lambda: play_command(id1))
        play_button2.config(command=lambda: play_command(id2))

    # When the button is pressed, the score for the winning song increments
    def button_command(indWin,indLose):
        global votes
        # Update the at_bat list to show these two songs have been selected
        at_bat[indWin] += 1
        at_bat[indLose] += 1
        # Increment the winning song
        votes[indWin] += 1
        voting_loop(button1, button2)

    # Define the function to play the songs using the play buttons
    def play_command(song_id):
        print(song_id)
        new_id_list = [song_id]
        sp.start_playback(uris=new_id_list)

    def skip_command():
        voting_loop(button1,button2)

    def pause_command():
        sp.pause_playback()

    # Define the function to quit the voting and save the results
    def quit_command():
        global tracks, artists, track_ids, votes, at_bat
        poll = []
        for i in range(len(tracks)):
            if at_bat[i] == 0 or votes[i] == 0:
                score = 0
            elif at_bat[i] > 0:
                score = float(votes[i])*(1.0 + 10/float(at_bat[i]))
            scores[i] = score
            poll.append([tracks[i], artists[i], track_ids[i], votes[i], at_bat[i], score])
        with open('poll_results.json', 'w') as write_file:
                json.dump(poll, write_file, indent=4)
        spotify.kill()
        root.quit()

    # Initialize the two song buttons
    button1 = tk.Button(root, width=50, command=button_command)
    button1.grid(row=1, column=0)
    button2 = tk.Button(root, width=50, command=button_command)
    button2.grid(row=2, column=0)

    # Initialize the two play buttons
    play_button1 = tk.Button(root, width=5, text='>')
    play_button1.grid(row=1, column=1)
    play_button2 = tk.Button(root, width=5, text='>')
    play_button2.grid(row=2, column=1)

    # Begin the voting
    voting_loop(button1, button2)

    # Create a button for quitting the program
    tk.Button(root, text='Skip', command=skip_command).grid(row=3, column=0)
    tk.Button(root, text='||', command=pause_command).grid(row=3, column=1)
    tk.Button(root, text='Quit', command=quit_command).grid(row=4, column=1)
    tk.mainloop()

    # Save the results to a playlist
    score_ind = sorted(range(len(scores)), key = lambda k: scores[k])
    results = reversed(score_ind)
    for i,ind in enumerate(results):
        if i == 0:
            sp.user_playlist_replace_tracks(username,results_playlist,[track_ids[ind]])
        else:
            sp.user_playlist_add_tracks(username,results_playlist,[track_ids[ind]])

#
#****************************************************
# Results
#****************************************************
#



# Print some results

score_ind = sorted(range(len(scores)), key = lambda k: scores[k])
results = reversed(score_ind)
    
    
# Plot some of the results
# Bar Graph of top 25 songs
song_results = []
score_results = []
for i,ind in enumerate(results):
    song_results.append(tracks[ind])
    score_results.append(round(scores[ind],1))
    if i >= 24:
        break
y_pos = np.arange(25)

fig = plt.figure(figsize=(20,10))
ax = fig.add_subplot(1,1,1)
ax.grid()
plt.bar(y_pos, score_results, align='center', alpha=0.5)
for i,v in enumerate(score_results):
    ax.text(i-.4, v+.1 , str(v), color='blue', fontweight='bold')
plt.xticks(y_pos,song_results, rotation='vertical')
plt.ylabel('Score')
plt.title('Top 25 Songs')
fig.tight_layout()
plt.show()


# Top10 artists
# Create a dict of all the artists and their scores
Nartists = list(set(artists))
artist_scores = {}
for i in range(len(Nartists)):
    artist_scores[Nartists[i]] = 0

# Find the score of each song by an artist
for artist, score in artist_scores.iteritems():
    Nsongs = 0
    indices = [i for i, x in enumerate(artists) if x == artist]
    for i,ind in enumerate(indices):
        Nsongs = Nsongs + 1
        score = score + scores[ind]
    if Nsongs == 0: # Catch the exception where the score is 0
        Nsongs = 1
    score = Nsongs/2 + score / Nsongs   
    artist_scores[artist] = round(score,1)

sorted_artists = sorted(artist_scores.items(), key=itemgetter(1))
sorted_artists = reversed(sorted_artists)
top_25_artist_scores = []
top_25_artists = []
for i,pair in enumerate(sorted_artists):
    top_25_artists.append(pair[0])
    top_25_artist_scores.append(pair[1])
    if i >= 24:
        break

fig = plt.figure(figsize=(20,10))
ax = fig.add_subplot(1,1,1)
ax.grid()
plt.bar(y_pos, top_25_artist_scores, align='center', alpha=0.5)
for i,v in enumerate(top_25_artist_scores):
    ax.text(i-.4, v+.1 , str(v), color='blue', fontweight='bold')
plt.xticks(y_pos,top_25_artists, rotation='vertical')
plt.ylabel('Score')
plt.title('Top 25 Artists')
fig.tight_layout()
plt.show()


