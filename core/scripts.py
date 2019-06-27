from .helper import log
import chardet

__doc__ = "Some functions that can make certain tasks easier."

def dcEscape(content: str, *args) -> str:
	"""
	Discord Escape
	Escape all formatting characters in Discord by adding a backslash in front.

	Usage: dcEscape(content: str[, 'format', 'ping', 'quote'])
	Format: escape discord formatting characters
	Ping: escape @everyone and @here
	Quote: removes all ` characters
	Defaults to replace all possible characters.
	"""
	if not args:
		args = ('format', 'ping', 'quote')
	if 'format' in args:
		formatChars = ("*", "<", '>', '_', '`', '|', '~')
		for char in formatChars:
			content = content.replace(char, "\\" + char)
	if 'ping' in args:
		content = content.replace("@everyone", "@\u200beveryone").replace("@here", "@\u200bhere")
	if 'quote' in args:
		content = content.replace("`", '')
	return content

def decode(content: bytes, codec: str = 'utf8') -> str or bytes:
	"""
	Decode
	Dynamicly decode bytes string to text. If not found, return original.

	Usage: decode(content, codec='utf8')
	content: bytes object to decode
	codec: amy python supported codec
	"""
	if not type(content) == bytes:
		log(None, content="Content not equal with bytes.")
		return content
	try:
		log(content="Trying to decode with object's intended encoding (or utf8)...")
		content = content.decode()
		log(content="Decode done with object's intended encoding (or utf8).")
	except UnicodeDecodeError:
		try:
			log(None, content="Trying to decode content with {}.".format(codec))
			content = content.decode(codec)
			log(None, content="Decode done with {}.".format(codec))
		except UnicodeDecodeError:
			try:
				log(None, content= "Can't decode with {}.".format(codec))
				chardetres = chardet.detect(content)
				content = content.decode(chardetres['encoding'])
				log(None, content= f"Chardet outputted {chardetres}")
			except TypeError:
				log(None, content="TypeError occured, returning original string.")
				return content
	return content