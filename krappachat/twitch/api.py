'''Module containing twitch API related content.'''

from base64 import b64decode

import requests


class API:
	'''Class to wrap the twitch API.'''
	client_id = b'cnNrYW94bjlpaHBwMGRpZDdqMzJsZHZ1Z3ZrdXJ4'

	def __init__(self):
		'''Initialize the API class.'''
		pass

	def authenticate(self):
		'''Authenticate to the twitch API service.'''
		# TODO: add nonce and state params to prevent csrf
		url = 'https://id.twitch.tv/oauth2/authorize'
		payload = {
			'client_id': self.get_client_id(),
			'redirect_uri': 'http://localhost',
			'response_type': 'token+id_token',
			'scope': 'openid+user:edit'
		}

		r = requests.get(url, params=payload)

	def get_client_id(self):
		'''Return decoded client_id.'''
		return b64decode(self.client_id, validate=True).decode()
