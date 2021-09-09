import pickle
import os
import types

def load_persistant_data():
	if not os.path.isfile(os.path.expanduser('~/.ti842py-persistant')):
		return {}

	with open(os.path.expanduser('~/.ti842py-persistant'), 'rb') as f:
		try:
			return pickle.load(f)
		except Exception:
			print(f'Warning: could not read persistant data file at {os.path.expanduser("~/.ti842py-persistant")}')
			return {}

def save_persistant_data(locals_dict):
	for key, value in list(locals_dict.items()):
		if isinstance(value, types.ModuleType):
			locals_dict.pop(key, None)

	print(locals())
	locals_dict.pop('get_key', None)
	locals_dict.pop('listener', None)
	locals_dict.pop('draw', None)

	with open(os.path.expanduser('~/.ti842py-persistant'), 'wb') as f:
		pickle.dump(locals_dict, f)
