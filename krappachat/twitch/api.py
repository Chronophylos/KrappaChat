"""Module containing twitch API related content."""

from base64 import b64decode
from twitch import TwitchClient


"""
TODO
* check uptime and availability
* maybe use webhooks
"""


class API:
    """Class to wrap the twitch API."""

    client_id = b'cnNrYW94bjlpaHBwMGRpZDdqMzJsZHZ1Z3ZrdXJ4'

    users = list()
    channels = list()

    def __init__(self, oauth: str):
        """Initialize the API class."""
        self.client = TwitchClient(client_id=b64decode(self.client_id).encode('utf-8'),
                                   oauth_token=oauth)

