import argparse
import basically_ti_basic as btb
import os
import tempfile
try:
	from .tiParser import BasicParser
except:
	from tiParser import BasicParser

def transpile(infile, outfile="stdout", decompileFile=True, forceDecompile=False):

	decode = os.path.splitext(infile)[1].lower() == ".8xp" and decompileFile == True

	if decode == True or forceDecompile == True:
		# Decompile 8Xp file
		try:
			temp_name = next(tempfile._get_candidate_names())
			btb.decompile_file(infile, temp_name)
			with open(temp_name, 'r') as f:
				pythonCode = BasicParser([line.strip() for line in f.readlines()]).toPython()
		finally:
			os.remove(temp_name)


	else:
		# Dont decompile

		# Read infile
		with open(infile, 'r') as f:
			file_lines = [line.strip() for line in f.readlines()]

		pythonCode = BasicParser(file_lines).toPython()

	# Write to outfile
	if outfile == "stdout":
		print("\n".join(pythonCode))
	else:
		with open(outfile, 'w') as f:
			for line in pythonCode:
				f.write(line + "\n")

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

	args = parser.parse_args()

	transpile(args.i, args.o, args.n, args.d)


if __name__ == "__main__":
	main()