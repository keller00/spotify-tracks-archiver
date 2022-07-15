from __future__ import annotations

"""This submodule creates the cli used by the project."""

import argparse
import colorama
import os
import sys

from dotenv import dotenv_values
from importlib.metadata import version
from typing import Sequence

from . import constants
from . import api


def run_cli(
    argv: Sequence[str] | None = None,
    /, *,
    config: dict[str, str] | None = None,
) -> int:
    parser = argparse.ArgumentParser(constants.app_name)
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {version(constants.app_name)}',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='don\'t actually fetch track informations',
    )
    parser.add_argument(
        '--print-secrets',
        action='store_const',
        const=True,
        default=False,
        help='whether to print out secrets',
        dest='secrets',
    )
    parser.add_argument(
        '--no-print-secrets',
        action='store_const',
        const=False,
        dest='secrets',
        help='whether to NOT print out secrets',
    )
    colorama.init(autoreset=True)
    args = parser.parse_args(argv)

    if config is None:
        config = {**dotenv_values('.env'), **os.environ}
    client_id = config.get(constants.client_id)
    client_secret = config.get(constants.client_secret)
    refresh_token = config.get(constants.refresh_token)
    access_token = config.get(constants.access_token)
    if client_id is None:
        print(
            f"'{constants.client_id}' is not set, use a .env file "
            'or a environmental veriable to set it',
            file=sys.stderr,
        )
        return 1
    if client_secret is None:
        print(
            f"'{constants.client_secret}' is not set, use a .env file "
            'or a environmental veriable to set it',
            file=sys.stderr,
        )
        return 1
    if args.dry_run:
        return 0
    sp_api = api.SpotifyAPI(
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        access_token=access_token,
        print_secrets=args.secrets,
    )
    import pprint
    pp = pprint.PrettyPrinter()
    tracks = sp_api.get_user_tracks()
    pp.pprint(list(t._asdict() for t in tracks))

    return 0


if __name__ == '__main__':
    raise SystemExit(run_cli())
