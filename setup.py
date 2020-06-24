#!/usr/bin/env python

import sys
from setuptools import setup, find_packages

if sys.version_info < (3, 6):
    raise NotImplementedError("Sorry, you need at least Python 3.6 to use the redirector.")

from src.redirector import redirector

setup(name='redirector',
      version=redirector.__version__,
      description='Simple and safe redirects follower.',
      long_description=redirector.__doc__,
      long_description_content_type="text/markdown",
      author=redirector.__author__,
      author_email='sindbag+spam@gmail.com',
      py_modules=['redirector'],
      packages=find_packages('src', exclude=['tests', 'tests.*']),
      package_dir={'': 'src'},
      install_requires=open('requirements.txt').readlines(),
      license='MIT',
      platforms='any',
      classifiers=['Development Status :: 4 - Beta',
                   "Operating System :: OS Independent",
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   ],
      )