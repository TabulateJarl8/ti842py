import re
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

def closeOpen(string):
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
		elif c == "," and open == True:
			# Reached a comma with open character
			newString += closingChar
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
	
def fixEquals(string):
	# Change = to ==
	return re.sub("(?<![<>!])\=", " == ", string)


class BasicParser(object):
	def __init__(self, basic):
		if isinstance(basic, list):
			self.basic = basic
		elif isinstance(basic, str):
			self.basic = [line.strip() for line in basic.split("\n")]
		else:
			raise TypeError("basic must be list or str, not {}".format(str(type(basic))))

		# Utility Functions
		self.IMPORTS = ["import os", "import time", ""]
		self.CLEAR = ["def clear():", "\tif os.system(\"clear\") != 0:", "\t\tif os.system(\"cls\") != 0:", "\t\t\tprint(\"Clearing the screen is not supported on this device\")", ""]

	def toPython(self):
		pythonCode = []
		# Add utility functions
		pythonCode += self.IMPORTS
		pythonCode += self.CLEAR

		indentLevel = 0
		# indentIncrease increases the indent on the next line
		indentIncrease = False
		# indentDecrease decreases the indent on the current line
		indentDecrease = False
		skipLine = False
		for index, line in enumerate(self.basic):
			statement = ""
			if line.startswith("\""):
				# Comments
				statement = "# " + line.lstrip("\"")
			elif skipLine == True:
				skipLine = False
				continue
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
				statement = "if " + line.lstrip("If ")
				statement = fixEquals(statement)
				statement = statement + ":"
				indentIncrease = True
			elif line == "Then":
				continue
			# Elif
			elif line == "Else" and self.basic[index + 1].startswith("If"):
				statement = "elif " + self.basic[index + 1].lstrip("If ")
				statement = fixEquals(statement)
				statement = statement + ":"
				indentDecrease = True
				indentIncrease = True
				skipLine = True
			# Else
			elif line == "Else" and not (self.basic[index + 1].startswith("If")):
				statement = "else:"
				indentDecrease = True
				indentIncrease = True
			elif line == "ClrHome":
				statement = "clear()"
			elif line == "End":
				indentDecrease = True
			# Input
			elif line.startswith("Input"):
				statement = line.split(",")
				statement = statement[1] + " = input(" + closeOpen(statement[0][6:]) + ")"
			# For loop
			elif line.startswith("For"):
				args = line[3:].strip("()").split(",")
				statement = "for " + args[0] + " in range(" + args[1] + ", " + args[2]
				if len(args) == 4:
					statement += ", " + args[3]
				statement += "):"
				indentIncrease = True
			# While loop
			elif line.startswith("While "):
				statement = "while " + fixEquals(line[6:]) + ":"
				indentIncrease = True
			# Repeat loop (tests at bottom)
			elif line.startswith("Repeat "):
				statement = ["firstPass = True", "while firstPass == True or " + fixEquals(line[7:]) + ":", "\tfirstPass = False"]
				indentIncrease = True
			# Pause
			elif line.startswith("Pause"):
				args = line[5:].strip().split(",")
				print(args)
				if len(args) <= 1:
					statement = "input("
					if len(args) == 1:
						statement += str(args[0]) + ")"
				else:
					statement = ["print(" + str(args[0]) + ")", "time.sleep(" + args[1] + ")"]
			# Wait		
			elif line.startswith("Wait"):
				statement = "time.sleep(" + line[5:] + ")"
			# Stop
			elif line == "Stop":
				statement = "exit()"
			# DelVar
			elif line.startswith("DelVar"):
				statement = "del " + line[7:]
			# Prompt
			elif line.startswith("Prompt"):
				variable = line[7:]
				statement = variable + " = input(\"" + variable + "=?\")"
			
				

			else:
				statement = "# UNKNOWN INDENTIFIER: {}".format(line)
				logger.warning("Unknown indentifier on line %s", index)

			if indentDecrease == True:
				indentLevel -= 1
				indentDecrease = False

			if isinstance(statement, str):
				pythonCode.append("\t"*indentLevel + statement)
			elif isinstance(statement, list):
				for item in statement:
					pythonCode.append("\t"*indentLevel + item)

			if indentIncrease == True:
				indentLevel += 1
				indentIncrease = False

		return pythonCode