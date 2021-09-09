import argparse
import basically_ti_basic as btb
import os
import tempfile
import sys
import subprocess
import io
import pty

try:
	from .tiParser import TIBasicParser
	from .__version__ import __version__
except ImportError:
	from tiParser import TIBasicParser
	from __version__ import __version__


def isUTF8(file):
	with open(file, 'rb') as f:
		data = f.read()
	try:
		decoded = data.decode('UTF-8')
	except UnicodeDecodeError:
		return False
	else:
		for ch in decoded:
			if 0xD800 <= ord(ch) <= 0xDFFF:
				return False
		return True


def transpile(infile, outfile="stdout", decompileFile=True, forceDecompile=False, multiplication=True, floating_point=True, turbo_draw=False, run=False):

	# detect stdin
	if hasattr(infile, 'name'):
		if not os.path.exists(infile.name):
			# Don't auto close since we are shadowing infile
			temp_stdin = tempfile.NamedTemporaryFile()
			temp_stdin.write(infile.buffer.read())
			temp_stdin.seek(0)
			infile = temp_stdin.name
		else:
			infile = infile.name

	decode = not isUTF8(infile) and decompileFile is True

	if decode is True or forceDecompile is True:
		# Decompile 8Xp file
		with tempfile.NamedTemporaryFile() as f:
			btb.decompile_file(infile, f.name)
			with open(f.name, 'r') as fp:
				pythonCode = TIBasicParser([line.strip() for line in fp.readlines()], multiplication, floating_point, turbo_draw).toPython()

	else:
		# Dont decompile

		# Read infile
		with open(infile, 'r') as f:
			file_lines = [line.strip() for line in f.readlines()]

		pythonCode = TIBasicParser(file_lines, multiplication, floating_point, turbo_draw).toPython()

	# Close temp_stdin if used
	if 'temp_stdin' in vars() or 'temp_stdin' in globals():
		temp_stdin.close()

	# Write to outfile
	if outfile == "stdout":
		if run is False:
			print("\n".join(pythonCode))
		else:
			with tempfile.NamedTemporaryFile() as f:
				for line in pythonCode:
					f.write(line.encode() + b"\n")
				f.seek(0)

				# test if something was piped to stdin
				if 'temp_stdin' in vars() or 'temp_stdin' in globals():
					# Create new tty to handle ioctl errors in termios
					master_fd, slave_fd = pty.openpty()
					proc = subprocess.Popen([sys.executable, f.name], stdin=slave_fd)
				else:
					# Nothing was piped to stdin
					proc = subprocess.Popen([sys.executable, f.name])

				try:
					proc.wait()
				except (Exception, KeyboardInterrupt):
					proc.terminate()
	else:
		with open(outfile, 'w') as f:
			for line in pythonCode:
				f.write(line + "\n")
		if run is True:
			os.system(sys.executable + " " + outfile)


def main():
	parser = argparse.ArgumentParser(description='TI-BASIC to Python 3 Transpiler')
	infile_argument = parser.add_argument(
		'infile',
		metavar='infile',
		nargs='?',
		type=argparse.FileType('r'),
		default=(None if sys.stdin.isatty() else sys.stdin),
		help="Input file (filename or stdin)."
	)
	parser.add_argument(
		'-o',
		'--out',
		required=False,
		default='stdout',
		dest='outfile',
		help="Optional output file to write to. Defaults to standard out."
	)
	parser.add_argument(
		'-n',
		'--force-normal',
		action='store_false',
		help="Forces the program to not attempt and decompile the input file. Useful for false positives",
		dest="n"
	)
	parser.add_argument(
		'-d',
		'--force-decompile',
		action="store_true",
		help="Forces the program to attempt to decompile the input file",
		dest="d"
	)

	parser.add_argument(
		'--no-fix-multiplication',
		action='store_false',
		help='Do not attempt to fix implicit multiplication. For example, AB -> A*B and A(1) -> A*(1)',
		dest='multiplication'
	)

	parser.add_argument(
		'--no-fix-floating-point',
		action='store_false',
		help='Do not attempt to fix floating point arithmetic errors. For example, 1.1 * 3 would normally say 3.3000000000000003 instead of 3.3',
		dest='floating_point'
	)

	parser.add_argument(
		'--turbo-draw',
		action='store_true',
		help='Remove the 0.1 second delay between drawing actions'
	)

	parser.add_argument(
		'-r',
		'--run',
		action="store_true",
		help="Runs the program after it\'s done transpiling. Will not print to stdout",
		dest='run'
	)

	parser.add_argument(
		'-V',
		'--version',
		action='version',
		version='ti842py {version}'.format(version=__version__)
	)

	args = parser.parse_args()

	if hasattr(args.infile, '__getitem__'):
		infile = args.infile[0]
	else:
		infile = args.infile

	if infile is None:
		raise argparse.ArgumentError(infile_argument, 'the infile argument is required')

	transpile(infile, args.outfile, args.n, args.d, args.multiplication, args.floating_point, args.turbo_draw, args.run)


if __name__ == "__main__":
	main()
