from kivy.app import App
from kivy.utils import platform
from pythonosc import osc_server, dispatcher
import sys
import logging
logging.basicConfig(level=logging.DEBUG)


class KrappaChatApp(App):

	def build(self):
		logging.info(f'Detected platform "{platform}"')
		if platform == 'android':
			from android import AndroidService
			self.service = AndroidService(title='IRCService')
		elif platform in ['linux', 'win']:
			import threading
			from service.main import main
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
		self.osc_server.shutdown()

	def on_pubmsg(self, message, *args):
		logging.info(f'Got a message! {message} {args}')
		self.root.text += f'Pubmsg: {args[0]}\n'

	def on_whisper(self, message, *args):
		logging.info(f'Got a whisper! {message} {args}')
		self.root.text += f'Whisper: {args[0]}\n'


if __name__ == '__main__':
	KrappaChatApp().run()
