import random
import traceback
import pickle
import re
import os
import sys
from graphics import *
import time
import tkinter.font as tkfont
import decimal
import inspect
import io
import tokenize
from datetime import datetime
import dis
import struct
import array
import types
import functools
import weakref
import warnings
import pynput


def clear():
	if os.system("clear") != 0:
		if os.system("cls") != 0:
			print("Clearing the screen is not supported on this device")

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

try:
	_array_to_bytes = array.array.tobytes
except AttributeError:
	_array_to_bytes = array.array.tostring


class _Bytecode:
	def __init__(self):
		code = (lambda: x if x else y).__code__.co_code
		opcode, oparg = struct.unpack_from('BB', code, 2)

		# Starting with Python 3.6, the bytecode format has changed, using
		# 16-bit words (8-bit opcode + 8-bit argument) for each instruction,
		# as opposed to previously 24 bit (8-bit opcode + 16-bit argument)
		# for instructions that expect an argument and otherwise 8 bit.
		# https://bugs.python.org/issue26647
		if dis.opname[opcode] == 'POP_JUMP_IF_FALSE':
			self.argument = struct.Struct('B')
			self.have_argument = 0
			# As of Python 3.6, jump targets are still addressed by their
			# byte unit. This is matter to change, so that jump targets,
			# in the future might refer to code units (address in bytes / 2).
			# https://bugs.python.org/issue26647
			self.jump_unit = 8 // oparg
		else:
			self.argument = struct.Struct('<H')
			self.have_argument = dis.HAVE_ARGUMENT
			self.jump_unit = 1

		self.has_loop_blocks = 'SETUP_LOOP' in dis.opmap
		self.has_pop_except = 'POP_EXCEPT' in dis.opmap
		self.has_setup_with = 'SETUP_WITH' in dis.opmap
		self.has_setup_except = 'SETUP_EXCEPT' in dis.opmap
		self.has_begin_finally = 'BEGIN_FINALLY' in dis.opmap

	@property
	def argument_bits(self):
		return self.argument.size * 8


_BYTECODE = _Bytecode()


# use a weak dictionary in case code objects can be garbage-collected
_patched_code_cache = weakref.WeakKeyDictionary()
try:
	_patched_code_cache[_Bytecode.__init__.__code__] = None
except TypeError:
	_patched_code_cache = {}  # ...unless not supported


def _make_code(code, codestring):
	try:
		return code.replace(co_code=codestring)  # new in 3.8+
	except AttributeError:
		args = [
			code.co_argcount,  code.co_nlocals,     code.co_stacksize,
			code.co_flags,     codestring,          code.co_consts,
			code.co_names,     code.co_varnames,    code.co_filename,
			code.co_name,      code.co_firstlineno, code.co_lnotab,
			code.co_freevars,  code.co_cellvars
		]

		try:
			args.insert(1, code.co_kwonlyargcount)  # PY3
		except AttributeError:
			pass

		return types.CodeType(*args)


def _parse_instructions(code, yield_nones_at_end=0):
	extended_arg = 0
	extended_arg_offset = None
	pos = 0

	while pos < len(code):
		offset = pos
		if extended_arg_offset is not None:
			offset = extended_arg_offset

		opcode = struct.unpack_from('B', code, pos)[0]
		pos += 1

		oparg = None
		if opcode >= _BYTECODE.have_argument:
			oparg = extended_arg | _BYTECODE.argument.unpack_from(code, pos)[0]
			pos += _BYTECODE.argument.size

			if opcode == dis.EXTENDED_ARG:
				extended_arg = oparg << _BYTECODE.argument_bits
				extended_arg_offset = offset
				continue

		extended_arg = 0
		extended_arg_offset = None
		yield (dis.opname[opcode], oparg, offset)

	for _ in range(yield_nones_at_end):
		yield (None, None, None)


def _get_instruction_size(opname, oparg=0):
	size = 1

	extended_arg = oparg >> _BYTECODE.argument_bits
	if extended_arg != 0:
		size += _get_instruction_size('EXTENDED_ARG', extended_arg)
		oparg &= (1 << _BYTECODE.argument_bits) - 1

	opcode = dis.opmap[opname]
	if opcode >= _BYTECODE.have_argument:
		size += _BYTECODE.argument.size

	return size


def _get_instructions_size(ops):
	size = 0
	for op in ops:
		if isinstance(op, str):
			size += _get_instruction_size(op)
		else:
			size += _get_instruction_size(*op)
	return size


def _write_instruction(buf, pos, opname, oparg=0):
	extended_arg = oparg >> _BYTECODE.argument_bits
	if extended_arg != 0:
		pos = _write_instruction(buf, pos, 'EXTENDED_ARG', extended_arg)
		oparg &= (1 << _BYTECODE.argument_bits) - 1

	opcode = dis.opmap[opname]
	buf[pos] = opcode
	pos += 1

	if opcode >= _BYTECODE.have_argument:
		_BYTECODE.argument.pack_into(buf, pos, oparg)
		pos += _BYTECODE.argument.size

	return pos


def _write_instructions(buf, pos, ops):
	for op in ops:
		if isinstance(op, str):
			pos = _write_instruction(buf, pos, op)
		else:
			pos = _write_instruction(buf, pos, *op)
	return pos


def _warn_bug(msg):
	warnings.warn("Internal error detected" +
				  " - result of with_goto may be incorrect. (%s)" % msg)


class _BlockStack(object):
	def __init__(self, labels, gotos):
		self.stack = []
		self.block_counter = 0
		self.last_block = None
		self.labels = labels
		self.gotos = gotos

	def _replace_in_stack(self, stack, old_block, new_block):
		for i, block in enumerate(stack):
			if block == old_block:
				stack[i] = new_block

	def replace(self, old_block, new_block):
		self._replace_in_stack(self.stack, old_block, new_block)

		for label in self.labels:
			_, _, label_blocks = self.labels[label]
			self._replace_in_stack(label_blocks, old_block, new_block)

		for goto in self.gotos:
			_, _, _, goto_blocks = goto
			self._replace_in_stack(goto_blocks, old_block, new_block)

	def push(self, opname, target_offset=None, previous=None):
		self.block_counter += 1
		self.stack.append((opname, target_offset,
						   previous, self.block_counter))

	def pop(self):
		if self.stack:
			self.last_block = self.stack.pop()
			return self.last_block
		else:
			_warn_bug("can't pop block")

	def pop_of_type(self, type):
		if self.stack and self.top()[0] != type:
			_warn_bug("mismatched block type")
		else:
			return self.pop()

	def copy_to_list(self):
		return list(self.stack)

	def top(self):
		return self.stack[-1] if self.stack else None

	def __len__(self):
		return len(self.stack)


def _find_labels_and_gotos(code):
	labels = {}
	gotos = []

	block_stack = _BlockStack(labels, gotos)

	opname1 = oparg1 = offset1 = None
	opname2 = oparg2 = offset2 = None
	opname3 = oparg3 = offset3 = None

	for opname4, oparg4, offset4 in _parse_instructions(code.co_code, 3):
		endoffset1 = offset2

		# check for block exits
		while block_stack and offset1 == block_stack.top()[1]:
			exit_block = block_stack.pop()
			exit_name = exit_block[0]

			if exit_name == 'SETUP_EXCEPT' and _BYTECODE.has_pop_except:
				block_stack.push('<EXCEPT>', previous=exit_block)
			elif exit_name == 'SETUP_FINALLY':
				block_stack.push('<FINALLY>', previous=exit_block)

		# check for special opcodes
		if opname1 in ('LOAD_GLOBAL', 'LOAD_NAME'):
			if opname2 == 'LOAD_ATTR' and opname3 == 'POP_TOP':
				name = code.co_names[oparg1]
				if name == 'label':
					if oparg2 in labels:
						raise SyntaxError('Ambiguous label {0!r}'.format(
							code.co_names[oparg2]
						))
					labels[oparg2] = (offset1,
									  offset4,
									  block_stack.copy_to_list())
				elif name == 'goto':
					gotos.append((offset1,
								  offset4,
								  oparg2,
								  block_stack.copy_to_list()))
		elif (opname1 in ('SETUP_LOOP',
						  'SETUP_EXCEPT', 'SETUP_FINALLY',
						  'SETUP_WITH', 'SETUP_ASYNC_WITH')) or \
			 (not _BYTECODE.has_loop_blocks and opname1 == 'FOR_ITER'):
			block_stack.push(opname1, endoffset1 + oparg1)
		elif opname1 == 'POP_EXCEPT':
			top_block = block_stack.top()
			if not _BYTECODE.has_setup_except and \
			   top_block and top_block[0] == '<FINALLY>':
				# in 3.8, only finally blocks are supported, so we must
				# determine whether it's except/finally ourselves
				block_stack.replace(top_block,
									('<EXCEPT>',) + top_block[1:])
				_, _, setup_block, _ = top_block
				block_stack.replace(setup_block,
									('SETUP_EXCEPT',) + setup_block[1:])
			block_stack.pop_of_type('<EXCEPT>')
		elif opname1 == 'END_FINALLY':
			# Python puts END_FINALLY at the very end of except
			# clauses, so we must ignore it in the wrong place.
			if block_stack and block_stack.top()[0] == '<FINALLY>':
				block_stack.pop_of_type('<FINALLY>')
		elif opname1 in ('WITH_CLEANUP', 'WITH_CLEANUP_START'):
			if _BYTECODE.has_setup_with:
				# temporary block to match END_FINALLY
				block_stack.push('<FINALLY>')
			else:
				# python 2.6 - finally was actually with
				last_block = block_stack.last_block
				block_stack.replace(last_block,
									('SETUP_WITH',) + last_block[1:])

		opname1, oparg1, offset1 = opname2, oparg2, offset2
		opname2, oparg2, offset2 = opname3, oparg3, offset3
		opname3, oparg3, offset3 = opname4, oparg4, offset4

	if block_stack:
		_warn_bug("block stack not empty")

	return labels, gotos


def _inject_nop_sled(buf, pos, end):
	while pos < end:
		pos = _write_instruction(buf, pos, 'NOP')


def _patch_code(code):
	new_code = _patched_code_cache.get(code)
	if new_code is not None:
		return new_code

	labels, gotos = _find_labels_and_gotos(code)
	buf = array.array('B', code.co_code)

	for pos, end, _ in labels.values():
		_inject_nop_sled(buf, pos, end)

	for pos, end, label, origin_stack in gotos:
		try:
			_, target, target_stack = labels[label]
		except KeyError:
			raise SyntaxError('Unknown label {0!r}'.format(
				code.co_names[label]
			))

		target_depth = len(target_stack)
		if origin_stack[:target_depth] != target_stack:
			raise SyntaxError('Jump into different block')

		ops = []
		for block, _, _, _ in reversed(origin_stack[target_depth:]):
			if block == 'FOR_ITER':
				ops.append('POP_TOP')
			elif block == '<EXCEPT>':
				ops.append('POP_EXCEPT')
			elif block == '<FINALLY>':
				ops.append('END_FINALLY')
			else:
				ops.append('POP_BLOCK')
				if block in ('SETUP_WITH', 'SETUP_ASYNC_WITH'):
					ops.append('POP_TOP')
				# END_FINALLY is needed only in pypy,
				# but seems logical everywhere
				if block in ('SETUP_FINALLY', 'SETUP_WITH',
							 'SETUP_ASYNC_WITH'):
					ops.append('BEGIN_FINALLY' if
							   _BYTECODE.has_begin_finally else
							   ('LOAD_CONST', code.co_consts.index(None)))
					ops.append('END_FINALLY')

		ops.append(('JUMP_ABSOLUTE', target // _BYTECODE.jump_unit))

		if pos + _get_instructions_size(ops) > end:
			# not enough space, add code at buffer end and jump there
			buf_end = len(buf)

			go_to_end_ops = [('JUMP_ABSOLUTE', buf_end // _BYTECODE.jump_unit)]

			if pos + _get_instructions_size(go_to_end_ops) > end:
				# not sure if reachable
				raise SyntaxError('Goto in an incredibly huge function')

			pos = _write_instructions(buf, pos, go_to_end_ops)
			_inject_nop_sled(buf, pos, end)

			buf.extend([0] * _get_instructions_size(ops))
			_write_instructions(buf, buf_end, ops)
		else:
			pos = _write_instructions(buf, pos, ops)
			_inject_nop_sled(buf, pos, end)

	new_code = _make_code(code, _array_to_bytes(buf))

	_patched_code_cache[code] = new_code
	return new_code


def with_goto(func_or_code):
	if isinstance(func_or_code, types.CodeType):
		return _patch_code(func_or_code)

	return functools.update_wrapper(
		types.FunctionType(
			_patch_code(func_or_code.__code__),
			func_or_code.__globals__,
			func_or_code.__name__,
			func_or_code.__defaults__,
			func_or_code.__closure__,
		),
		func_or_code
	)


def getTime():
	now = datetime.now()
	return [now.hour, now.minute, now.second]


def getDate():
	now = datetime.now()
	return [now.year, now.month, now.day]


def dayOfWk(year, month, day):
	dt = datetime.strptime('{year}-{month:02d}-{day:02d}'.format(year=year, month=month, day=day), '%Y-%m-%d')
	return int(dt.strftime('%w')) + 1 # sunday would be zero, so shift everything up by 1 so that sunday is 1


def decistmt(s):
	# Function for parsing a line of code and making all floats into decimal objects

	# List containing all tokens of new statement
	result = []

	# Tokenize statement
	tokens = tokenize.tokenize(io.BytesIO(s.encode('utf-8')).readline)

	# Iterate over tokens
	for toknum, tokval, _, _, _ in tokens:

		# Test if current token is a number and contains a '.' in order to detect floats
		if toknum == tokenize.NUMBER and '.' in tokval: # is float

			# Current token is float, so insert a new decimal object into the new statement instead of the current token
			# Example: 3.3 -> decimal.Decimal("3.3")
			result.extend([
				(tokenize.NAME, 'decimal'),
				(tokenize.OP, '.'),
				(tokenize.NAME, 'Decimal'),
				(tokenize.OP, '('),
				(tokenize.STRING, repr(tokval)),
				(tokenize.OP, ')')
			])
		else:
			# Current token is not a float, append it to the new statement without modification
			result.append((toknum, tokval))

	# Convert token list back into source code
	return tokenize.untokenize(result).decode('utf-8')


def fix_floating_point(f):
	# Decorator for fixing floating-point arithmetic within a function
	def wrapper(*args, **kwargs):
		# Get the source of the function as a list (each element is one line)
		src = inspect.getsource(f).split('\n')
		# Initiate variable for creation of new source code. Starts with function definition
		newsrc = src[1] + '\n'

		# Iterate over function source; skip decorator and function definition
		for line in src[2:]:
			# Expand tabs for spaces in order to calculate indent size
			line = line.expandtabs(4)

			# Calculate amount of indentation for line
			indent = len(line) - len(line.lstrip())

			# Parse and adjust line of code with decistmt function defined above, then add to new source code
			newsrc += '{}{}\n'.format(' ' * indent, decistmt(line))

		# Exec new source code after adjustments to create a new local function
		exec(newsrc)

		# Call that new function that we just created; has the same name as the decorated function so we can just use f.__name__
		locals()[f.__name__]()

	# Return wrapper function
	return wrapper


BLUE = 10
RED = 11
BLACK = 12
MAGENTA = 13
GREEN = 14
ORANGE = 15
BROWN = 16
NAVY = 17
LTBLUE = 18
YELLOW = 19
WHITE = 20
LTGRAY = 21
MEDGRAY = 22
GRAY = 23
DARKGRAY = 24

class InvalidColorError(Exception):
	pass

class Draw:
	def __init__(self):
		self.win = None
		self.winOpen = False
		self.pixels = {}
		self.points = {}
		self.texts = {}
		self.colors = {'10': 'blue', '11': 'red', '12': 'black', '13': 'magenta', '14': 'green', '15': 'orange', '16': 'brown', '17': 'navy', '18': 'light sky blue', '19': 'yellow', '20': 'white', '0': 'white', '21': 'light gray', '22': 'dark gray', '23': 'gray', '24': 'dark slate gray'}
		for _ in range(1, 10):
			self.colors[str(_)] = 'blue'
		self.currentTextColor = 'blue'

	def _slow(function):
		def wrapper(*args, **kwargs):
			function(*args, **kwargs)
			time.sleep(0.01)
		return wrapper

	def openWindow(self):
		# The TI-84 Plus CE has a graph resolution of 250x160 pixels
		# Not to be confused with the screen resolution of 320x240 pixels
		if self.winOpen is False:
			self.win = GraphWin('ti842py', 250, 160)
			self.win.setBackground('white')
			self.winOpen = True

	def closeWindow(self):
		if self.winOpen is True:
			self.win.close()
			self.winOpen = False

	def graphCoordsToPixels(self, x, y, minX=-10, maxX=10, minY=-10, maxY=10):
		# Can work for vertical or horizontal coords
		xs = (decimal.Decimal(maxX) - decimal.Decimal(minX)) / 250
		ys = (decimal.Decimal(minY) - decimal.Decimal(maxY)) / 160
		horiz = (decimal.Decimal(x) - decimal.Decimal(minX)) / decimal.Decimal(xs)
		vertical = (decimal.Decimal(y) - decimal.Decimal(maxY)) / decimal.Decimal(ys)
		return horiz, vertical

	def tiColorToGraphicsColor(self, color, isBackground=False):
		if int(color) not in range(1, 25):
			raise InvalidColorError(f'The specified color value "{color}" is not in range 1-24')
		color = str(color)

		color = re.sub(r'(\d+)', lambda m: self.colors.get(m.group(), '[ERR:DOMAIN]'), color)

		return color

	@_slow
	def backgroundOn(self, color):
		self.win.setBackground(self.tiColorToGraphicsColor(color, isBackground=True))

	@_slow
	def backgroundOff(self):
		self.win.setBackground('white')

	def clrDraw(self):
		for item in self.win.items[:]:
			item.undraw()
		self.win.update()

	@_slow
	def circle(self, x, y, r, color=10, linestyle=''):
		# TODO: Implement linestyle
		c = Circle(Point(self.graphCoordsToPixels(x), self.graphCoordsToPixels(y)), r)
		c.setOutline(self.tiColorToGraphicsColor(color))
		c.draw(self.win)

	@_slow
	def line(self, x1, y1, x2, y2, erase=1, color=10, style=1):
		# TODO: Erase and style not implemented yet
		x1, y1 = self.graphCoordsToPixels(x1, y1)
		x2, y2 = self.graphCoordsToPixels(x2, y2)
		line = Line(Point(x1, y1), Point(x2, y2))
		line.setOutline(self.tiColorToGraphicsColor(color))
		line.draw(self.win)

	@_slow
	def textColor(self, color):
		self.currentTextColor = self.tiColorToGraphicsColor(color)

	@_slow
	def text(self, row, column, *args):
		# column = x, row = y
		text = ''.join([str(arg) for arg in args])
		fontsize = 7

		# Calculate correct center value based on text width
		font = tkfont.Font(family='helvetica', size=fontsize, weight='normal')
		text_width = font.measure(text) // 2
		text_height = font.metrics('linespace') // 2
		column += text_width
		row += text_height

		# Undraw previous text
		# TODO: draw background behind it instead, maybe
		if str(column) in self.texts:
			if str(row) in self.texts[str(column)]:
				self.texts[str(column)][str(row)].undraw()
				del self.texts[str(column)][str(row)]

		message = Text(Point(column, row), text.upper())
		message.setTextColor(self.currentTextColor)
		message.setSize(fontsize)
		message.draw(self.win)
		if str(row) not in self.texts:
			self.texts[str(column)] = {}
		self.texts[str(column)][str(row)] = message

	@_slow
	def pxlOn(self, row, column, color=10):
		# Row = y; Column = x
		pnt = Point(column, row)
		pnt.setOutline(self.tiColorToGraphicsColor(color))
		if column not in self.pixels:
			self.pixels[str(column)] = {}
		self.pixels[str(column)][str(row)] = pnt

		pnt.draw(self.win)

	@_slow
	def pxlOff(self, row, column):
		if str(column) in self.pixels:
			if str(row) in self.pixels[str(column)]:
				self.pixels[str(column)][str(row)].undraw()
				del self.pixels[str(column)][str(row)]

	@_slow
	def pxlTest(self, row, column):
		if str(column) in self.pixels and str(row) in self.pixels[str(column)]:
			return True
		return False

	@_slow
	def ptOn(self, x, y, mark=1, color=10):
		x, y = self.graphCoordsToPixels(x, y)

		if str(x) not in self.points:
			self.points[str(x)] = {}
		if str(y) not in self.points[str(x)]:
			self.points[str(x)][str(y)] = {}

		# If mark is unknown, it will default to 1, so test for 1 with `else`
		if mark in [2, 6]:
			# 3x3 box
			p1x = (x - 3 / 2)
			p1y = (y + 3 / 2)
			p2x = (x + 3 / 2)
			p2y = (y - 3 / 2)
			rec = Rectangle(Point(p1x, p1y), Point(p2x, p2y))
			rec.setOutline(self.tiColorToGraphicsColor(color))
			rec.draw(self.win)
			self.points[str(x)][str(y)][str(mark)] = (rec,)
		elif mark in [3, 7]:
			# 3x3 cross
			line1 = Line(Point(x - 2, y), Point(x + 2, y))
			line1.setOutline(self.tiColorToGraphicsColor(color))
			line1.draw(self.win)
			line2 = Line(Point(x, y - 2), Point(x, y + 2))
			line2.setOutline(self.tiColorToGraphicsColor(color))
			line2.draw(self.win)
			self.points[str(x)][str(y)][str(mark)] = (line1, line2)
		else:
			# Dot
			p1x = (x - 2 / 2)
			p1y = (y + 2 / 2)
			p2x = (x + 2 / 2)
			p2y = (y - 2 / 2)
			rec = Rectangle(Point(p1x, p1y), Point(p2x, p2y))
			rec.setFill(self.tiColorToGraphicsColor(color))
			rec.setOutline(self.tiColorToGraphicsColor(color))
			rec.draw(self.win)
			self.points[str(x)][str(y)][str(mark)] = (rec,)

	@_slow
	def ptOff(self, x, y, mark=1):
		x, y = self.graphCoordsToPixels(x, y)
		if str(x) in self.points:
			if str(y) in self.points[str(x)]:
				if str(mark) in self.points[str(x)][str(y)]:
					for item in self.points[str(x)][str(y)][str(mark)]:
						item.undraw()
					del self.points[str(x)][str(y)][str(mark)]

class DataLoader:
	def __init__(self):
		self.storage_location = os.path.expanduser('~/.ti842py-persistant')

		self.load_data()

	def _load_from_all_objects(self):
		if 'variables' not in self.all_objects:
			self.all_objects['variables'] = {}
		if 'matrices' not in self.all_objects:
			self.all_objects['matrices'] = {}
		if 'lists' not in self.all_objects:
			self.all_objects['lists'] = {}

		self.variables = self.all_objects['variables']
		self.matrices = self.all_objects['matrices']
		self.lists = self.all_objects['lists']

	def load_locals(self, locals_object):
		'''Iterate through locals and sort them into the correct dictionaries'''
		for name in locals_object:
			if re.match(r'^[A-Zθ]{1}$', name):
				self.variables[name] = locals_object[name]
			elif re.match(r'^matrix_[A-J]$', name):
				self.matrices[name] = locals_object[name]
			elif re.match(r'^l[1-6]$', name):
				self.lists[name] = locals_object[name]
		return self

	def write_data(self):
		'''Write loaded data into persistant file'''
		print(self.all_objects)
		with open(self.storage_location, 'wb') as f:
			pickle.dump(self.all_objects, f)

	def load_data(self):
		'''Load persistant data from persistant file.'''
		self.all_objects = {}

		if os.path.isfile(self.storage_location):
			with open(self.storage_location, 'rb') as f:
				self.all_objects = pickle.load(f)
				print(self.all_objects)

		self._load_from_all_objects()

		return self

	def update_locals(self, locals_object):
		'''Inject loaded data into locals'''
		for item in self.all_objects:
			for key, value in self.all_objects[item].items():
				print(key, value)
				# print(f'{locals_object[key]=}')
				locals_object[key] = value

	def exception_hook(self, exc_type, value, tb):
		traceback.print_exception(exc_type, value, tb)

		# iterate to last frame in traceback
		while tb.tb_next:
			tb = tb.tb_next

		self.load_locals(tb.tb_frame.f_locals)
		self.write_data()

	def __str__(self):
		return repr(self.all_objects)

persistant_data_loader = DataLoader()
sys.excepthook = persistant_data_loader.exception_hook
# thing = DataLoader().load_locals(locals().copy())
# print(thing)
# thing.write_data()

# thing = DataLoader().load_data()
# thing.update_locals(locals())
# print(locals())
# print(A)


# @fix_floating_point
# @with_goto
def main():
	get_key = GetKey()
	listener = pynput.keyboard.Listener(on_press=get_key.set_last_key)
	listener.start()
	draw = Draw()
	draw.openWindow()
	l1, l2, l3, l4, l5, l6 = ([None for _ in range(0, 999)] for _ in range(6)) # init lists
	A = B = C = D = E = F = G = H = I = J = K = L = M = N = O = P = Q = R = S = T = U = V = W = X = Y = Z = θ = 0 # init variables
	J = 0
	# clear()
	# persistant_data_loader.load_locals(locals())
	# persistant_data_loader.write_data()
	# print(locals().update({'A': 1}))
	print(locals())
	# persistant_data_loader.load_data()
	# persistant_data_loader.update_locals(locals())
	locals()['FUN'] = 1
	print(FUN)

	draw.textColor(15)
	draw.backgroundOn(WHITE)
	# UNKNOWN INDENTIFIER: GridOff
	# UNKNOWN INDENTIFIER: AxesOff
	draw.clrDraw()
	draw.text(150,120,"PRESS 'CLEAR' TO EXIT")
	draw.textColor(12)
	label .lbl1
	X = get_key.get_last_key()
	if X == 45:
		goto .lbl6
	else:
		goto .lbl4
		label .lbl4
		draw.line(random.random()*10,random.random()*10,random.random()*10,random.random()*10,1,random.randint(10,20))
		l1 = getTime()
		l2 = getDate()
		X = l1[0]
		Y = l1[1]
		Z = l1[2]
		A = l2[0]
		B = l2[1]
		C = l2[2]
		if X>12:
			X = X-12
			goto .lbl5
		else:
			label .lbl5
			if X == 0:
				X = 12

			if Z == 0:
				draw.clrDraw()

			label .lbl7
			if Y<10:
				J = 1
				draw.text(0,0,X,":0",Y,":",Z)
				goto .lbl3
			else:
				J = 0
				draw.text(0,0,X,":",Y,":",Z)
				goto .lbl3
				label .lbl3
				if Z>9:
					goto .lbl8
				elif J == 1:
					draw.text(0,0,X,":0",Y,":0",Z)
					goto .lbl8
				else:
					draw.text(0,0,X,":",Y,":0",Z)
					goto .lbl8
					label .lbl8
					D = dayOfWk(A,B,C)*1
					draw.line(-10,7.56,-3.275,7.56,12)
					draw.text(25,0,"DAY OF WEEK:")
					if D == 1:
						draw.text(43,0,"SUNDAY")
						goto .lbl2
					elif D == 2:
						draw.text(43,0,"MONDAY")
						goto .lbl2
					elif D == 3:
						draw.text(43,0,"TUESDAY")
						goto .lbl2
					elif D == 4:
						draw.text(43,0,"WENDSDAY")
						goto .lbl2
					elif D == 5:
						draw.text(43,0,"THURSDAY")
						goto .lbl2
					elif D == 6:
						draw.text(43,0,"FRIDAY")
						goto .lbl2
					else:
						draw.text(43,0,"SATURDAY")
						goto .lbl2
						label .lbl2
						draw.line(-10,2.5,-3.275,2.5,12)
						draw.text(65,0,B,"/",C,"/",A)
						l2 = getTime()
						while l2[2] == l1[2]:
							l2 = getTime()

						goto .lbl1
						label .lbl6
						draw.clrDraw()
						draw.text(30,115,"EXIT?")
						draw.text(50,85,"1-YES")
						draw.text(50,145,"2-NO")
						firstPass = True
						while firstPass is True or not (X == 92 or X == 93):
							firstPass = False
							draw.line(-7.273,8.05,-7.273,-4.15,1,random.randint(13,19))
							draw.line(-7.273,-4.15,6.83,-4.15,1,random.randint(13,19))
							draw.line(6.83,-4.15,6.83,8.05,1,random.randint(13,19))
							draw.line(6.83,8.05,-7.273,8.05,1,random.randint(13,19))
							X = get_key.get_last_key()

						clear()
						if X == 93:
							draw.clrDraw()
							goto .lbl1
						else:
							draw.backgroundOn(BLACK)
							draw.clrDraw()
	try:
		while True:
			draw.win.getMouse()
	except GraphicsError:
		pass
if __name__ == '__main__':
	try:
		main()
	except:
		traceback.print_exc()
		try:
			import sys, termios
			# clear stdin on unix-like systems
			termios.tcflush(sys.stdin, termios.TCIFLUSH)
		except ImportError:
			pass
