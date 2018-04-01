"""Module for emote handling."""

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
	index = dict()

	@staticmethod
	def load(name: str):
		"""Load a file from cache.

		Load a file from cache if it exists otherwise raise
		FileNotFoundError.

		:param name: a string to search for in the cache
		:return: a byte-like object
		"""
		if name not in EmoteCache.index:
			path = os.path.join(EmoteCache.location, name)
			if os.path.exists(path):
				EmoteCache.index[name] = path
			else:
				raise FileNotFoundError
		with open(EmoteCache.index[name], 'rb') as cached_file:
			data = cached_file.read()
		return data

	@staticmethod
	def cache(name: str, data: BytesIO):
		"""Cache a byte-like object.

		:param name: a name for the cached file
		:param data: a byte-like object to cache
		"""
		path = os.path.join(EmoteCache.location, name)
		with open(path, 'wb') as cached_file:
			cached_file.write(data.getvalue())
		EmoteCache.index[name] = path


class Emote:
	"""Class to download and store an emote."""

	images = dict()

	def __init__(self, name: str, url: str, emote_type: EmoteTypes):
		"""Create new emote by name and url."""
		self.name = name
		self.url = url
		if not url.endswith('/'):
			self.url += '/'
		self.emote_type = emote_type
		# TODO: make async
		for res in EmoteResolutions:
			self.images[res] = EmoteCache.load(self.name + res)

	def download(self, res: EmoteResolutions):
		"""Download emote image data."""
		suffix = Emote.get_suffix_for_type(res, self.emote_type)
		r = requests.get(self.url + suffix)
		if not r.status_code == 200:
			raise Exception
		b = BytesIO(r.content)
		EmoteCache.cache(self.name + res.value, b)
		self.images[res] = Image.open(b)

	@staticmethod
	def get_suffix_for_type(res: EmoteResolutions, emote_type: EmoteTypes):
		"""Get URL suffix for given emote resolution and type."""
		if emote_type == EmoteTypes.Twitch:
			return str(res.value) + '.0'
		if emote_type == EmoteTypes.FrankerFaceZ:
			value = 4 if res.value == 3 else res.value
			return str(value)
		if emote_type == EmoteTypes.BetterTwitchTV:
			return str(res.value) + 'x'


class EmoteList:
	"""Stores all emotes."""

	def __init__(self):
		"""Create new list of emotes."""
		pass

	def add_emote(self):
		"""Add given emote."""
		pass

	def add_emotes(self):
		"""Add given emotes."""
		pass
