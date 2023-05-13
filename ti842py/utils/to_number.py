def to_number(string):
	try:
		return int(string)
	except ValueError:
		try:
			return float(string)
		except ValueError:
			return string
