import re
import logging
import os
import shutil

try:
	from . import parsing_utils
except ImportError:
	import parsing_utils

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


class TIBasicParser:
	def __init__(self, basic, multiplication, floating_point, turbo_draw):
		if isinstance(basic, list):
			self.basic = basic
		elif isinstance(basic, str):
			self.basic = [line.strip() for line in basic.split("\n")]
		else:
			raise TypeError("basic must be list or str, not {}".format(str(type(basic))))

		self.multiplication = multiplication
		self.floating_point = floating_point
		self.turbo_draw = turbo_draw

		# Utility Functions
		self.UTILS = {"wait": {"code": [""], "imports": ["import time"], "enabled": False}, "menu": {"code": [""], "imports": ["import dialog"], "enabled": False}, "math": {"code": [""], "imports": ["import math"], "enabled": False}, 'random': {'code': [''], 'imports': ['import random'], 'enabled': False}}
		here = os.path.abspath(os.path.dirname(__file__))
		for file in [file for file in os.listdir(os.path.join(here, "utils")) if os.path.isfile(os.path.join(here, "utils", file))]:
			with open(os.path.join(here, "utils", file)) as f:
				self.UTILS[os.path.splitext(file)[0]] = {}
				self.UTILS[os.path.splitext(file)[0]]["code"] = [line.rstrip() for line in f.readlines() if not line.startswith("import ") and not line.startswith("from ")]
				f.seek(0)
				self.UTILS[os.path.splitext(file)[0]]["imports"] = [line.rstrip() for line in f.readlines() if line.startswith("import ") or line.startswith("from ")]
				self.UTILS[os.path.splitext(file)[0]]["enabled"] = False

		if self.floating_point:
			self.UTILS['fix_floating_point']['enabled'] = True

		if self.turbo_draw:
			self.UTILS['draw']['code'] = [line for line in self.UTILS['draw']['code'] if '@_slow' not in line]

		self.drawLock = False

	def convertLine(self, index, line):
		# TODO: possible curses interface instead of just printing and outputting

		statement = ""

		# Fix lists
		number_table = {'₁': '1', '₂': '2', '₃': '3', '₄': '4', '₅': '5', '₆': '6'}
		line = re.sub('(?:L|l)([₁₂₃₄₅₆]){1}', lambda m: 'L' + number_table[m.group(1)], line)

		# TODO: Make rules for :, dont fully understand it yet
		if self.skipLine > 0:
			self.skipLine -= 1
			return None
		elif line == "":
			# Blank
			statement = ""
		# Disp
		elif line.startswith("Disp "):
			statement = re.search("Disp (.*[^)])", line).groups(1)[0]
			statement = "print(" + parsing_utils.closeOpen(statement) + ", sep=\"\")"
		# Variables
		elif "->" in line or "→" in line:
			statement = re.split("->|→", line)
			statement.reverse()

			if statement[0] == "rand":
				# seeding rand
				statement = "random.seed(" + statement[-1] + ")"
				self.UTILS["random"]["enabled"] = True
			else:
				statement = " = ".join(statement)
		# If
		elif line.startswith("If "):
			try:
				if self.basic[index + 1] == "Then":
					# If/Then statement
					statement = "if " + line.lstrip("If ")
					statement = parsing_utils.fixEquals(statement)
					statement = statement + ":"
					self.indentIncrease = True
				elif re.search(r"If.*[^\"]:", line) is not None:
					# If statement on 1 line
					statement = ["if " + parsing_utils.fixEquals(line.lstrip("If ").split(":", 1)[0]) + ":", "\t" + self.convertLine(index + 1, line.lstrip("If ").split(":", 1)[1])]
				else:
					# If statement on 2 lines; no Then
					statement = ["if " + parsing_utils.fixEquals(line.lstrip("If ")) + ":", '\t' + self.convertLine(index + 1, self.basic[index + 1])]

					if self.basic[index + 2].startswith('End'):
						self.skipLine = 2 # prioritize ending the if statement
					else:
						self.skipLine = 1 # skip next line since its incorporated into this line
			except IndexError:
				# Last line in file, test for 1 line If statement
				if re.search(r"If.*[^\"]:", line) is not None:
					statement = ["if " + parsing_utils.fixEquals(line.lstrip("If ").split(":", 1)[0]) + ":", "\t" + self.convertLine(index + 1, line.lstrip("If ").split(":", 1)[1])]
		elif line == "Then":
			return None
		# Elif
		elif line == "Else" and self.basic[index + 1].startswith("If"):
			statement = "elif " + self.basic[index + 1].lstrip("If ")
			statement = parsing_utils.fixEquals(statement)
			statement = statement + ":"
			self.indentDecrease = True
			self.indentIncrease = True
			self.skipLine = 1
		# Else
		elif line == "Else" and not (self.basic[index + 1].startswith("If")):
			statement = "else:"
			self.indentDecrease = True
			self.indentIncrease = True
		elif line == "ClrHome":
			self.UTILS["clear"]["enabled"] = True
			statement = "clear()"
		elif line == "End":
			self.indentDecrease = True
		# Input
		elif line.startswith("Input"):
			statement = line.split(",")
			if len(statement) > 1:
				if "," in statement[1]:
					statement = statement[1] + " = [toNumber(number) for number in input(" + parsing_utils.closeOpen(statement[0][6:]) + ")]"
				else:
					statement = statement[1] + " = toNumber(input(" + parsing_utils.closeOpen(statement[0][6:]) + "))"
			else:
				if statement[0].strip() != "Input":
					# No input text
					statement = statement[0][6:] + " = toNumber(input(\"?\"))"
				else:
					statement = "input()"
			self.UTILS["toNumber"]["enabled"] = True
		# For loop
		elif line.startswith("For"):
			args = line[4:].strip("()").split(",")
			statement = "for " + args[0] + " in range(" + args[1] + ", " + args[2]
			if len(args) == 4:
				statement += ", " + args[3]
			statement += "):"
			self.indentIncrease = True
		# While loop
		elif line.startswith("While "):
			statement = "while " + parsing_utils.fixEquals(line[6:]) + ":"
			self.indentIncrease = True
		# Repeat loop (tests at bottom)
		elif line.startswith("Repeat "):
			statement = ["firstPass = True", "while firstPass is True or not (" + parsing_utils.fixEquals(line[7:]) + "):", "\tfirstPass = False"]
			self.indentIncrease = True
		# Pause
		elif line.startswith("Pause"):
			args = line[5:].strip().split(",")
			if len(args) <= 1:
				statement = "input("
				if len(args) == 1:
					statement += str(args[0]) + ")"
			else:
				statement = ["print(" + str(args[0]) + ")", "time.sleep(" + args[1] + ")"]
				self.UTILS["wait"]["enabled"] = True
		# Wait
		elif line.startswith("Wait"):
			statement = "time.sleep(" + line[5:] + ")"
			self.UTILS["wait"]["enabled"] = True
		# Stop
		elif line == "Stop":
			statement = "exit()"
		# DelVar
		elif line.startswith("DelVar"):
			statement = "del " + line[7:]
		# Prompt
		# TODO: Fix prompt after Output going over output
		elif line.startswith("Prompt"):
			variable = line[7:]
			if "," in variable:
				statement = variable + " = [toNumber(number) for number in input(\"" + variable + "=?\").split(\",\")]"
			else:
				statement = variable + " = toNumber(input(\"" + variable + "=?\"))"
			self.UTILS["toNumber"]["enabled"] = True
		# Goto (eww)
		elif line.startswith("Goto "):
			statement = "goto .lbl" + line[5:]
			self.UTILS["goto"]["enabled"] = True
		# Lbl
		elif line.startswith("Lbl "):
			statement = "label .lbl" + line[4:]
			statement = statement.replace(':', '\n') # you can end lbl with :
			self.UTILS["goto"]["enabled"] = True
		# Output
		elif line.startswith("Output("):
			statement = parsing_utils.noStringReplace('Output', 'output', [parsing_utils.closeOpen(line)])
			self.UTILS["output"]["enabled"] = True
		# DS<(
		elif line.startswith("DS<("):
			variable, value = line[3:].strip("()").split(",")
			statement = ["if " + variable + " - 1 >= " + value + ":", "\t" + self.convertLine(index + 1, self.basic[index + 1])]
			self.skipLine = 1
		# IS>(
		elif line.startswith("IS>("):
			variable, value = line[3:].strip("()").split(",")
			statement = ["if " + variable + " + 1 <= " + value + ":", "\t" + self.convertLine(index + 1, self.basic[index + 1])]
			self.skipLine = 1
		# Menu
		elif line.startswith("Menu"):
			if shutil.which("dialog") is None:
				logger.warning("dialog executable not found. Please install dialog to use menus")
			tiMenu = line[4:].strip("()").split(",")
			title = tiMenu.pop(0).strip(" \"")
			options = []
			for i in range(0, len(tiMenu), 2):
				options.extend([tiMenu[i].strip(" \""), tiMenu[i + 1].strip(" \"")])
			statement = parsing_utils.menu(title, options)
			self.UTILS["menu"]["enabled"] = True
			self.UTILS['clear']['enabled'] = True
		# Line(
		elif line.startswith('Line('):
			statement = parsing_utils.closeOpen(line.replace('Line(', 'draw.line('))
			self.UTILS['draw']['enabled'] = True

		# BackgroundOff
		elif line == 'BackgroundOff':
			statement = 'draw.backgroundOff()'
			self.UTILS['draw']['enabled'] = True

		# Background On
		elif line.startswith('BackgroundOn '):
			statement = line.replace('BackgroundOn ', 'draw.backgroundOn(')
			statement = statement.split('(')[0] + '("' + statement.split('(')[1] + '")'
			self.UTILS['draw']['enabled'] = True

		# ClrDraw
		elif line == 'ClrDraw':
			statement = 'draw.clrDraw()'
			self.UTILS['draw']['enabled'] = True

		# Circle
		elif line.startswith('Circle('):
			statement = parsing_utils.closeOpen(line.replace('Circle(', 'draw.circle('))
			self.UTILS['draw']['enabled'] = True

		# Text
		elif line.startswith('Text('):
			statement = parsing_utils.closeOpen(line.replace('Text(', 'draw.text('))
			self.UTILS['draw']['enabled'] = True

		# Pxl-On
		elif line.startswith('Pxl-On('):
			statement = parsing_utils.closeOpen(line.replace('Pxl-On(', 'draw.pxlOn('))
			self.UTILS['draw']['enabled'] = True

		# Pxl-Off
		elif line.startswith('Pxl-Off('):
			statement = parsing_utils.closeOpen(line.replace('Pxl-Off(', 'draw.pxlOff('))
			self.UTILS['draw']['enabled'] = True

		# pxl-Test
		elif line.startswith('pxl-Test('):
			statement = parsing_utils.closeOpen(line.replace('pxl-Test(', 'draw.pxlTest('))
			self.UTILS['draw']['enabled'] = True

		# Pt-On
		elif line.startswith('Pt-On('):
			statement = parsing_utils.closeOpen(line.replace('Pt-On(', 'draw.ptOn('))
			self.UTILS['draw']['enabled'] = True

		# Pt-Off
		elif line.startswith('Pt-Off('):
			statement = parsing_utils.closeOpen(line.replace('Pt-Off(', 'draw.ptOff('))
			self.UTILS['draw']['enabled'] = True

		# TextColor
		elif line.startswith('TextColor('):
			statement = parsing_utils.closeOpen(line.replace('TextColor(', 'draw.textColor('))
			self.UTILS['draw']['enabled'] = True

		# DispGraph
		elif line == 'DispGraph':
			statement = 'draw.openWindow()'
			self.UTILS['draw']['enabled'] = True

		elif line == 'ClrAllLists':
			statement = 'l1 = l2 = l3 = l4 = l5 = l6 = [None for _ in range(0, 999)]'

		# Clr single list
		elif line.startswith('ClrList '):
			statement = line[8:] + ' = [None for _ in range(0, 999)]'

		else:
			# Things that can be alone on a line
			if line.startswith("getKey") or line.startswith("abs") or line.startswith("sqrt") or line.startswith("toString(") or line.startswith('randInt(') or line.startswith('rand'):
				statement = line
			else:
				statement = "# UNKNOWN INDENTIFIER: {}".format(line)
				logger.warning("Unknown indentifier on line %s", index + 1)

		if isinstance(statement, str):
			statement = [statement]

		if "getKey" in ' '.join(statement):
			# Replace getKey with getKey() if getKey is not inside of quotes
			statement = parsing_utils.noStringReplace(r'getKey(?!\()+', "getKey()", statement)
			self.UTILS["getKey"]["enabled"] = True
		if "[theta]" in ' '.join(statement):
			# Replace [theta] with theta if [theta] is not inside of quotes
			statement = [item.replace('[theta]', "θ") for item in statement]
		if "^" in ' '.join(statement):
			# Convert every ^ not in a string to **
			statement = parsing_utils.noStringReplace(r'\^', '**', statement)
		if "–" in ' '.join(statement):
			# Remove long dash
			statement = [item.replace('–', "-") for item in statement]
		if "getTime" in ' '.join(statement):
			# Replace getTime with getTime() if getTime is not inside of quotes
			statement = parsing_utils.noStringReplace(r'getTime(?!\()+', 'getTime()', statement)
			self.UTILS["getDateTime"]["enabled"] = True
		if "getDate" in ' '.join(statement):
			# Replace getDate with getDate() if getDate is not inside of quotes
			statement = parsing_utils.noStringReplace(r'getDate(?!\()+', 'getDate()', statement)
			self.UTILS["getDateTime"]["enabled"] = True
		if "sqrt(" in ' '.join(statement):
			# Replace sqrt with math.sqrt if sqrt is not inside of quotes
			statement = parsing_utils.noStringReplace('sqrt', 'math.sqrt', statement)
			self.UTILS["math"]["enabled"] = True
		if "toString(" in ' '.join(statement):
			# Replace toString() with str() if toString() is not inside of quotes
			statement = parsing_utils.noStringReplace(r'toString\(([^\)]+)\)', r'str(\1)', statement)
		if "rand" in ' '.join(statement):
			# Replace rand with random.random() if rand is not inside of quotes
			statement = parsing_utils.noStringReplace(r'rand(?!\(|I|o)+', 'random.random()', statement)
			statement = parsing_utils.noStringReplace(r'rand\(([0-9])\)', r'[random.random() for _ in range(\1)]', statement)
			self.UTILS['random']['enabled'] = True
		if 'dayOfWk(' in ' '.join(statement):
			self.UTILS['getDateTime']['enabled'] = True
		if 'remainder(' in ' '.join(statement):
			statement = parsing_utils.noStringReplace(r'remainder\(([^\)]+)\)', lambda m: m.group(1).replace(' ', '').split(',')[0] + ' % ' + m.group(1).replace(' ', '').split(',')[1], statement)

		if 'dim(' in ' '.join(statement):
			statement = parsing_utils.noStringReplace(r'dim\(', 'len(', statement)

		if re.search(r'l[1-6]\([0-9A-Za-z]+\)', ' '.join(statement)):
			# List subscription
			try:
				statement = parsing_utils.noStringReplace(r'(l[1-6])\(([0-9A-Za-z]+)\)', lambda m: m.group(1) + '[' + str(int(m.group(2)) - 1) + ']', statement)
			except ValueError:
				statement = parsing_utils.noStringReplace(r'(l[1-6])\(([0-9A-Za-z]+)\)', lambda m: m.group(1) + '[' + m.group(2) + ']', statement)

		if 'randInt(' in ' '.join(statement):
			# Replace randInt with random.randint
			statement = parsing_utils.noStringReplace('randInt', 'random.randint', statement)

			for i in range(len(statement)):
				split_statement = parsing_utils.parenthesis_split(parsing_utils.closeOpen(statement[i]))

				for j in range(len((split_statement))):
					if 'random.randint' in split_statement[j]:
						args = re.search(r'random\.randint\((.*?)\)', split_statement[j]).group(1).replace(' ', '').split(',') # get data in between parentheses
						if len(args) >= 3:
							# Generate args[2] amount of random numbers
							split_statement[j] = re.sub(r'random\.randint\(.*?\)', '[random.randint(' + args[0] + ', ' + args[1] + ') for i in range(' + args[2] + ')]', split_statement[j])
				statement[i] = ' '.join(split_statement)

			self.UTILS['random']['enabled'] = True

		if self.multiplication:
			for statement_index, item in enumerate(statement):
				statement[statement_index] = parsing_utils.toValidEqn(item)

		if isinstance(statement, list) and len(statement) == 1:
			statement = statement[0]

		return statement

	def toPython(self):
		self.pythonCode = []

		self.pythonCode += ["def main():", "\tl1 = l2 = l3 = l4 = l5 = l6 = [None for _ in range(0, 999)] # init lists"]
		self.pythonCode += ["\tA = B = C = D = E = F = G = H = I = J = K = L = M = N = O = P = Q = R = S = T = U = V = W = X = Y = Z = θ = 0 # init variables"]

		self.indentLevel = 1
		# indentIncrease increases the indent on the next line
		self.indentIncrease = False
		# indentDecrease decreases the indent on the current line
		self.indentDecrease = False
		self.skipLine = 0

		# Iterate over TI-BASIC code and convert each line
		for index, line in enumerate(self.basic):
			statement = self.convertLine(index, line)

			if self.UTILS['draw']['enabled'] is True and self.drawLock is False:
				self.drawLock = True
				self.pythonCode.insert(1, '\tdraw.openWindow()')
				self.pythonCode.insert(1, '\tdraw = Draw()')

			if statement is None:
				continue

			# Indentation
			if self.indentDecrease is True:
				self.indentLevel -= 1
				self.indentDecrease = False

			# Append converted line to list of code
			if isinstance(statement, str):
				self.pythonCode.append("\t" * self.indentLevel + statement)
			elif isinstance(statement, list):
				for item in statement:
					self.pythonCode.append("\t" * self.indentLevel + item)

			# Indentation
			if self.indentIncrease is True:
				self.indentLevel += 1
				self.indentIncrease = False

		# Hand of end if drawing
		if self.UTILS['draw']['enabled'] is True:
			# hang on end if drawing
			self.pythonCode += [
				'\ttry:',
				'\t\twhile True:',
				'\t\t\tdraw.win.getMouse()',
				'\texcept GraphicsError:',
				'\t\tpass'
			]

		# Decorate main with with_goto if goto is used
		if self.UTILS["goto"]["enabled"] is True:
			self.pythonCode.insert(0, "@with_goto")
		if self.UTILS['fix_floating_point']['enabled'] is True:
			self.pythonCode.insert(0, '@fix_floating_point')

		# Add required utility functions
		neededImports = []
		for item in self.UTILS:
			if self.UTILS[item]["enabled"] is True:
				# Add code to new file
				self.pythonCode = self.UTILS[item]["code"] + self.pythonCode
				for importedPackage in self.UTILS[item]["imports"]:
					# Have separate list so that all of the imports are at the top
					if importedPackage not in neededImports:
						neededImports.append(importedPackage)
		self.pythonCode = neededImports + self.pythonCode

		self.pythonCode += ["if __name__ == \"__main__\":", "\tmain()"]

		return self.pythonCode
