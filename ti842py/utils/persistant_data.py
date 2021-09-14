import pickle
import re
import os
import traceback
import sys

class DataLoader:
	def __init__(self):
		self.storage_location = os.path.expanduser('~/.ti842py-persistant')

		self.load_data()

	def _load_from_all_objects(self):
		if 'variables' not in self.all_objects:
			self.all_objects['variables'] = {}
		if 'matrices' not in self.all_objects:
			self.all_objects['matrices'] = {}
		if 'lists' not in self.all_objects:
			self.all_objects['lists'] = {}

		self.variables = self.all_objects['variables']
		self.matrices = self.all_objects['matrices']
		self.lists = self.all_objects['lists']

	def load_locals(self, locals_object):
		'''Iterate through locals and sort them into the correct dictionaries'''
		for name in locals_object:
			if re.match(r'^[A-Zθ]{1}$', name):
				self.variables[name] = locals_object[name]
			elif re.match(r'^matrix_[A-J]$', name):
				self.matrices[name] = locals_object[name]
			elif re.match(r'^l[1-6]$', name):
				self.lists[name] = locals_object[name]
		return self

	def write_data(self):
		'''Write loaded data into persistant file'''
		with open(self.storage_location, 'wb') as f:
			pickle.dump(self.all_objects, f)

	def load_data(self):
		'''Load persistant data from persistant file.'''
		self.all_objects = {}

		if os.path.isfile(self.storage_location):
			with open(self.storage_location, 'rb') as f:
				self.all_objects = pickle.load(f)

		self._load_from_all_objects()

		return self

	def update_locals(self, locals_object):
		'''Inject loaded data into locals'''
		for item in self.all_objects:
			for key, value in self.all_objects[item].items():
				locals_object[key] = value

	def exception_hook(self, exc_type, value, tb):
		traceback.print_exception(exc_type, value, tb)

		# iterate to last frame in traceback
		while tb.tb_next:
			tb = tb.tb_next

		self.load_locals(tb.tb_frame.f_locals)
		self.write_data()

	def __str__(self):
		return repr(self.all_objects)

persistant_data_loader = DataLoader()
sys.excepthook = persistant_data_loader.exception_hook
# thing = DataLoader().load_locals(locals().copy())
# print(thing)
# thing.write_data()

# thing = DataLoader().load_data()
# thing.update_locals(locals())
# print(locals())
# print(A)