"""Main module of KrappaChat containing the KrappaChatApp kivy application."""

import cProfile
import logging
import pickle
import sys
import threading

import irc.client
from blinker import Namespace
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
from .service import ChatEvent
from .secret import channels

logging.basicConfig(level=logging.DEBUG)

blinker_namespace = Namespace()
Signal = blinker_namespace.signal


class Message:
	def __init__(self):
		pass


class ChatView(BoxLayout):
	"""Kivy chat view widget."""
	data: dict() = dict()
	channel = channels[0]

	def __init__(self, **kwargs):
		"""Initialize a new ChatView with the given OSC client to forward messages."""
		super().__init__(**kwargs)

	def send_message(self, message: str):
		"""Forward message to send to the OSC server."""
		Signal('send_message').send(target=self.channel, message=message)

	def add_event(self, channel: str, event: irc.client.Event):
		"""Add a new message event to the RecycleView."""
		if channel not in self.data:
			self.data[channel] = list()
		self.data[channel].append(event)
		self.rv.data.append({'event': event})

	def clear(self):
		"""Clear all message Rows from the RecycleView."""
		self.rv.data = []


class KrappaChatApp(App):
	"""Main kivy application responsible for GUI and background service handling."""
	profile = cProfile.Profile()
	enableProfiling = False

	def __init__(self, **kwargs):
		if 'enable_profiling' in kwargs:
			self.enableProfiling = kwargs['enable_profiling']
		super().__init__(**kwargs)

	def build(self):
		self.title = 'KrappaChat'
		# noinspection PyAttributeOutsideInit
		self.chat_view = ChatView()
		return self.chat_view

	def on_start(self):
		"""Build main application, initialize background service and events."""

		if self.enableProfiling:
			logging.info('Enabling profiling')
			self.profile.enable()

		logging.info(f'Detected platform "{platform}"')
		if platform == 'android':
			# noinspection PyUnresolvedReferences
			from android import AndroidService
			self.service = AndroidService(title='IRCService')
		elif platform in ['linux', 'win']:
			from .service import create_service
			# noinspection PyAttributeOutsideInit
			self.service = threading.Thread(target=create_service,
											args=(blinker_namespace,))
			self.service.daemon = True
		else:
			logging.critical(f'Currently not supported platform!')
			sys.exit(1)

		logging.debug('Starting Service')
		self.service.start()

		logging.debug('Connecting Signals')

		Signal('chat-message').connect(self.handle_chat_message)

	def on_stop(self):
		if self.enableProfiling:
			self.profile.disable()
			self.profile.dump_stats('krappachat.profile')

	def handle_chat_message(self, message: str, event: ChatEvent):
		"""Event method handling chat messages."""
		event = pickle.loads(event)
		self.chat_view.add_event(event.target, event)


def main():
	"""Main."""
	KrappaChatApp().run()


if __name__ == '__main__':
	main()
