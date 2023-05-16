from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='powercmd',
      version='0.3.6',
      description='A generic framework to build typesafe line-oriented command interpreters',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/dextero/powercmd',
      author='Marcin Radomski',
      author_email='marcin@mradomski.pl',
      license='MIT',
      packages=['powercmd'],
      zip_safe=True,
      install_requires=['prompt_toolkit >= 2.0'])
