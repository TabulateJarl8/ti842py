def toNumber(string):
	try:
		return int(string)
	except ValueError:
		try:
			return float(string)
		except ValueError:
			return string
