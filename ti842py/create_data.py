def create_data():
	fuzzy = locals()
	with open('test', 'wb') as f:
		pickle.dump(fuzzy, f)

	with open('test', 'rb') as f:
		test = pickle.load(f)
		locals().update(test)
	print(locals())

create_data()