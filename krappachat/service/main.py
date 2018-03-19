import logging
import sys
import pickle

import irc.client
from pythonosc import udp_client
logging.basicConfig(level=logging.DEBUG)


class TwitchChatClient(irc.client.SimpleIRCClient):

	def __init__(self, channels, nickname, oauth_token):
		server, port = 'irc.chat.twitch.tv', 6667
		self.channels = channels
		self.osc_client = udp_client.SimpleUDPClient('127.0.0.1', 3000)
		irc.client.SimpleIRCClient.__init__(self)
		self.connect(server, port, nickname, password=oauth_token)
		self.start()

	def on_welcome(self, connection, event):
		connection.cap('REQ', ':twitch.tv/membership')
		connection.cap('REQ', ':twitch.tv/tags')
		connection.cap('REQ', ':twitch.tv/commands')
		for channel in self.channels:
			connection.join(channel)

	def on_join(self, connection, event):
		logging.info('Joined channel.')

	def on_disconnect(self, connection, event):
		sys.exit(0)

	def on_pubmsg(self, connection, event):
		self.osc_client.send_message('/pubmsg', pickle.dumps(event))

	def on_whisper(self, connection, event):
		self.osc_client.send_message('/whisper', pickle.dumps(event))


def main():
	from secret import nickname, oauth
	TwitchChatClient(['#chronophylos'], nickname, oauth)


if __name__ == '__main__':
	main()
