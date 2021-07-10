def output(y, x, text):
	print("\033[" + str(y) + ";" + str(x) + "H" + text)