#!/usr/bin/env python
from setuptools import setup, find_packages

extras = {
    'test': ['nose', 'coverage', 'faker', 'hypothesis']
}

setup(name='spacewiki',
      packages=find_packages(),
      install_requires=[
          'Flask>=0.11',
          'MarkupSafe',
          'peewee>=2.5.1',
          'bleach',
          'GitPython',
          'mistune',
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
      ],
      extras_require = extras
)
