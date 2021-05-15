import os

# Windows
if os.name == 'nt':
	import msvcrt

# Posix (Linux, OS X)
else:
	import sys
	import termios
	import atexit
	from select import select


class KBHit:

	def __init__(self):
		'''Creates a KBHit object that you can call to do various keyboard things.
		'''

		if os.name == 'nt':
			pass

		else:

			# Save the terminal settings
			self.fd = sys.stdin.fileno()
			self.new_term = termios.tcgetattr(self.fd)
			self.old_term = termios.tcgetattr(self.fd)

			# New terminal setting unbuffered
			self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
			termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

			# Support normal-terminal reset at exit
			atexit.register(self.set_normal_term)

	def set_normal_term(self):
		''' Resets to normal terminal.  On Windows this is a no-op.
		'''

		if os.name == 'nt':
			pass

		else:
			termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

	def getch(self):
		''' Returns a keyboard character after kbhit() has been called.
			Should not be called in the same program as getarrow().
		'''

		if os.name == 'nt':
			return msvcrt.getch().decode('utf-8')

		else:
			return sys.stdin.read(1)

	def getarrow(self):
		''' Returns an arrow-key code after kbhit() has been called. Codes are
		0 : up
		1 : right
		2 : down
		3 : left
		Should not be called in the same program as getch().
		'''

		if os.name == 'nt':
			msvcrt.getch() # skip 0xE0
			c = msvcrt.getch()
			vals = [72, 77, 80, 75]

		else:
			c = sys.stdin.read(3)[2]
			vals = [65, 67, 66, 68]

		return vals.index(ord(c.decode('utf-8')))

	def kbhit(self):
		''' Returns True if keyboard character was hit, False otherwise.
		'''
		if os.name == 'nt':
			return msvcrt.kbhit()

		else:
			dr, dw, de = select([sys.stdin], [], [], 0)
			return dr != []


kb = KBHit()

keyMap = {
	"f1": 11,
	"f2": 12,
	"f3": 13,
	"f4": 14,
	"f5": 15,
	"ctrl": 21,
	"f6": 22,
	"delete": 23,
	"left": 24,
	"up": 25,
	"right": 26,
	"alt": 31,
	"f10": 32,
	"f7": 33,
	"down": 34,
	"a": 41,
	"b": 42,
	"c": 43,
	"f8": 44,
	"f9": 45,
	"d": 51,
	"e": 52,
	"f": 53,
	"g": 54,
	"h": 55,
	"^": 5,
	"i": 61,
	",": 62,
	"j": 62,
	"(": 63,
	"k": 63,
	")": 64,
	"l": 64,
	"/": 65,
	"m": 65,
	"÷": 65,
	"n": 71,
	"7": 72,
	"o": 72,
	"8": 73,
	"p": 73,
	"9": 74,
	"q": 74,
	"×": 75,
	"*": 75,
	"r": 75,
	"s": 81,
	"4": 82,
	"t": 82,
	"5": 83,
	"u": 83,
	"6": 84,
	"v": 84,
	"-": 85,
	"−": 85,
	"w": 85,
	"=": 91,
	"x": 91,
	"1": 92,
	"y": 92,
	"2": 93,
	"z": 93,
	"3": 94,
	"+": 95,
	"\"": 95,
	"0": 102,
	"space": 102,
	".": 103,
	":": 103,
	"-": 104,
	"?": 104,
	"−": 104,
	"enter": 105
}


def getKey():
	if kb.kbhit():
		c = kb.getch().lower()
		if c in keyMap:
			return keyMap[c]
		return 0
	else:
		return 0
