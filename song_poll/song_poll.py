#!/usr/bin/env python

import sys
import spotipy
import spotipy.util as util
import random
import Tkinter as tk
import json
from subprocess import Popen, call
import time


## Open Spotify so the songs can play
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

# Initialize lists of information to be used
tracks = []
artists = []
track_ids = []
votes = [] # how many times thesong has been chosen
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
        votes.append(row[3])
        at_bat.append(row[4])
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
for i,track in enumerate(track_check):
    if track in tracks:
        pass
    else:
        tracks.append(track)
        artists.append(artist_check[i])
        track_ids.append(id_check[i])
        votes.append(0)
        at_bat.append(0)
        print(track + ' added')

# Clear unused variables
del i, track_check, artist_check, id_check

# Scores list must match length of new track list
scores = [0]*len(tracks)


#
#****************************************************
# Data retreival complete
#****************************************************
#


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



# Print the results
score_ind = sorted(range(len(scores)), key = lambda k: scores[k])
results = reversed(score_ind)
for i,ind in enumerate(results):
    if i <= 25:
        print(tracks[ind], ' --- ', scores[ind])
    if i == 0:
        sp.user_playlist_replace_tracks(username,results_playlist,[track_ids[ind]])
    else:
        sp.user_playlist_add_tracks(username,results_playlist,[track_ids[ind]])
    






# Reorder the results playlist to match scores
# https://open.spotify.com/user/1295552060/playlist/1cgMS7J9sCxKQ5vcvms4RM?si=VKXecWXGSp6Iq5LjyZ1gsw

# for i,ind in enumerate(results):
#     if i == 0:
#         print(track_ids[ind],tracks[ind])
#         sp.user_playlist_replace_tracks(username,results_playlist,track_ids[ind])


# print(track_ids[results])
# print(track_ids[0:10])

# def reorder_results(track_list,results):
#     n = len(track_list)
#     print(n)
#     temp = [0]*n
#     for i,ind in enumerate(results):
#         # print(i)
#         # print(track_list[i])
#         # print(idx)
#         # print(idx[i])
#         # print(temp[idx[i]])
#         temp[ind] = track_list[i]

#     for i,ind in enumerate(results):
#         track_list[i] = temp[i]
#         ind = i

# reorder_results(track_ids,results)
# print(track_ids[0:10])
