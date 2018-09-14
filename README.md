# Spotify Development

Use this repo for projects using Spotify's API throught the Python package [Spotipy][sp].

The following three environment veriables must be set:

    export SPOTIPY_CLIENT_ID='your-spotify-client-id'
    export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
    export SPOTIPY_REDIRECT_URI='your-app-redirect-url'

The first two can be found on the [Spotify developer dashboard][dash]. The last one can be a broken link as long as the application won't be used commercially. Use `http://localhost/`.

[sp]: https://spotipy.readthedocs.io/en/latest/
[dash]: https://developer.spotify.com/dashboard/login
