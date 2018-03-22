"""Main module of KrappaChat containing the KrappaChatApp kivy application."""

import logging
import sys
import pickle
import threading

from kivy.app import App
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from pythonosc import osc_server, udp_client, dispatcher
logging.basicConfig(level=logging.INFO)


class ChatView(BoxLayout):
	"""Kivy chat view widget."""

	def __init__(self, osc_client, **kwargs):
		"""Initialize a new ChatView with the given OSC client to forward messages."""
		super().__init__(**kwargs)
		self.osc_client = osc_client
		self.cols = 1

	def send_message(self, target, message):
		"""Forward message to send to the OSC server."""
		self.osc_client.send_message('/send_message', [target, message])

	def add_event(self, event):
		"""Add a new message event to the RecycleView."""
		self.rv.data.append({'event': event})

	def clear(self):
		"""Clear all message Rows from the RecycleView."""
		self.rv.data = []


class KrappaChatApp(App):
	"""Main kivy application responsible for GUI and background service handling."""

	def build(self):
		"""Build main application, initialize background service and OSC server."""
		logging.info(f'Detected platform "{platform}"')
		if platform == 'android':
			from android import AndroidService
			self.service = AndroidService(title='IRCService')
		elif platform in ['linux', 'win']:
			from service.main import main
			self.service = threading.Thread(target=main, args=())
			self.service.daemon = True
		else:
			logging.critical(f'Currently not supported platform!')
			sys.exit(1)
		self.service.start()

		# OSC server
		dp = dispatcher.Dispatcher()
		dp.map('/pubmsg', self.handle_pubmsg)
		dp.map('/whisper', self.handle_whisper)
		self.osc_server = osc_server.ThreadingOSCUDPServer(('127.0.0.1', 3000), dp)
		server_thread = threading.Thread(target=self.osc_server.serve_forever)
		server_thread.start()

		# OSC client
		self.osc_client = udp_client.SimpleUDPClient('127.0.0.1', 3001)

		self.chat_view = ChatView(self.osc_client)
		return self.chat_view

	def on_stop(self):
		"""On application stop shut down the OSC server."""
		self.osc_server.shutdown()

	def handle_pubmsg(self, message, event):
		"""Event method handling public channel messages."""
		event = pickle.loads(event)
		self.chat_view.add_event(event)

	def handle_whisper(self, message, event):
		"""Event method handling private whispers."""
		event = pickle.loads(event)
		self.chat_view.add_event(event)


if __name__ == '__main__':
	KrappaChatApp().run()
