from __future__ import annotations

from typing import NamedTuple

app_name = 'spotify_tracks_archiver'
client_id = 'CLIENT_ID'
client_secret = 'CLIENT_SECRET'
refresh_token = 'REFRESH_TOKEN'
access_token = 'ACCESS_TOKEN'
REDIRECT_URI = 'http://localhost:8000'

# URLs
SPOTIFY_ACCOUNTS_URL = 'https://accounts.spotify.com'
SPOTIFY_ACCOUNTS_AUTHORIZE_URL = f'{SPOTIFY_ACCOUNTS_URL}/authorize'
SPOTIFY_ACCOUNTS_API_URL = f'{SPOTIFY_ACCOUNTS_URL}/api'
SPOTIFY_TOKEN_URL = f'{SPOTIFY_ACCOUNTS_API_URL}/token'


class Song(NamedTuple):
    artists: str
    name: str
    url: str
    album: str
