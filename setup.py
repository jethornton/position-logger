import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="position_logger",
	version="0.0.1",
	author="John Thornton",
	author_email="bjt128@gmail.com",
	description="LinuxCNC Position Logger",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/jethornton/position-logger",
	packages=setuptools.find_packages(),
	install_requires=['python-pyqt'],
	classifiers=[
		"Development Status :: 3 - Alpha",
		"Programming Language :: Python :: 2.7",
		"License :: OSI Approved :: MIT License",
		"Operating System :: POSIX :: Linux",
	],
)
