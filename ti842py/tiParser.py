import re
import logging
import os
import shutil

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

def closeOpen(string):
	# TODO: Fix overwriting on strings
	# `Output(3,1,"Masses, heavy to light, in kilograms.Assumes no friction and vi 0"` becomes `output(1, 3, "n kilograms.Assumes no friction and vi 0"")`
	newString = ""
	# Function for closing open quotation marks/parenthesis
	open = False
	closingChar = ""
	for i, c in enumerate(string):
		if i + 1 == len(string) and c != closingChar:
			# Last character and current character does not close
			if open == True:
				# Append open character to string
				c += closingChar
		# elif c == "," and open == True:
			# Reached a comma with open character
			# newString += closingChar
		elif open == True and c == closingChar:
			# Closing character reached
			open = False
			closingChar = ""
		elif open == False and c == "\"":
			# Opening quote
			open = True
			closingChar = "\""
		elif open == False and c == "(":
			# Opening parenthesis
			open = True
			closingChar = ")"
		newString += c
	return newString

def menu(title, args):
	choices = []
	for i in range(0, len(args), 2):
		choices.append((str((i // 2) + 1) + ".", str(args[i])))

	# Convert args to dict
	args = {str((i // 2) + 1) + ".": args[i + 1] for i in range(0, len(args), 2)}

	ifstmt = ["d = dialog.Dialog()", "menu = d.menu(\"" + title + "\", choices=" + str(choices) + ")"]
	for key in args:
		ifstmt.extend(["if menu[1] == \"" + str(key) + "\":", "\tgoto .lbl" + str(args[key])])

	return ifstmt

def fixEquals(string):
	# Change = to == if not between quotes
	return re.sub(r'(?!\B"[^"]*)(?<![<>!])\=(?!\()+(?![^"]*"\B)', " == ", string)

def parenthesis_split(sentence,separator=" ",lparen="(",rparen=")"):
	nb_brackets=0
	sentence = sentence.strip(separator) # get rid of leading/trailing seps

	l = [0]
	for i, c in enumerate(sentence):
		if c == lparen:
			nb_brackets += 1
		elif c == rparen:
			nb_brackets -= 1
		elif c == separator and nb_brackets == 0:
			l.append(i)
		# handle malformed string
		if nb_brackets < 0:
			raise Exception("Syntax error")

	l.append(len(sentence))
	# handle missing closing parentheses
	if nb_brackets>0:
		raise Exception("Syntax error")

	return([sentence[i:j].strip(separator) for i,j in zip(l,l[1:])])


class TIBasicParser(object):
	def __init__(self, basic):
		if isinstance(basic, list):
			self.basic = basic
		elif isinstance(basic, str):
			self.basic = [line.strip() for line in basic.split("\n")]
		else:
			raise TypeError("basic must be list or str, not {}".format(str(type(basic))))

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

	def convertLine(self, index, line):
		statement = ""
		# TODO: Make rules for :, dont fully understand it yet
		if line.startswith("\""):
			# Comments
			statement = "# " + line.lstrip("\"")
		elif self.skipLine > 0:
			self.skipLine -= 1
			return None
		elif line == "":
			# Blank
			statement = ""
		# Disp
		elif line.startswith("Disp "):
			statement = re.search("Disp (.*[^)])", line).groups(1)[0]
			statement = "print(" + closeOpen(statement) + ", sep=\"\")"
		# Variables
		elif "->" in line or "→" in line:
			statement = re.split("->|→", line)
			statement.reverse()
			statement = " = ".join(statement)
		# If
		elif line.startswith("If "):
			try:
				if self.basic[index + 1] == "Then":
					# If/Then statement
					statement = "if " + line.lstrip("If ")
					statement = fixEquals(statement)
					statement = statement + ":"
					self.indentIncrease = True
				elif re.search(r"If.*[^\"]:", line) != None:
					# If statement on 1 line
					statement = ["if " + fixEquals(line.lstrip("If ").split(":", 1)[0]) + ":", "\t" + self.convertLine(index + 1, line.lstrip("If ").split(":", 1)[1])]
				else:
					# If statement on 2 lines; no Then
					statement = ["if " + fixEquals(line.lstrip("If ")) + ":", '\t' + self.convertLine(index + 1, self.basic[index + 1])]
			except IndexError:
				# Last line in file, test for 1 line If statement
				if re.search(r"If.*[^\"]:", line) != None:
					statement = ["if " + fixEquals(line.lstrip("If ").split(":", 1)[0]) + ":", "\t" + self.convertLine(index + 1, line.lstrip("If ").split(":", 1)[1])]
		elif line == "Then":
			return None
		# Elif
		elif line == "Else" and self.basic[index + 1].startswith("If"):
			statement = "elif " + self.basic[index + 1].lstrip("If ")
			statement = fixEquals(statement)
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
					statement = statement[1] + " = [toNumber(number) for number in input(" + closeOpen(statement[0][6:]) + ")]"
				else:
					statement = statement[1] + " = toNumber(input(" + closeOpen(statement[0][6:]) + "))"
			else:
				if statement[0].strip() != "Input":
					# No input text
					statement = statement[0][6:] + " = toNumber(input(\"?\"))"
				else:
					statement = "input()"
			self.UTILS["toNumber"]["enabled"] = True
		# For loop
		elif line.startswith("For"):
			args = line[3:].strip("()").split(",")
			statement = "for " + args[0] + " in range(" + args[1] + ", " + args[2]
			if len(args) == 4:
				statement += ", " + args[3]
			statement += "):"
			self.indentIncrease = True
		# While loop
		elif line.startswith("While "):
			statement = "while " + fixEquals(line[6:]) + ":"
			self.indentIncrease = True
		# Repeat loop (tests at bottom)
		elif line.startswith("Repeat "):
			statement = ["firstPass = True", "while firstPass == True or " + fixEquals(line[7:]) + ":", "\tfirstPass = False"]
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
			self.UTILS["goto"]["enabled"] = True
		# Output
		elif line.startswith("Output("):
			statement = line[7:]
			statement = statement.split(",")
			if statement[-1].count("\"") > 1:
				statement[-1] = "\"" + re.findall('"([^"]*)"', statement[-1])[0] + "\""
			elif statement[-1].count("\"") == 1:
				statement[-1] = "\"" + statement[-1].strip(" ")[1:] + "\""
			statement[-1] = statement[-1].strip(" ")
			statement = "output(" + statement[1].strip(" ") + ", " + statement[0].strip(" ") + ", " + statement[-1] + ")"
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
			if shutil.which("dialog") == None:
				logger.warning("dialog executable not found. Please install dialog to use menus")
			tiMenu = line[4:].strip("()").split(",")
			title = tiMenu.pop(0).strip(" \"")
			options = []
			for i in range(0, len(tiMenu), 2):
				options.extend([tiMenu[i].strip(" \""), tiMenu[i + 1].strip(" \"")])
			statement = menu(title, options)
			self.UTILS["menu"]["enabled"] = True
		else:
			# Things that can be alone on a line
			if line.startswith("getKey") or line.startswith("abs") or line.startswith("sqrt") or line.startswith("toString(") or line.startswith('randInt('):
				statement = line
			else:
				statement = "# UNKNOWN INDENTIFIER: {}".format(line)
				logger.warning("Unknown indentifier on line %s", index)

		# Fix things contained within statement

		if "getKey" in statement:
			# Replace getKey with getKey() if getKey is not inside of quotes
			statement = re.sub(r'(?!\B"[^"]*)getKey(?!\()+(?![^"]*"\B)', "getKey()", statement)
			self.UTILS["getKey"]["enabled"] = True
		if "[theta]" in statement:
			# Replace [theta] with theta if [theta] is not inside of quotes
			statement = re.sub(r'(?!\B"[^"]*)\[theta\](?![^"]*"\B)', "theta", statement)
		if "^" in statement:
			# Convert every ^ not in a string to **
			statement = re.sub(r'(?!\B"[^"]*)\^(?![^"]*"\B)', "**", statement)
		if "–" in statement:
			# Remove long dash if not in string
			statement = re.sub(r'(?!\B"[^"]*)–(?![^"]*"\B)', "-", statement)
		if "getTime" in statement:
			# Replace getTime with getTime() if getTime is not inside of quotes
			statement = re.sub(r'(?!\B"[^"]*)getTime(?!\()+(?![^"]*"\B)', "getTime()", statement)
			self.UTILS["getDateTime"]["enabled"] = True
		if "getDate" in statement:
			# Replace getDate with getDate() if getDate is not inside of quotes
			statement = re.sub(r'(?!\B"[^"]*)getDate(?!\()+(?![^"]*"\B)', "getDate()", statement)
			self.UTILS["getDateTime"]["enabled"] = True
		if "sqrt(" in statement:
			# Replace sqrt with math.sqrt if sqrt is not inside of quotes
			statement = re.sub(r'(?!\B"[^"]*)sqrt(?![^"]*"\B)', "math.sqrt", statement)
			self.UTILS["math"]["enabled"] = True
		if "toString(" in statement:
			# Replace toString() with str() if toString() is not inside of quotes
			statement = re.sub(r'toString\(([^\)]+)\)', r'str(\1)', statement)
		if 'randInt(' in statement:
			# Replace randInt with random.randint
			statement = re.sub('randInt', 'random.randint', statement)

			split_statement = parenthesis_split(closeOpen(statement))

			for i in range(len((split_statement))):
				if 'random.randint' in split_statement[i]:
					args = re.search(r'random\.randint\((.*?)\)', split_statement[i]).group(1).replace(' ', '').split(',') # get data in between parentheses
					if len(args) >= 3:
						# Generate args[2] amount of random numbers
						split_statement[i] = re.sub(r'random\.randint\(.*?\)', '[random.randint(' + args[0] + ', ' + args[1] + ') for i in range(' + args[2] + ')]', split_statement[i])

			statement = ' '.join(split_statement)

			self.UTILS['random']['enabled'] = True
		return statement

	def toPython(self):
		self.pythonCode = []

		self.pythonCode += ["def main():"]

		self.indentLevel = 1
		# indentIncrease increases the indent on the next line
		self.indentIncrease = False
		# indentDecrease decreases the indent on the current line
		self.indentDecrease = False
		self.skipLine = 0

		# Iterate over TI-BASIC code and convert each line
		for index, line in enumerate(self.basic):
			statement = self.convertLine(index, line)

			if statement == None:
				continue

			# Indentation
			if self.indentDecrease == True:
				self.indentLevel -= 1
				self.indentDecrease = False

			# Append converted line to list of code
			if isinstance(statement, str):
				self.pythonCode.append("\t"*self.indentLevel + statement)
			elif isinstance(statement, list):
				for item in statement:
					self.pythonCode.append("\t"*self.indentLevel + item)

			# Indentation
			if self.indentIncrease == True:
				self.indentLevel += 1
				self.indentIncrease = False

		# Decorate main with with_goto if goto is used
		if self.UTILS["goto"]["enabled"] == True:
			self.pythonCode.insert(0, "@with_goto")

		# Add required utility functions
		neededImports = []
		for item in self.UTILS:
			if self.UTILS[item]["enabled"] == True:
				# Add code to new file
				self.pythonCode = self.UTILS[item]["code"] + self.pythonCode
				for importedPackage in self.UTILS[item]["imports"]:
					# Have separate list so that all of the imports are at the top
					if not importedPackage in neededImports:
						neededImports.append(importedPackage)
		self.pythonCode = neededImports + self.pythonCode

		self.pythonCode += ["if __name__ == \"__main__\":", "\tmain()"]

		return self.pythonCode
