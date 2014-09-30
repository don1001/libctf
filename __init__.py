#!/usr/bin/env python


# sudo pip install pycrypto
import Crypto.Hash.SHA
import Crypto.Hash.SHA256
import Crypto.Hash.MD5
import Crypto.Cipher.AES

# sudo pip install hexdump
import hexdump as m_hexdump

import struct
import sys
import socket
### Trucs que j'utilise tout le temps ###

def sha1(x):
	return Crypto.Hash.SHA.SHA1Hash(x).digest()
def sha256(x):
	return Crypto.Hash.SHA256.SHA256Hash(x).digest()
def md5(x):
	return Crypto.Hash.MD5.MD5Hash(x).digest()
# AES in ECB mode
def aes(data, key, IV="", decrypt=False, mode=Crypto.Cipher.AES.MODE_ECB):
	hdl = Crypto.Cipher.AES.new(key, mode, IV)
	if(decrypt):
		return hdl.decrypt(data)
	else:
		return hdl.encrypt(data)

def aes_cbc(data, key, IV, decrypt=False):
	return aes(data, key, IV=IV, decrypt=decrypt, mode=Crypto.Cipher.AES.MODE_CBC)
def d(x):
	"""Pack to uint32"""
	return struct.pack("<I", x)

def w(x):
	"""Pack to uint16"""
	return struct.pack("<H", x)

def __isprintable__(c):
	val = ord(c)
	if(val >= 0x20 and val < 0x80):
		return True
	return False

# Do not write colors out of tty
__tty__= sys.stdout.isatty()

def color(string, color="red"):
	colors = {
		"red":'\033[91m',
		"green":'\033[92m'
	}
	ENDC= '\033[0m'
	if __tty__:
		return colors[color] + string + ENDC
	else:
		return string

def hexdump(data, highlight = None, output="print", printoffset=0):
	"""output hexdump data with highlight on strings in highlight list"""
	gen = m_hexdump.hexdump(data, result="generator")
	offsets = []
	out = ""
	# if the highlight is a string, make it an array
	if isinstance(highlight, basestring):
		highlight = [highlight]
	# get the (offset, len) of every match in data
	if highlight != None and len(highlight) > 0:
		for h in highlight:
			index = data.find(h)
			while index != -1:
				offsets.append((index, len(h)))
				index = data.find(h, index +1)
	#print offsets
	# convert to a bit mask 
	mask = [False] * len(data)
	for (index, length) in offsets:
		for i in xrange(length):
			mask[index + i] = True
	#print mask

	index = 0
	while index < len(data):
		x = data[index:index+16]
		# Print the offset
		s = "%.8x: "%(index + printoffset)
		# Print first half of hex dump
		for i in xrange(len(x[:8])):
			c = "%.2x "%(ord(x[i]))
			if (mask[index + i]):
				s += color(c, "red")
			else:
				s += c
		s+= " "
		# Print second half of hex dump
		for i in xrange(len(x[8:])):
			c = "%.2x "%(ord(x[8 + i]))
			if (mask[index + i + 8]):
				s += color(c, "red")
			else:
				s += c
		if (len(x) < 16):
			s += " " * 3 * (16-len(x))
		s+= " "
		# Print ascii part
		for i in xrange(len(x)):
			if __isprintable__(x[i]):
				c=x[i]
			else:
				c="."
			if mask[index +i]:
				s += color(c, "red")
			else:
				s += c
		if (output == "print"):
			print s
		else:
			out += s
		index += 16
	if (output == "string"):
		return s

# attempt to do sorta mutable strings
class Buffer(object):
	s=""
	def __init__(self, s="", length=0):
		if (s != "" and length != 0):
			raise Exception("One of s or length must be set")
		if length == 0:
			self.s = s
		else:
			self.s = "\0"*length
	def __getitem__(self, x):
		return self.s.__getitem__(x)
	def __setitem__(self, x, y):
		if isinstance(x, int):
			x = slice(x, x+1, None)
		if (x.stop == None):
			x = slice(x.start, x.start + len(y))
		if (x.start == None):
			x = slice(x.stop - len(y), x.stop)
		#print x
		if (x.stop - x.start != len(y)):
			raise Exception("Replacement string (%d) too big for range[%d:%d]"%(len(y),x.start, x.stop))
		if x.stop > len(self.s):
			self.s += chr(0) * (x.stop - len(self.s))
		self.s = self.s[:x.start] + y + self.s[x.stop:]
	def __str__(self):
		return self.s.__str__()
	def __add__(self, x):
		return Buffer(self.s.__add__(x))
	def __len__(self):
		return self.s.__len__()
	def encode(self, x):
		return self.s.encode(x)
	def decode(self, x):
		return self.s.decode(x)
	def join(self, x, y):
		return self.s.join(x, y)
def __assert__(x):
	if not x:
		 raise Exception("Assertion failed")

def test():
	__assert__(sha1("test") != None)
	__assert__(md5("test") != None)
	__assert__(sha256("test") != None)
	__assert__(d(0x41424344) == "DCBA")
	__assert__(w(0x4142) == "BA")
	#hexdump("A" * 15 + "HELLO" + "B" * 16, "HELLO")
	hexdump("ABCDEFGHAABB",["A", "AA"])
	#hexdump(sha256("test"))
	s = Buffer("abcd")
	__assert__(s[0:4] == "abcd")
	__assert__(s[:4] == "abcd")
	__assert__(s[1:] == "bcd")
	s[4] = 'e'
	s[5:7] = 'fg'
	s[0]="A"
	s[10]="K"
	s[7:]="hij"
	print s
	s[:11]="Hello"
	print s
	__assert__(type(s)==Buffer)
	s+=" World!"
	__assert__(type(s)==Buffer)
	print s
	print len(s)
	print s.encode("hex")
	#s="hello"
	__assert__(type(s)==Buffer)
	x = Buffer(length = 10)
	print x.encode("hex"), len(x)

	#aes test
	x = aes("A"*16, "B"*16)
	hexdump(x)
	hexdump(aes(x, "B"*16, decrypt=True))

	x = aes_cbc("A"*16, "B"*16, IV="C"*16)
	hexdump(x)
	hexdump(aes_cbc(x, "B"*16, IV="C"*16, decrypt=True))
if __name__ == '__main__':
    test()