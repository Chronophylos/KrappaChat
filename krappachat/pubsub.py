import asyncio
import websockets
from blinker import Namespace


class PubSub:
	def __init__(self):
		pass


class Message:
	def __init__(self, line):
		print(line)


class TwitchWebSocket:
	queue = list()

	def __init__(self):
		pass

	async def start(self):
		async with websockets.connect('wss://irc-chat.twitch.tv') as websocket:
			self.handler(websocket)

	async def consumer_handler(self, websocket):
		async for message in websocket:
			await self.consumer(message)

	async def consumer(self, message):
		message = Message(message)

	async def producer_handler(self, websocket):
		while True:
			message = await self.producer()
			await websocket.send(message)

	async def producer(self):
		while len(self.queue) == 0:
			asyncio.sleep(0.1)
		return self.queue.pop()

	async def handler(self, websocket):
		consumer_task = asyncio.ensure_future(self.consumer_handler(websocket))
		producer_task = asyncio.ensure_future(self.producer_handler(websocket))
		done, pending = await asyncio.wait(
				[consumer_task, producer_task],
				return_when=asyncio.FIRST_COMPLETED,
		)

		for task in pending:
			task.cancel()

	def connect(self, nick, token):
		self._send_message('PASS ' + token)
		self._send_message('NICK ' + nick)

	def join(self, channel):
		self._send_message('JOIN ' + channel)

	def _send_message(self, message):
		self.queue.append(message)

	def on_joined(self, room):
		Signal('joined').send(self, room)


def register_signal(namespace):
	assert isinstance(namespace, Namespace)

	global blinker_namespace
	global Signal

	blinker_namespace = namespace
	Signal = namespace.signal
