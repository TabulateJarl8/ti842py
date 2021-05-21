import sys


def output(y, x, text):
	sys.stdout.write("\x1b7\x1b[%d;%df%s\n\x1b8" % (y, x, text))
	sys.stdout.flush()
