import pynput

class GetKey:
	def __init__(self):
		self.last_key = 0
		self.keymap = {
			pynput.keyboard.Key.f1: 11,
			pynput.keyboard.Key.f2: 12,
			pynput.keyboard.Key.f3: 13,
			pynput.keyboard.Key.f4: 14,
			pynput.keyboard.Key.f5: 15,
			"`": 21,
			pynput.keyboard.Key.f6: 22,
			pynput.keyboard.Key.delete: 23,
			pynput.keyboard.Key.left: 24,
			pynput.keyboard.Key.up: 25,
			pynput.keyboard.Key.right: 26,
			"~": 31,
			pynput.keyboard.Key.f10: 32,
			pynput.keyboard.Key.f7: 33,
			pynput.keyboard.Key.down: 34,
			"a": 41,
			"b": 42,
			"c": 43,
			pynput.keyboard.Key.f8: 44,
			pynput.keyboard.Key.f9: 45,
			"d": 51,
			"e": 52,
			"f": 53,
			"g": 54,
			"h": 55,
			"^": 55,
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
			pynput.keyboard.Key.space: 102,
			".": 103,
			":": 103,
			"?": 104,
			pynput.keyboard.Key.enter: 105
		}

	def set_last_key(self, key):
		if hasattr(key, 'char'):
			# convert to string
			key = key.char.lower()

		if key in self.keymap:
			self.last_key = self.keymap[key]

	def get_last_key(self):
		key = self.last_key
		self.last_key = 0
		return key
