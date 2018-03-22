"""Main module of KrappaChat containing the KrappaChatApp kivy application."""

import logging
import pickle
import sys

from kivy.app import App
from kivy.utils import platform
from pythonosc import osc_server, dispatcher

logging.basicConfig(level=logging.DEBUG)


class KrappaChatApp(App):
	"""Main kivy application responsible for GUI and background service	handling."""

	def build(self):
		"""Build main application, initialize background service and OSC server."""
		logging.info(f'Detected platform "{platform}"')
		if platform == 'android':
			from android import AndroidService
			self.service = AndroidService(title='IRCService')
		elif platform in ['linux', 'win']:
			import threading
			from krappachat.service.main import main
			self.service = threading.Thread(target=main, args=())
			self.service.daemon = True
		else:
			logging.critical(f'Currently not supported platform!')
			sys.exit(1)
		self.service.start()
		dp = dispatcher.Dispatcher()
		dp.map('/pubmsg', self.on_pubmsg)
		dp.map('/whisper', self.on_whisper)
		self.osc_server = osc_server.ThreadingOSCUDPServer(('127.0.0.1', 3000), dp)
		server_thread = threading.Thread(target=self.osc_server.serve_forever)
		server_thread.start()

	def on_stop(self):
		"""On application stop shut down the OSC server."""
		self.osc_server.shutdown()

	def on_pubmsg(self, message, event):
		"""Event method handling public channel messages."""
		event = pickle.loads(event)
		self.root.text += f'Pubmsg: {event.arguments[0]}\n'

	def on_whisper(self, message, event):
		"""Event method handling private whispers."""
		event = pickle.loads(event)
		self.root.text += f'Whisper: {event.arguments[0]}\n'


if __name__ == '__main__':
	KrappaChatApp().run()
