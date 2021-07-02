import decimal
import inspect
import io
import tokenize


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