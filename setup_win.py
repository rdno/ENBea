# -*- coding: utf-8 -*-
import fnmatch
import glob
import os
import re

from distutils.cmd import Command

def get_content_of_file(filename):
    file_ = open(filename, 'r')
    content = file_.read()
    file_.close()
    return content

def compile_ui_windows():
    for filename in glob.glob1('ui', '*.ui'):
        os.system('pyuic4 -o enbea/ui_%s.py ui/%s' % \
                      (filename.split('.')[0], filename))
        use_i18n('enbea/ui_%s.py' % filename.split('.')[0])

def use_i18n(uipy):
    content = get_content_of_file(uipy)
    content = content.replace('from PyQt4 import QtCore, QtGui\n\n', 'from PyQt4 import QtCore, QtGui\nfrom enbea.translation import i18n\n\n')
    content =  re.sub('QtGui.QApplication.translate\([\"\w\d\.]+, ([^,]+), [\"\w\d\.]+, [\"\w\d\.]+\)', 
                      lambda m:'i18n('+m.group(1)+')', content)
    with open(uipy, 'w') as pyfile:
        pyfile.write(content)

def make_nsis_installer():
    content = get_content_of_file('win-installer-template.nsi')
    files = []
    for file_ in glob.glob('dist/*.*'):
        files.append(file_)
        print file_
    include_files_str = ''.join(map(lambda s:'File "'+s+'"\n    ',  files))
    delete_files_str = ''.join(map(lambda s:'Delete "$INSTDIR\\'+s.replace('dist\\', '')+'"\n    ',  files))
    include_files_str += 'File /r "dist\\locale"'
    delete_files_str += 'RMDir /r "$INSTDIR\\locale"'
    content = content.replace('#INCLUDE_FILES#', include_files_str)
    content = content.replace('#DELETE_FILES#', delete_files_str)
    with open('win-installer.nsi', 'w') as nsisfile:
        nsisfile.write(content)

def find_files(patterns):
    for root, dirs, files in os.walk(os.curdir):
        for basename in files:
            if not '.\\build' in root and \
               not '.\\dist'  in root:
                for pattern in patterns:
                    if fnmatch.fnmatch(basename, pattern):
                        filename = os.path.join(root, basename)
                        yield filename
class MakeInstaller(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        os.system('mkdir dist\\locale')
        os.system('xcopy /E /Y /Q locale dist\\locale')
        make_nsis_installer()
        os.system("makensis.exe /X\"SetCompressor /SOLID lzma\" win-installer.nsi")

def generate_mo_windows():
    for lang in glob.glob1("po", "*.po"):
        os.system("mkdir locale\\%s\\LC_MESSAGES" % lang.split('.')[0])
        os.system("msgfmt --output-file=locale\\%s\\LC_MESSAGES\\%s.mo po\\%s" \
                      % (lang.split('.')[0], 'enbea', lang))
def generate_pot_windows():
    infile = 'po\\POTFILES.in'
    with open(infile, 'w') as potfilesin:
        for file_ in find_files(['*.py']):
            potfilesin.write(file_+'\n')
    os.system('xgettext --keyword=i18n -f %s -o %s' % \
                  (infile, 'po/enbea.pot'))
    for item in glob.glob1("po", "*.po"):
        print "Updating .. ", item
        os.system("msgmerge --update --no-wrap --sort-by-file po/%s po/enbea.pot" % item)
options = {'windows':['enbea.py'],
           'options':{"py2exe": {"skip_archive": False, "includes": ["sip"],"bundle_files":3}},
           'zipfile':None}
cmdclass_win = {'makeinstaller':MakeInstaller}
    