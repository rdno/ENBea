# -*- coding: utf-8 -*-
import glob
import os
import re

def compile_ui_windows():
    for filename in glob.glob1('ui', '*.ui'):
        os.system('pyuic4 -o enbea/ui_%s.py ui/%s' % \
                      (filename.split('.')[0], filename))
        use_i18n('enbea/ui_%s.py' % filename.split('.')[0])

def use_i18n(uipy):
    pyfile = open(uipy, 'r')
    content = pyfile.read()
    pyfile.close()
    content = content.replace('from PyQt4 import QtCore, QtGui\n\n', 'from PyQt4 import QtCore, QtGui\nfrom enbea.translation import i18n\n\n')
    content =  re.sub('QtGui.QApplication.translate\([\"\w\d\.]+, ([^,]+), [\"\w\d\.]+, [\"\w\d\.]+\)', 
                      lambda m:'i18n('+m.group(1)+')', content)
    pyfile = open(uipy, 'w')
    content = pyfile.write(content)
    pyfile.close()

options = {'windows':['enbea.py'],
           'options':{"py2exe": {"skip_archive": False, "includes": ["sip"],"bundle_files":3}},
           'zipfile':None}    
    