"""Main module of KrappaChat containing the KrappaChatApp kivy application."""

import logging
import pickle
import sys
import threading

import irc.client
from blinker import Namespace
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform

logging.basicConfig(level=logging.INFO)

blinker_namespace = Namespace()
Signal = blinker_namespace.signal


class ChatView(BoxLayout):
	"""Kivy chat view widget."""

	def __init__(self, **kwargs):
		"""Initialize a new ChatView with the given OSC client to forward messages."""
		super().__init__(**kwargs)
		self.cols = 1

	def send_message(self, target: str, message: str):
		"""Forward message to send to the OSC server."""
		send_message_signal = Signal('send_message')
		send_message_signal.send(target=target, message=message)

	def add_event(self, event: irc.client.Event):
		"""Add a new message event to the RecycleView."""
		self.rv.data.append({'event': event})

	def clear(self):
		"""Clear all message Rows from the RecycleView."""
		self.rv.data = []


class KrappaChatApp(App):
	"""Main kivy application responsible for GUI and background service handling."""

	def build(self):
		"""Build main application, initialize background service and events."""
		logging.info(f'Detected platform "{platform}"')

		if platform == 'android':
			from android import AndroidService
			self.service = AndroidService(title='IRCService')
		elif platform in ['linux', 'win']:
			from .service import create_service
			self.service = threading.Thread(target=create_service,
											args=(blinker_namespace,))
			self.service.daemon = True
		else:
			logging.critical(f'Currently not supported platform!')
			sys.exit(1)
		self.service.start()

		self.chat_view = ChatView()

		Signal('pubmsg').connect(self.handle_pubmsg)
		Signal('whisper').connect(self.handle_whisper)

		return self.chat_view

	def handle_pubmsg(self, message: str, event: irc.client.Event):
		"""Event method handling public channel messages."""
		event = pickle.loads(event)
		self.chat_view.add_event(event)

	def handle_whisper(self, message: str, event: irc.client.Event):
		"""Event method handling private whispers."""
		event = pickle.loads(event)
		self.chat_view.add_event(event)


def main():
	"""Main."""
	KrappaChatApp().run()


if __name__ == '__main__':
	main()
