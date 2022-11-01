from __future__ import annotations

import json
import os
from unittest import mock

from spotify_tracks_archiver import constants as c
from spotify_tracks_archiver import main


def test_get_access_token():
    with mock.patch('spotify_tracks_archiver.api.SpotifyAPI.get_user_tracks'):
        assert main.run_cli(
            [],
            config={
                c.client_id: os.environ[c.client_id],
                c.client_secret: os.environ[c.client_secret],
                c.refresh_token: os.environ[c.refresh_token],
            },
        ) == 0


def test_normal_run(capsys):
    assert main.run_cli([]) == 0
    out, err = capsys.readouterr()
    assert not err
    assert json.loads(out)
