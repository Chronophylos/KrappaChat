"""Module for emote handling."""

from enum import Enum
from io import BytesIO

import requests
from PIL import Image


class EmoteType(Enum):
	"""Enum class to specify emote type."""

	Twitch = 0,
	FrankerFaceZ = 1,
	BetterTwitchTV = 2,


class EmoteResolution(Enum):
	"""Enum class to specify emote resolution."""

	Small = 1
	Medium = 2
	Big = 3


class Emote:
	"""Class to download and store an emote."""

	images = dict()

	def __init__(self, name: str, url: str, emote_type: EmoteType):
		"""Create new emote by name and url."""
		self.name = name
		self.url = url
		if not url.endswith('/'):
			self.url += '/'
		self.emote_type = emote_type

	# TODO: load cached images

	def download(self):
		"""Download emote image data."""
		# TODO: cache images
		for res in EmoteResolution:
			suffix = Emote.get_suffix_for_type(res, self.emote_type)
			r = requests.get(self.url + suffix)
			if not r.status_code == 200:
				raise Exception
			self.images[res] = Image.open(BytesIO(r.content))

	@staticmethod
	def get_suffix_for_type(res: EmoteResolution, emote_type: EmoteType):
		"""Get URL suffix for given emote resolution and type."""
		if emote_type == EmoteType.Twitch:
			return str(res.value) + '.0'
		if emote_type == EmoteType.FrankerFaceZ:
			value = 4 if res.value == 3 else res.value
			return str(value)
		if emote_type == EmoteType.BetterTwitchTV:
			return str(res.value) + 'x'


class EmoteList:
	"""Stores all cached emotes."""

	def __init__(self):
		"""Create new list of emotes."""
		pass

	def add_emote(self):
		"""Add given emote."""
		pass

	def add_emotes(self):
		"""Add given emotes."""
		pass
