import pickle
import re
import os

class DataLoader:
	def __init__(self):
		self.storage_location = os.path.expanduser('~/.ti842py-persistant')

		self.load_data()

	def _load_from_all_objects(self):
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

	def __repr__(self):
		return str(self.all_objects)

# A = 'no'
# thing = DataLoader().load_locals(locals().copy())
# print(thing)
# thing.write_data()
thing = DataLoader().load_data()
thing.update_locals(locals())
print(locals())
print(A)