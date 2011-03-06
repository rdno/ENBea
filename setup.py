#!/usr/bin/python
# -*- coding: utf-8 -*-
import glob
import os
if os.name == 'nt':
    import py2exe

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

                      
class MultiPlatformCommand(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        if os.name == 'posix':
            self.run_posix()
        elif os.name == 'nt':
            self.run_win()
    def run_posix(self):
        pass
    def run_win(self):
        print "Your os suck!"

class Mo(MultiPlatformCommand):
    def run_posix(self):
        generate_mo()

class Pot(MultiPlatformCommand):
    def run_posix(self):
        generate_pot()

class UICompile(MultiPlatformCommand):
    def run_posix(self):
        compile_ui()
    def run_win(self):
        from setup_win import compile_ui_windows
        compile_ui_windows()

class Clean(clean):
    def run(self):
        if not os.name == 'nt':
            os.system('find . -name *.pyc | xargs rm -rvf')
            os.system('find . -name *~ | xargs rm -rvf')
            clean.run(self)

class Tags(MultiPlatformCommand):
    """Command for creating emacs TAGS file"""
    def run(self):
        os.system('etags *.py enbea/*.py')

if os.name == 'nt':
    from setup_win import options
    extra_options = options
else:
    extra_options = {}
setup(name="ENBea",
      version="0.2",
      description="An episode renamer using IMDb API",
      author=u"Rıdvan Örsvuran",
      author_email='flasherdn@gmail.com',
      license='GPL',
      packages=['enbea'],
      scripts=['enbea.py'],
      cmdclass = {'compileui':UICompile,
                  'clean':Clean,
                  'tags':Tags,
                  'pot':Pot,
                  'mo':Mo},
      **extra_options
      )
