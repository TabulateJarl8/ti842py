import decimal
import copy
import operator
import math

class DimensionMismatchError(Exception):
	pass

class InvalidDimensionError(Exception):
	pass

class SingularMatrixError(Exception):
	pass

class Matrix:
	'''
	Matrix class that acts like the matrices on TI calculators
	'''
	def __init__(self, init_matrix=None):
		if init_matrix is None:
			self.matrix = [[0]]
		else:
			self.matrix = init_matrix

	def reshape(self, rows, cols):
		'''
		Reshape Matrix
		'''

		# No checks required since here aren't any rules to resizing matrices
		# in TI-BASIC for the 84

		result = [[0 for _ in range(cols)] for _ in range(rows)]

		count = 0
		for i in range(len(self.matrix)):
			for j in range(len(self.matrix[0])):
				try:
					result[count // cols][count % cols] = self.matrix[i][j]
				except IndexError:
					# Shrinking the matrix will throw an error; ignore this
					pass

				count += 1

		self.matrix = result

	def shape(self):
		'''
		returns rows, cols
		'''

		return len(self.matrix), len(self.matrix[0])

	def _operate_on_matrix_elements(self, operation, factor_a, factor_b):
		'''
		Apply an operation to each element in the matrix.
		factors can be ints, floats, or other matrices
		'''

		# Convert to decimal objects
		if isinstance(factor_a, float):
			factor_a = decimal.Decimal(str(factor_a))
		if isinstance(factor_b, float):
			factor_b = decimal.Decimal(str(factor_b))

		if isinstance(factor_a, Matrix) and isinstance(factor_b, Matrix):
			if not factor_a.shape() == factor_b.shape():
				raise DimensionMismatchError('Check size (dim) of lists or matrices')

		new_matrix = Matrix()
		if isinstance(factor_a, Matrix):
			new_matrix.reshape(*factor_a.shape())
		elif isinstance(factor_b, Matrix):
			new_matrix.reshape(*factor_b.shape())

		if isinstance(factor_a, Matrix):
			factor_a = copy.deepcopy(factor_a.matrix)
		if isinstance(factor_b, Matrix):
			factor_b = copy.deepcopy(factor_b.matrix)

		for i in range(len(new_matrix)):
			for j in range(len(new_matrix[i])):

				# Generate factors to compute
				if isinstance(factor_a, list):
					item_a = factor_a[i][j]
				else:
					item_a = factor_a

				if isinstance(factor_b, list):
					item_b = factor_b[i][j]
				else:
					item_b = factor_b

				# Convert current items to decimal objects if applicable
				if isinstance(item_a, float):
					item_a = decimal.Decimal(str(item_a))
				if isinstance(item_b, float):
					item_b = decimal.Decimal(str(item_b))


				item_computation = operation(item_a, item_b)
				if isinstance(item_computation, decimal.Decimal):
					if str(item_computation).isdigit():
						item_computation = int(item_computation)
					else:
						item_computation = float(item_computation)

				new_matrix[i][j] = item_computation

		return new_matrix

	def _generate_zero_matrix(self, size):
		'''
		Generate a matrix of shape rows, cols with all zeros, where rows and cols are both equal to size.
		The main diagonal is one.
		Used for raising a matrix to the power of zero.
		'''

		return Matrix([[1 if i == j else 0 for j in range(size)] for i in range(size)])

	def _invert_matrix(self, matrix):
		'''
		Invert a matrix object
		Mostly taken from https://stackoverflow.com/a/39881366/11591238
		'''

		def transposeMatrix(m):
			return map(list, zip(*m))

		def getMatrixMinor(m, i, j):
			return [row[:j] + row[j + 1:] for row in (m[:i] + m[i + 1:])]

		def getMatrixDeternminant(m):
			#base case for 2x2 matrix
			if len(m) == 2:
				return m[0][0] * m[1][1] - m[0][1] * m[1][0]

			determinant = 0
			for c in range(len(m)):
				determinant += ((-1) ** c) * m[0][c] * getMatrixDeternminant(getMatrixMinor(m, 0, c))
			return determinant

		def getMatrixInverse(m):
			determinant = getMatrixDeternminant(m)
			#special case for 2x2 matrix:
			if len(m) == 2:
				return [[m[1][1] / determinant, -1 * m[0][1] / determinant],
						[-1 * m[1][0] / determinant, m[0][0] / determinant]]

			#find matrix of cofactors
			cofactors = []
			for r in range(len(m)):
				cofactorRow = []
				for c in range(len(m)):
					minor = getMatrixMinor(m, r, c)
					cofactorRow.append(((-1) ** (r + c)) * getMatrixDeternminant(minor))
				cofactors.append(cofactorRow)
			cofactors = transposeMatrix(cofactors)
			for r in range(len(cofactors)):
				for c in range(len(cofactors)):
					cofactors[r][c] = cofactors[r][c] / determinant
			return cofactors

		try:
			new_matrix = getMatrixInverse(matrix.matrix)
		except ZeroDivisionError as exc:
			raise SingularMatrixError('No inverse matrix exists.') from exc

		return Matrix(new_matrix)


	def __len__(self):
		# Return rows, cols
		return self.shape()

	def __mul__(self, other):
		if isinstance(other, Matrix):
			# matrix multiplication

			# https://www.varsitytutors.com/hotmath/hotmath_help/topics/compatible-matrices.html
			if self.shape()[1] == other.shape()[0]:

				# https://stackoverflow.com/a/10508239/11591238
				zip_other_matrix = list(zip(*other.matrix))
				new_matrix = [
					[
						sum(ele_a * ele_b for ele_a, ele_b in zip(row_self, col_other))
						for col_other in zip_other_matrix
					] for row_self in self.matrix
				]

				return Matrix(new_matrix)

			else:

				raise DimensionMismatchError('Check size (dim) of lists or matrices')

		elif isinstance(other, (int, float)):
			new_matrix = self._operate_on_matrix_elements(operator.mul, self, other)
			return new_matrix

	def __imul__(self, other):
		new_matrix = self.__mul__(other)
		self.matrix = copy.deepcopy(new_matrix.matrix)
		del new_matrix

		return self

	def __rmul__(self, other):
		new_matrix = self._operate_on_matrix_elements(operator.mul, other, self)
		return new_matrix

	def __add__(self, other):
		# Plus(+) and minus(-) add or subtract the matching elements of two matrices with the same size
		# http://tibasicdev.wikidot.com/matrices
		new_matrix = self._operate_on_matrix_elements(operator.add, self, other)
		return new_matrix

	def __iadd__(self, other):
		new_matrix = self.__add__(other)
		self.matrix = copy.deepcopy(new_matrix.matrix)
		del new_matrix

		return self

	def __radd__(self, other):
		new_matrix = self._operate_on_matrix_elements(operator.add, other, self)
		return new_matrix

	def __sub__(self, other):
		new_matrix = self._operate_on_matrix_elements(operator.sub, self, other)
		return new_matrix

	def __isub__(self, other):
		new_matrix = self.__sub__(other)
		self.matrix = copy.deepcopy(new_matrix.matrix)
		del new_matrix

		return self

	def __rsub__(self, other):
		new_matrix = self._operate_on_matrix_elements(operator.sub, other, self)
		return new_matrix

	def __pow__(self, other):
		if self.shape()[0] != self.shape()[1]:
			raise InvalidDimensionError('Matrix must be square.')

		if other >= 1:
			new_matrix = Matrix(copy.deepcopy(self.matrix))
			for _ in range(other - 1):
				new_matrix = self.__mul__(new_matrix)

			return new_matrix
		elif other == 0:
			return self._generate_zero_matrix(self.shape()[0])
		elif other == -1:
			return self._invert_matrix(self)
		else:
			raise ValueError('Must not be under -1')

	def __ipow__(self, other):
		new_matrix = self.__pow__(other)
		self.matrix = copy.deepcopy(new_matrix.matrix)
		del new_matrix

		return self

	def __floor__(self):
		new_matrix = copy.deepcopy(self.matrix)
		for i in range(len(new_matrix)):
			for j in range(len(new_matrix[i])):
				new_matrix[i][j] = math.floor(new_matrix[i][j])
		return Matrix(new_matrix)

	def __abs__(self):
		new_matrix = copy.deepcopy(self.matrix)
		for i in range(len(new_matrix)):
			for j in range(len(new_matrix[i])):
				new_matrix[i][j] = abs(new_matrix[i][j])
		return Matrix(new_matrix)

	def __neg__(self):
		new_matrix = copy.deepcopy(self.matrix)
		for i in range(len(new_matrix)):
			for j in range(len(new_matrix[i])):
				new_matrix[i][j] = -new_matrix[i][j]
		return Matrix(new_matrix)

	def __eq__(self, other):
		return 1 if self.matrix == other.matrix else 0

	def __ne__(self, other):
		return not self.__eq__(other)

	def __repr__(self):
		return '\n'.join(['[' + ' '.join([str(num) for num in sublist]) + ']' for sublist in self.matrix])

	def __getitem__(self, index):
		# We do not need __setitem__ because the user should not be messing
		# with the parent lists directly. __getitem__ is enough to interface
		# with the child lists contained within self.matrix
		return self.matrix[index] # indexes start at 1 in TI-BASIC

	def __call__(self, row, col):
		# TI-BASIC matrices are accessed like [A](1, 2), so I've implemented
		# that here. Uses __getitem__
		return self.__getitem__(row)[col] # indexes start at 1 in TI-BASIC
