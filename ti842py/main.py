import argparse
import basically_ti_basic as btb
import os
import tempfile
import sys
import subprocess

try:
	from .tiParser import TIBasicParser
except:
	from tiParser import TIBasicParser

def transpile(infile, outfile="stdout", decompileFile=True, forceDecompile=False, run=False):

	decode = os.path.splitext(infile)[1].lower() == ".8xp" and decompileFile == True

	if decode == True or forceDecompile == True:
		# Decompile 8Xp file
		try:
			temp_name = next(tempfile._get_candidate_names())
			while os.path.exists(temp_name):
				temp_name = next(tempfile._get_candidate_names())
			btb.decompile_file(infile, temp_name)
			with open(temp_name, 'r') as f:
				pythonCode = TIBasicParser([line.strip() for line in f.readlines()]).toPython()
		finally:
			os.remove(temp_name)


	else:
		# Dont decompile

		# Read infile
		with open(infile, 'r') as f:
			file_lines = [line.strip() for line in f.readlines()]

		pythonCode = TIBasicParser(file_lines).toPython()

	# Write to outfile
	if outfile == "stdout":
		if run == False:
			print("\n".join(pythonCode))
		else:
			with tempfile.NamedTemporaryFile() as f:
				for line in pythonCode:
					f.write(line.encode() + b"\n")
				f.seek(0)
				proc = subprocess.Popen([sys.executable, f.name])
				try:
					proc.wait()
				except:
					proc.terminate()
	else:
		with open(outfile, 'w') as f:
			for line in pythonCode:
				f.write(line + "\n")
		if run == True:
			os.system(sys.executable + " " + outfile)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'-o',
		required=False,
		default='stdout',
		help="Optional output file to write to. Defaults to standard out."
		)
	parser.add_argument(
		'-i',
		required=True,
		help="Input file."
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
		'-r',
		'--run',
		action="store_true",
		help="Runs the program after it\'s done transpiling. Will not print to stdout",
		dest='run'
	)

	args = parser.parse_args()

	transpile(args.i, args.o, args.n, args.d, args.run)


if __name__ == "__main__":
	main()