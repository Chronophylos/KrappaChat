import irc.client
import sys
import logging
from pythonosc import udp_client, osc_message_builder
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
		osc_client.send_message('/pubmsg', event.arguments[0])

	def on_privmsg(self, connection, event):
		osc_client.send_message('/whisper', event.arguments[0])


def main():
	nickname = 'xxx'
	oauth_token = 'xxx'
	TwitchChatClient(['#xxx'], nickname, oauth_token)


if __name__ == '__main__':
	main()
