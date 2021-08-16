import unittest
import pathlib
import subprocess

try:
	import ti842py
except ImportError as exc:
	raise ImportError('ti842py is not installed. Please install the local version by running `python3 setup.py sdist` followed by `pip3 install dist/* --force-reinstall` in the root directory of the repository') from exc

print(f'ti842py version {ti842py.__version__}')

parent_directory = pathlib.Path(__file__).parents[1].resolve()

class MainTestCase(unittest.TestCase):
	def test_traspile(self):
		ti842py.transpile(str(parent_directory / 'program.txt'), str(parent_directory / 'output.py'))

	def test_command_transpile(self):
		child = subprocess.Popen(['ti842py', str(parent_directory / 'program.txt'), '-o', str(parent_directory / 'output.py')])
		child.communicate()
		self.assertEqual(child.returncode, 0, 'Must exit with code 0')


if __name__ == '__main__':
	unittest.main()