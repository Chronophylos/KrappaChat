"""Module for emote handling."""

import hashlib
import json
import os
from enum import Enum
from io import BytesIO

import requests
from PIL import Image


class EmoteTypes(Enum):
	"""Enum class to specify emote type."""

	Twitch = 0,
	FrankerFaceZ = 1,
	BetterTwitchTV = 2,


class EmoteResolutions(Enum):
	"""Enum class to specify emote resolution."""

	Small = 1
	Medium = 2
	Big = 3


class EmoteCache:
	"""Class for caching emotes."""

	location = 'cache'
	index_file = location + '/index.json'
	index = None

	@staticmethod
	def load(name: str):
		"""Load a file from cache.

		Load a file from cache if it exists otherwise raise
		FileNotFoundError.

		:param name: a string to search for in the cache
		:return: a byte-like object
		"""
		data = None
		EmoteCache._load_index()
		if name in EmoteCache.index:
			with open(EmoteCache.index[name], 'rb') as cached_file:
				data = cached_file.read()
		return data

	@staticmethod
	def cache(name: str, data: BytesIO):
		"""Cache a byte-like object.

		:param name: a name for the cached file
		:param data: a byte-like object to cache
		"""
		EmoteCache._load_index()
		path = ""
		if name not in EmoteCache.index.items():
			path = os.path.join(EmoteCache.location,
								hashlib.sha1(name.encode()).hexdigest())
			EmoteCache.index[name] = path
		else:
			path = EmoteCache.index[name] = path
		with open(path, 'wb') as cached_file:
			cached_file.write(data.getvalue())
		EmoteCache._save_index()

	@staticmethod
	def _load_index():
		"""Load the index file containing the paths for the cache."""
		if not EmoteCache.index:
			if not os.path.exists(EmoteCache.index_file):
				EmoteCache.index = dict()
			else:
				EmoteCache.index = json.load(open(EmoteCache.index_file))

	@staticmethod
	def _save_index():
		"""Save the index to a file."""
		json.dump(EmoteCache.index, open(EmoteCache.index_file, 'w'))


class BaseEmote:
	"""Class to download and store an emote."""

	images = dict()

	def __init__(self, name: str, emote_id: int or str, emote_type: EmoteTypes):
		"""Create new emote by name and url."""
		self.name = name
		self.id = emote_id
		self.emote_type = emote_type

	def download(self, res: EmoteResolutions) -> bool:
		"""Download emote image data.

		:return: True if the image is loaded from cache and False otherwise.
		"""
		name = ';'.join([self.name, self.id, res.value])
		img = EmoteCache.load(name)
		if img is not None:
			self.images[res] = img
			return True
		url = self.get_url(res)
		r = requests.get(url)
		if not r.status_code == 200:
			raise Exception
		b = BytesIO(r.content)
		EmoteCache.cache(name, b)
		self.images[res] = Image.open(b)
		return False

	def get_url(self, res: EmoteResolutions) -> str:
		"""Get URL suffix for given emote resolution and type."""
		pass


class TwitchEmote(BaseEmote):
	"""A twitch emote."""

	def __init__(self, name: str, emote_id: int):
		"""Call the super."""
		super().__init__(name, emote_id, EmoteTypes.Twitch)

	def get_url(self, res: EmoteResolutions) -> str:
		""":returns: the url for this twitch emote."""
		return f'https://static-cdn.jtvnw.net/emoticons/v1/{self.id}/{res.value}.0'


class FFZEmote(BaseEmote):
	"""A FFZ emote."""

	def __init__(self, name: str, emote_id: int or str):
		"""Call the super."""
		super().__init__(name, emote_id, EmoteTypes.FrankerFaceZ)

	def get_url(self, res: EmoteResolutions) -> str:
		""":returns: the url for this twitch emote."""
		value = 4 if res.value == 3 else res.value
		return f'https://cdn.frankerfacez.com/emoticon/{self.id}/{value}'


class BTTVEmote(BaseEmote):
	"""A BTTV emote."""

	def __init__(self, name: str, emote_id: int or str):
		"""Call the super."""
		super().__init__(name, emote_id, EmoteTypes.BetterTwitchTV)

	def get_url(self, res: EmoteResolutions) -> str:
		""":returns: the url for this twitch emote."""
		return f'https://cdn.betterttv.net/emote/{self.id}/{res.value}x'


class EmoteSet:
	"""Stores a emote set."""

	emotes = list()

	def __init__(self, set_id: int, emote_class=BaseEmote):
		"""Constructor."""
		self.id = set_id
		self.emote_class = emote_class

	def get_set(self):
		""":return: the set."""
		pass

	def download(self, res: EmoteResolutions):
		"""Download the set."""
		for emote in self.emotes:
			assert isinstance(emote, self.emote_class)
			emote.download(res)


class GlobalEmotes(EmoteSet):
	"""Stores all global Twitch Emotes."""

	def __init__(self):
		"""Call the super."""
		super().__init__(0)


class FFZChannelEmotes(EmoteSet):
	"""Stores all FFZ Emotes for a channel."""

	def __init__(self, name: str, set_id: int):
		"""Call the super."""
		self.name = name
		super().__init__(set_id)
