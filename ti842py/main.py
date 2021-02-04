import argparse
try:
	from .tiParser import BasicParser
except:
	from tiParser import BasicParser

def transpile(infile, outfile="stdout"):

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

	args = parser.parse_args()

	transpile(args.i, args.o)


if __name__ == "__main__":
	main()