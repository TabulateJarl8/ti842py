import os

def prgm(program_path):
	if '.' not in program_path and '~' not in program_path and program_path.isupper():
		# most likely code from a TI-BASIC program, since these are constraints for program names
		# this will be useful when implementing a shell for ti842py
		program_path = os.path.expanduser(program_path) + '.8xp'
		user_path = False
	else:
		# most likely user-supplied path; expand user
		program_path = os.path.expanduser(program_path)
		user_path = True

	if user_path:
		# directly check if the file exists after expanding user
		if os.path.isfile(program_path):
			directory_listing = [program_path]
			program_name_index = 0
		else:
			raise FileNotFoundError(f'[Errno 2] No such file or directory: \'{program_path}\'')
	else:
		# change case to lower in order to match extension
		directory_listing = os.listdir()
		try:
			# search for case insensitive filename in current directory
			program_name_index = [file.lower() for file in directory_listing].index(program_path.lower())
		except ValueError as exc:
			raise FileNotFoundError(f'[Errno 2] No such file or directory: \'{program_path}\'') from exc

	# run program
	os.system(f'ti842py "{directory_listing[program_name_index]}" --run')