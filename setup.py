#!/usr/bin/python
# -*- coding: utf-8 -*-
import glob
import os

from distutils.core import setup
from distutils.cmd import Command
from distutils.command.clean import clean

def compile_ui():
    for filename in glob.glob1('ui', '*.ui'):
        os.system('pyuic4 -o enbea/ui_%s.py ui/%s -g %s' % \
                      (filename.split('.')[0], filename,
                       'enbea'))

def generate_pot():
    infile = 'po/POTFILES.in'
    files = os.popen("find . -name '*.py'").read().strip().split("\n")
    with open(infile, 'w') as potfilesin:
        potfilesin.write('\n'.join(files))
    os.system('xgettext --keyword=i18n -f %s -o %s' % \
                  (infile, 'po/enbea.pot'))
    for item in glob.glob1("po", "*.po"):
        print "Updating .. ", item
        os.system("msgmerge --update --no-wrap --sort-by-file po/%s po/enbea.pot" % item)

def generate_mo():
    for lang in glob.glob1("po", "*.po"):
        os.system("mkdir -p locale/%s/LC_MESSAGES" % lang.split('.')[0])
        os.system("msgfmt --output-file=locale/%s/LC_MESSAGES/%s.mo po/%s" \
                      % (lang.split('.')[0], 'enbea', lang))

class Mo(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        generate_mo()


class Pot(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        generate_pot()



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
                  'tags':Tags,
                  'pot':Pot,
                  'mo':Mo}
      )
