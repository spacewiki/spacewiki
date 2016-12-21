#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='spacewiki',
      packages=find_packages(),
      install_requires=[
          'Flask>=0.11',
          'MarkupSafe',
          'peewee>=2.5.1',
          'bleach',
          'GitPython',
          'mistune',
          'hypothesis',
          'pillow',
          'slugify',
          'flask-script',
          'colorlog',
          'gevent',
          'libsass',
          'cssmin',
          'Flask-Assets',
          'flask-login',
          'PyYAML'
      ]
)
