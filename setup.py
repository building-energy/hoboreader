# -*- coding: utf-8 -*-


from setuptools import setup, find_packages
from codecs import open
from os import path

setup(  
    name='hoboreader', 
    version='0.0.1',  
    description='Python package for reading Onset Hobo sensor csv files',  # Required
    url='https://github.com/stevenkfirth/hoboreader',  # Optional
    author='Steven Firth',  # Optional
    author_email='s.k.firth@lboro.ac.uk',  # Optional
    packages=find_packages() # Required
    )
