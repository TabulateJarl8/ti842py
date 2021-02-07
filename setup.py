import setuptools
import os

install_requires = [
	"basically-ti-basic>=0.1.4",
	"keyboard>=0.13.5",
	"pythondialog>=3.5.1"
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
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
	include_package_data=True
)
