import setuptools
import os

install_requires = [
	"basically-ti-basic>=0.1.4",
	"goto-statement @ https://github.com/TabulateJarl8/python-goto/archive/patch-2.zip#egg=goto_statement-1.2"
]

with open("README.md", "r") as fh:
	long_description = fh.read()

here = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(here, "ti842py", "__version__.py"), "r") as f:
	exec(f.read(), about)

setuptools.setup(
    name=about["__title__"],
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=about["__url__"],
	install_requires=install_requires,
	entry_points={
		'console_scripts': [
			'ti842py = ti842py.main:main'
		]
	},
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
	include_package_data=True
)