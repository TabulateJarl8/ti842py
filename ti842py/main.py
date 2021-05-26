import argparse
import basically_ti_basic as btb
import os
import tempfile
import sys
import subprocess

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


def transpile(infile, outfile="stdout", decompileFile=True, forceDecompile=False, multiplication=True, run=False):

	decode = not isUTF8(infile) and decompileFile is True

	if decode is True or forceDecompile is True:
		# Decompile 8Xp file
		with tempfile.NamedTemporaryFile() as f:
			btb.decompile_file(infile, f.name)
			with open(f.name, 'r') as fp:
				pythonCode = TIBasicParser([line.strip() for line in fp.readlines()], multiplication).toPython()

	else:
		# Dont decompile

		# Read infile
		with open(infile, 'r') as f:
			file_lines = [line.strip() for line in f.readlines()]

		pythonCode = TIBasicParser(file_lines, multiplication).toPython()

	# Write to outfile
	if outfile == "stdout":
		if run is False:
			print("\n".join(pythonCode))
		else:
			with tempfile.NamedTemporaryFile() as f:
				for line in pythonCode:
					f.write(line.encode() + b"\n")
				f.seek(0)
				proc = subprocess.Popen([sys.executable, f.name])
				try:
					proc.wait()
				except Exception:
					proc.terminate()
	else:
		with open(outfile, 'w') as f:
			for line in pythonCode:
				f.write(line + "\n")
		if run is True:
			os.system(sys.executable + " " + outfile)


def main():
	parser = argparse.ArgumentParser(description='TI-BASIC to Python 3 Transpiler')
	parser.add_argument(
		'infile',
		metavar='infile',
		nargs=1,
		help="Input file."
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
	transpile(args.infile[0], args.outfile, args.n, args.d, args.multiplication, args.run)


if __name__ == "__main__":
	main()
