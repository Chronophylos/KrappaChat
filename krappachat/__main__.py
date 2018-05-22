"""Main file for krappachat."""

import sys

if (__package__ is None or __package__ == "") and not hasattr(sys, 'frozen'):
	# direct call of __main__.py
	import os

	path = os.path.realpath(os.path.abspath(__file__))
	sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

if __name__ == '__main__':
	import krappachat

	krappachat.main()
