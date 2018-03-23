"""Background service for KrappaChat.

Module containing the main() method run by the KrappaChatApp as a
background service to run a TwitchChatClient instance.
"""

import datetime
import logging
import pickle
import ssl
import sys
import threading

import irc.client
import irc.connection
from pythonosc import osc_server, udp_client, dispatcher

from .constants import default_colors
from .twitch_api import API

logging.basicConfig(level=logging.DEBUG)


class ChatEvent:
	"""Data storage class for all chat events."""

	def __init__(self, event: irc.client.Event):
		"""Create a new ChatEvent from a given event of type irc.client.Event."""
		self.source = event.source
		self.target = event.target
		self.type = event.type
		self.message = ' '.join(event.arguments)
		tags = {i['key']: i['value'] for i in event.tags}
		self.timestamp_ms = int(tags['tmi-sent-ts'])
		self.time_string = self._get_sent_time_string()
		self.badges = tags['badges'].split(',') if tags['badges'] else []
		self.user_name = tags['display-name']
		self.user_color = tags['color'] if tags['color'] else self._get_default_color_for_user(self.user_name)
		self.user_is_mod = tags['mod'] == '1'
		self.user_is_sub = tags['subscriber'] == '1'
		self.user_is_turbo = tags['turbo'] == '1'
		# Missing: self.user_type, self.user_id, self.room_id, self.emotes, self.id

	def _get_sent_time_string(self, format='%H:%M:%S'):
		"""Return the sent time in readable form in the given format."""
		dt = datetime.datetime.fromtimestamp(self.timestamp_ms / 1000)
		return dt.strftime(format)

	@staticmethod
	def _get_default_color_for_user(name):
		"""Following: https://discuss.dev.twitch.tv/t/default-user-color-in-chat/385/2."""
		n = ord(name[0]) + ord(name[-1])
		return default_colors[n % len(default_colors)]


class TwitchChatClient(irc.client.SimpleIRCClient):
	"""IRC Client for Twitch.

	Twitch specific SimpleIRCClient to connect to and communicate with the twitch chat servers.
	"""

	def __init__(self, channels: list, nickname: str, oauth_token: str,
				 api: API):
		"""Create a new TwitchChatClient.

		Create a new TwitchChatClient using the provided nickname and
		oauth_token to connect to the twitch server and join the given
		channels.
		"""
		self.api = api
		server, port = 'irc.chat.twitch.tv', 443
		self.channels = channels
		super().__init__()

		# OSC client
		self.osc_client = udp_client.SimpleUDPClient('127.0.0.1', 3000)

		# OSC server
		dp = dispatcher.Dispatcher()
		dp.map('/send_message', self.send_message)
		self.osc_server = osc_server.ThreadingOSCUDPServer(('127.0.0.1', 3001), dp)
		server_thread = threading.Thread(target=self.osc_server.serve_forever)
		server_thread.start()

		# IRC connection
		connect_factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
		self.connect(server, port, nickname, password=oauth_token,
					 connect_factory=connect_factory)
		self.start()

	def on_welcome(self, connection: irc.connection, event: irc.client.Event):
		"""Server welcome handling.

		Join the given channels and use IRC v3 capability registration as documented here:
		https://dev.twitch.tv/docs/irc/#twitch-specific-irc-capabilities.
		"""
		connection.cap('REQ', ':twitch.tv/membership')
		connection.cap('REQ', ':twitch.tv/tags')
		connection.cap('REQ', ':twitch.tv/commands')
		for channel in self.channels:
			channel = channel.lower()
			if not channel.startswith('#'):
				channel = '#' + channel
			connection.join(channel)

	def on_join(self, connection: irc.connection, event: irc.client.Event):
		"""Channel join handling."""
		logging.info('Joined channel.')

	def on_disconnect(self, connection: irc.connection,
					  event: irc.client.Event):
		"""Server disconnect handling."""
		sys.exit(0)

	def on_pubmsg(self, connection: irc.connection, event: irc.client.Event):
		"""Public message handling forwarding the event via OSC."""
		self.osc_client.send_message('/pubmsg', pickle.dumps(ChatEvent(event)))

	def on_whisper(self, connection: irc.connection, event: irc.client.Event):
		"""Whisper message handling forwarding the event via OSC."""
		self.osc_client.send_message('/whisper', pickle.dumps(ChatEvent(event)))

	def send_message(self, command, target: str, message: str):
		"""Send message to IRC."""
		self.connection.privmsg(target, message)


def create_service():
	"""Use this method as the background service."""
	from .secret import nickname, oauth, channels

	# Create API
	api = API(oauth)

	TwitchChatClient(channels, nickname, oauth, api)
