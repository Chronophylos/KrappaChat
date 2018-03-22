'''Module containing the main() method run by the KrappaChatApp as a background service to run a TwitchChatClient instance.'''

import logging
import sys
import pickle
import ssl

import irc.client
import irc.connection
from pythonosc import udp_client
logging.basicConfig(level=logging.DEBUG)


class TwitchChatClient(irc.client.SimpleIRCClient):
	'''Twitch specific SimpleIRCClient to connect to and communicate with the twitch chat servers.'''

	def __init__(self, channels, nickname, oauth_token):
		'''Create a new TwitchChatClient using the provided nickname and oauth_token to connect to the twitch server and join the given channels.'''
		server, port = 'irc.chat.twitch.tv', 443
		self.channels = channels
		self.osc_client = udp_client.SimpleUDPClient('127.0.0.1', 3000)
		irc.client.SimpleIRCClient.__init__(self)
		connect_factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
		self.connect(server, port, nickname, password=oauth_token, connect_factory=connect_factory)
		self.start()

	def on_welcome(self, connection, event):
		'''Server welcome handling. Join the given channels and use IRC v3 capability registration as documented here: https://dev.twitch.tv/docs/irc/#twitch-specific-irc-capabilities .'''
		connection.cap('REQ', ':twitch.tv/membership')
		connection.cap('REQ', ':twitch.tv/tags')
		connection.cap('REQ', ':twitch.tv/commands')
		for channel in self.channels:
			connection.join(channel)

	def on_join(self, connection, event):
		'''Channel join handling.'''
		logging.info('Joined channel.')

	def on_disconnect(self, connection, event):
		'''Server disconnect handling.'''
		sys.exit(0)

	def on_pubmsg(self, connection, event):
		'''Public message handling forwarding the event via OSC.'''
		self.osc_client.send_message('/pubmsg', pickle.dumps(event))

	def on_whisper(self, connection, event):
		'''Whisper message handling forwarding the event via OSC.'''
		self.osc_client.send_message('/whisper', pickle.dumps(event))


def main():
	'''Use this method as the background service.'''
	from krappachat.secret import nickname, oauth, channels
	TwitchChatClient(channels, nickname, oauth)


if __name__ == '__main__':
	main()
