import re
import itertools
import tokenize
import io

try:
	from . import token_utils
except ImportError:
	import token_utils


def closeOpen(string):
	if string.count("\"") % 2 != 0:
		string = string + "\""

	# Split string by "
	splitString = string.split('"')
	open_paren = 0
	closed_paren = 0

	for i in range(0, len(splitString), 2): # skip all even elements since those are in between quotes
		open_paren += splitString[i].count('(')
		closed_paren += splitString[i].count(')')

	# Add needed closing parentheses
	string = string + ')' * (open_paren - closed_paren)
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
		2N  -> 2*N
		N 2 -> N* 2
		2(A+B) -> 2*(A+B)
		(A+B)2 -> (A+B)*2
		2 3 -> 2* 3
		M N -> M* N
		(A+B)C -> (A+B)*C
		A(3) -> A*(3)
		a(3) -> a(3) - will only add multiplication if the preceding token is capital, since that is a variable
	"""

	"""
	Modified from ideas
	https://github.com/aroberge/ideas/blob/master/ideas/examples/implicit_multiplication.py
	"""

	constants = ['BLUE', 'RED', 'BLACK', 'MAGENTA', 'GREEN', 'ORANGE', 'BROWN', 'NAVY', 'LTBLUE', 'YELLOW', 'WHITE', 'LTGRAY', 'MEDGRAY', 'GRAY', 'DARKGRAY']

	tokens = token_utils.tokenize(source)
	if not tokens:
		return tokens

	prev_token = tokens[0]
	new_tokens = [prev_token]

	for token in tokens[1:]:
		if token.is_not_in(constants):
			# Check if implicit multiplication should be added
			if (
				(
					(prev_token.is_number() or (prev_token.is_identifier() and prev_token.string.isupper()))
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
				# Multiple variables next to one another
				# ABC -> A*B*C
				token.string = '*'.join(token.string)
				new_tokens.append(token)
			else:
				new_tokens.append(token)
		else:
			# Token in constants, skip
			new_tokens.append(token)

		prev_token = token

	return token_utils.untokenize(new_tokens)


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

