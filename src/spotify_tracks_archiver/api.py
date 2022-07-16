from __future__ import annotations

import base64
import http.server
import random
import socketserver
import string
import urllib.parse
from collections.abc import Iterator
from typing import Generator

import colorama
import httpx

from . import constants


class SpotifyAuth(httpx.Auth):
    requires_response_body = True

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        access_token: str | None,
        refresh_token: str,
        print_secrets: bool,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.print_secrets = print_secrets
        if access_token is None:
            with httpx.Client() as client:
                self.update_tokens(client.send(self.build_refresh_request()))
        else:
            self.access_token = access_token

    def auth_flow(
        self,
        request: httpx.Request,
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers['Authorization'] = f'Bearer {self.access_token}'
        response = yield request

        if response.status_code == 401:
            refresh_response = yield self.build_refresh_request()
            self.update_tokens(refresh_response)

            request.headers['Authorization'] = f'Bearer {self.access_token}'
            yield request

    def build_refresh_request(self) -> httpx.Request:
        return httpx.Request(
            method='POST',
            url=constants.SPOTIFY_TOKEN_URL,
            params={
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
            },
            headers={
                'Authorization': 'Basic '
                + base64.b64encode(
                    f'{self.client_id}:{self.client_secret}'.encode(),
                ).decode('utf-8'),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        )

    def update_tokens(
        self,
        response: httpx.Response,
    ) -> None:
        data = response.json()
        self.access_token = data['access_token']
        if self.print_secrets:
            print(
                colorama.Fore.RED +
                f'Updated access token to \'{self.access_token}\'',
            )


class SpotifyAPI:

    REDIRECT_URI = constants.REDIRECT_URI

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str | None = None,
        access_token: str | None = None,
        print_secrets: bool = False,
    ) -> None:
        self.print_secrets = print_secrets
        if refresh_token is None:
            print('Refresh token is missing, must authenticate!')
            auth_response: dict[str, list[str]] | None = None

            class OAUTHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
                def log_message(self, format, *args):
                    """Prevent received printing requests."""
                    pass

                def do_GET(self):
                    nonlocal auth_response
                    auth_response = urllib.parse.parse_qs(
                        self.requestline.split()[1][2:],
                    )
                    f = self.send_head()
                    if f:
                        try:
                            self.wfile.write(b'Authentication succeeded')
                        finally:
                            self.close_connection = True
                            self.server.shutdown()
                            f.close()

                def do_HEAD(self):
                    return

            with socketserver.ThreadingTCPServer(
                ('', 8000),
                OAUTHTTPRequestHandler,
            ) as http_server:
                # TODO: disable HTTP server from printing what it receives
                url = httpx.URL(
                    constants.SPOTIFY_ACCOUNTS_AUTHORIZE_URL,
                    params={
                        'response_type': 'code',
                        'client_id': client_id,
                        'scope': 'user-read-private,'
                                 'user-library-read,'
                                 'playlist-read-private',
                        'state': ''.join(
                            random.choice(string.ascii_letters)
                            for _ in range(16)
                        ),
                        'redirect_uri': self.REDIRECT_URI,
                    },
                )
                print(
                    f'Open {colorama.Fore.BLUE}{url}{colorama.Fore.RESET} '
                    'to authorize',
                )
                http_server.serve_forever()
                if auth_response is None:
                    raise Exception(
                        f'{colorama.Fore.RED}Invalid auth response:'
                        f'{auth_response}',
                    )
                try:
                    code = auth_response['code'][0]
                except KeyError:
                    print(
                        f'{colorama.Fore.RED}Received error in '
                        f'callback: {auth_response}',
                    )
                refresh_token, access_token = self.get_refresh_access_token(
                    code=code,
                    redirect_uri=constants.REDIRECT_URI,
                    client_id=client_id,
                    client_secret=client_secret,
                )
                print(f'{colorama.Fore.GREEN}Successfully authenticated')
                if self.print_secrets:
                    print(
                        colorama.Fore.RED +
                        f'Save this for later!! {refresh_token=}',
                    )
        self._http_client = httpx.Client(
            base_url='https://api.spotify.com',
            auth=SpotifyAuth(
                client_id=client_id,
                client_secret=client_secret,
                access_token=access_token,
                refresh_token=refresh_token,
                print_secrets=print_secrets,
            ),
        )

    def get_refresh_access_token(
        self,
        code: str,
        redirect_uri: str,
        client_id: str,
        client_secret: str,
    ) -> tuple[str, str]:
        r = httpx.request(
            'POST',
            constants.SPOTIFY_TOKEN_URL,
            params={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': redirect_uri,
            },
            headers={
                'Authorization': 'Basic '
                + base64.b64encode(
                    f'{client_id}:{client_secret}'.encode(),
                ).decode('utf-8'),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        )
        data = r.json()
        return data['refresh_token'], data['access_token']

    def get_user_tracks(self) -> Iterator[constants.Song]:
        r = self._http_client.request(
            'GET',
            '/v1/me/tracks',
            params={'offset': 0, 'limit': 50},
            headers={
                'Content-Type': 'application/json',
            },
        )
        for e in self._consume_pagination(r.json()):
            track = e['track']
            yield constants.Song(
                artists=', '.join(a['name'] for a in track['artists']),
                name=track['name'],
                url=track['external_urls']['spotify'],
                album=track['album']['name'],
            )

    def _consume_pagination(
        self,
        d: dict,
        verb: str = 'GET',
    ) -> Iterator[dict]:
        yield from d['items']
        while d['next'] is not None:
            r = self._http_client.request(
                verb,
                d['next'],
                headers={
                    'Content-Type': 'application/json',
                },
            )
            d = r.json()
            yield from d['items']
