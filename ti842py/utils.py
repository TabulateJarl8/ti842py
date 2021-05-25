import token_utils
import re
import itertools

import tokenize
from io import StringIO

def closeOpen(string):
	if string.count("\"") % 2 != 0:
		string = string + "\""

	# Split string by "
	splitString = string.split('"')
	open = 0
	closed = 0

	for i in range(0, len(splitString), 2): # skip all even elements since those are in between quotes
		open += splitString[i].count('(')
		closed += splitString[i].count(')')

	# Add needed closing parentheses
	string = string + ')' * (open - closed)
	return string


def fixEquals(string):
	# Change = to == if not between quotes
	return re.sub(r'(?!\B"[^"]*)(?<![<>!])\=(?!\()+(?![^"]*"\B)', " == ", string)


def noStringReplace(regexp, newSubstr, statementList):
	# Replace everything in statementList that matches regexp with newSubstr, as long as its not in a string
	# Split by "
	statementList = [item.split('"') for item in statementList]

	# Iterate through expression list
	for i in range(len(statementList)):
		# Skip all even elements since those are in between quotes
		for j in range(0, len(statementList[i]), 2):
			statementList[i][j] = re.sub(regexp, newSubstr, statementList[i][j])

		# Restore list element
		statementList[i] = '"'.join(statementList[i])

	return statementList


def parenthesis_split(sentence, separator=" ", lparen="(", rparen=")"):
	nb_brackets = 0
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
	if nb_brackets > 0:
		raise Exception("Syntax error")

	return([sentence[i:j].strip(separator) for i, j in zip(l, l[1:])])


def menu(title, args):
	choices = []
	for i in range(0, len(args), 2):
		choices.append((str((i // 2) + 1) + ".", str(args[i])))

	# Convert args to dict
	args = {str((i // 2) + 1) + ".": args[i + 1] for i in range(0, len(args), 2)}

	ifstmt = ["d = dialog.Dialog()", "menu = d.menu(\"" + title + "\", choices=" + str(choices) + ")"]
	for key in args:
		ifstmt.extend(["if menu[1] == \"" + str(key) + "\":", "\tclear()", "\tgoto .lbl" + str(args[key])])

	return ifstmt


def toValidEqn(source):
	"""This adds a multiplication symbol where it would be understood as
	being implicit by the normal way algebraic equations are written but would
	be a SyntaxError in Python. Thus we have::
		2n  -> 2*n
		n 2 -> n* 2
		2(a+b) -> 2*(a+b)
		(a+b)2 -> (a+b)*2
		2 3 -> 2* 3
		m n -> m* n
		(a+b)c -> (a+b)*c
	The obvious one (in algebra) being left out is something like ``n(...)``
	which is a function call - and thus valid Python syntax.
	"""

	"""
	MIT License

	Copyright (c) 2020 André Roberge

	[untokenize function modified from https://github.com/myint/untokenize
	Copyright (C) 2013-2018 Steven Myint - MIT Licence]

	Permission is hereby granted, free of charge, to any person obtaining a copy
	of this software and associated documentation files (the "Software"), to deal
	in the Software without restriction, including without limitation the rights
	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
	copies of the Software, and to permit persons to whom the Software is
	furnished to do so, subject to the following conditions:

	The above copyright notice and this permission notice shall be included in all
	copies or substantial portions of the Software.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
	SOFTWARE.
	"""

	constants = ['BLUE', 'RED', 'BLACK', 'MAGENTA', 'GREEN', 'ORANGE', 'BROWN', 'NAVY', 'LTBLUE', 'YELLOW', 'WHITE', 'LTGRAY', 'MEDGRAY', 'GRAY', 'DARKGRAY']

	tokens = token_utils.tokenize(source)
	if not tokens:
		return tokens

	prev_token = tokens[0]
	new_tokens = [prev_token]

	for token in tokens[1:]:
		if token.is_not_in(constants):
			# The code has been written in a way to demonstrate that this type of
			# transformation could be done as the source is tokenized by Python.
			if (
				(
					prev_token.is_number()
					and ((token.is_identifier() and token.string.isupper()) or token.is_number() or token == "(")
				)
				or (
					(prev_token.is_identifier() and prev_token.string.isupper())
					and ((token.is_identifier() and token.string.isupper()) or token.is_number())
				)
				or (prev_token == ")" and ((token.is_identifier() and token.string.isupper()) or token.is_number()))
			):
				new_tokens.append("*")

			if token.is_identifier() and token.string.isupper() and len(token.string) > 1:
				token.string = '*'.join(token.string)
				new_tokens.append(token)
			else:
				new_tokens.append(token)
		else:
			# Token in constants, skip
			new_tokens.append(token)

		prev_token = token

	return token_utils.untokenize(new_tokens)