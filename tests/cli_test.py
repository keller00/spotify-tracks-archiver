from __future__ import annotations

from importlib.metadata import version

import pytest
from spotify_tracks_archiver import constants
from spotify_tracks_archiver import main


def test_help(capsys):
    with pytest.raises(SystemExit):
        assert main.run_cli(['-h']) == 0

    out, err = capsys.readouterr()
    assert out
    assert not err


def test_version(capsys):
    with pytest.raises(SystemExit):
        assert main.run_cli(['-v']) == 0

    out, err = capsys.readouterr()
    assert out.strip(
    ) == f'{constants.app_name} {version(constants.app_name)}'
    assert not err


def test_dry_run():
    assert main.run_cli(
        ['--dry-run'],
        config={
            'CLIENT_ID': 'client_id',
            'CLIENT_SECRET': 'client_secret',
            'REFRESH_TOKEN': 'refresh_token',
        },
    ) == 0
