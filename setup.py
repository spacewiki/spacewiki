#!/usr/bin/env python
from setuptools import setup, find_packages
from distutils.command.build import build as _build
import distutils.cmd
import subprocess
import os
import os.path

class build(_build):
    sub_commands = [('build_npm', None)] + _build.sub_commands

class NpmCommand(distutils.cmd.Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        pwd = os.path.dirname(__file__)
        jsDir = os.path.sep.join((pwd, 'spacewiki', 'static'))
        subprocess.check_call([os.environ.get('NPM', 'npm'), 'install'], cwd=jsDir)

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
          'PyYAML',
          'flask_restful'
      ],
      extras_require = extras,
      include_package_data=True,
      cmdclass={
          'build_npm': NpmCommand,
          'build': build
      }
)
