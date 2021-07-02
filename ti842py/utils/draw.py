from graphics import *
import time
import tkinter.font as tkfont
import decimal


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

class Draw:
	def __init__(self):
		self.win = None
		self.winOpen = False
		self.pixels = {}
		self.points = {}
		self.texts = {}
		self.colors = {'BLUE': 'blue', 'RED': 'red', 'BLACK': 'black', 'MAGENTA': 'magenta', 'GREEN': 'green', 'ORANGE': 'orange', 'BROWN': 'brown', 'NAVY': 'navy', 'LTBLUE': 'light sky blue', 'YELLOW': 'yellow', 'WHITE': 'white', 'LTGRAY': 'light gray', 'MEDGRAY': 'dark gray', 'GRAY': 'gray', 'DARKGRAY': 'dark slate gray'}
		self.colorNumbers = {'10': 'blue', '11': 'red', '12': 'black', '13': 'magenta', '14': 'green', '15': 'orange', '16': 'brown', '17': 'navy', '18': 'light sky blue', '19': 'yellow', '20': 'white', '0': 'white', '21': 'light gray', '22': 'dark gray', '23': 'gray', '24': 'dark slate gray'}
		for _ in range(1, 10):
			self.colorNumbers[str(_)] = 'blue'
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
		color = str(color)
		for color1, color2 in self.colors.items():
			color = color.replace(color1, color2)
		for color1, color2 in self.colorNumbers.items():
			color = color.replace(color1, color2)
		if color not in self.colors.values():
			# Failsafe
			if not isBackground:
				print(f'WARNING: Unknown color: {color}. defaulting to blue.')
				color = 'blue'
			else:
				print(f'WARNING: Unknown color: {color}. defaulting to white.')
				color = 'white'
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
	def circle(self, x, y, r, color='blue', linestyle=''):
		# TODO: Implement linestyle
		c = Circle(Point(self.graphCoordsToPixels(x), self.graphCoordsToPixels(y)), r)
		c.setOutline(self.tiColorToGraphicsColor(color))
		c.draw(self.win)

	@_slow
	def line(self, x1, y1, x2, y2, erase=1, color='blue', style=1):
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
	def pxlOn(self, row, column, color='blue'):
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
	def ptOn(self, x, y, mark=1, color='blue'):
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
