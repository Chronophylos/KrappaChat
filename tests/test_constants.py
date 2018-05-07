from krappachat.constants import *


def test_colors():
	"""Test default_colors and make sure it's a valid list."""
	assert isinstance(default_colors, list)
	for x in default_colors:
		assert isinstance(x, str)
		assert len(x) == 7
		assert x.startswith('#')
