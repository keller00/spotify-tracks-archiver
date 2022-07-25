# spotify_tracks_archiver
[![PyPi](https://img.shields.io/pypi/v/spotify-tracks-archiver.svg)](https://pypi.python.org/pypi/spotify_tracks_archiver/)
[![codecov](https://codecov.io/gh/keller00/spotify-tracks-archiver/branch/main/graph/badge.svg)](https://codecov.io/gh/keller00/spotify-tracks-archiver)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/keller00/spotify-tracks-archiver/main.svg)](https://results.pre-commit.ci/latest/github/keller00/spotify-tracks-archiver/main)

A way to back up your "Liked Songs" library from Spotify to a JSON file.

## Set up

1. Set up a virtualenv and install this project into it.
    ```console
    python -m pip install spotify_tracks_archiver
    ```

2. Create an app at https://developer.spotify.com/dashboard/applications and save the `Client ID` and `Client Secret` into a file called `.env` like this (or set them as individual environmental variables):
    ```
    CLIENT_ID="..."
    CLIENT_SECRET="..."
    ```

3. Run `spotify_tracks_archiver --print-secrets --dry-run` and authenticate. This should print your Refresh Token and save it to your `.env` file (or set it as an environmental variable):
    ```
    ...
    REFRESH_TOKEN="..."
    ```

4. You're done, execute `spotify_tracks_archiver` and pipe it into a file and/or automate the process on some CI ([example on GitHub Actions](https://github.com/keller00/spotify-tracks-archiver-action)).
