from setuptools import setup, find_packages

setup(
    name='electrolab',
    version='0.0.1',
    author='Oliver Rodriguez',
    author_email='oliverrz@illinois.edu',
    packages=find_packages('src'),
    package_dir={'':'src'},
    url='https://github.com/jrlLAB/ElectroLab',
    keywords='Electrochemistry',
    install_requires=[
    'numpy',
	'scipy',
	'matplotlib',
	'softpotato',
    ],
)
