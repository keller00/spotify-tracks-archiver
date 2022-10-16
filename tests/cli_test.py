from __future__ import annotations

from importlib.metadata import version

import pytest
from spotify_tracks_archiver import constants as C
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
    ) == f'{C.app_name} {version(C.app_name)}'
    assert not err


def test_dry_run():
    assert main.run_cli(
        ['--dry-run'],
    ) == 0


def test_unchanged_env_detection():
    """For when someone forgets to update .env after copying the example."""
    assert main.run_cli(
        config={
            'CLIENT_ID': '...',
            'CLIENT_SECRET': 'client_secret',
        },
    ) == 2
    assert main.run_cli(
        config={
            'CLIENT_ID': 'client_id',
            'CLIENT_SECRET': '...',
        },
    ) == 2
