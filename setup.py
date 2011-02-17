#!/usr/bin/python
# -*- coding: utf-8 -*-
import glob
import os

from distutils.core import setup
from distutils.cmd import Command
from distutils.command.clean import clean

def compile_ui():
    for filename in glob.glob1('ui', '*.ui'):
        os.system('pyuic4 -o enbea/ui_%s.py ui/%s' % \
                      (filename.split('.')[0], filename))

class UICompile(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        compile_ui()

class Clean(clean):
    def run(self):
        os.system('find . -name *.pyc | xargs rm -rvf')
        os.system('find . -name *~ | xargs rm -rvf')
        clean.run(self)

class Tags(Command):
    """Command for creating emacs TAGS file"""
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        os.system('etags *.py enbea/*.py')



setup(name="ENBea",
      version="0.1",
      description="An episode renamer using IMDb API",
      author=unicode("Rıdvan Örsvuran"),
      author_email='flasherdn@gmail.com',
      license='GPL',
      packages=['enbea'],
      scripts=['enbea.py'],
      cmdclass = {'compileui':UICompile,
                  'clean':Clean,
                  'tags':Tags}
      )
