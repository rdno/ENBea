# -*- coding: utf-8 -*-
import re
import os

def camelCase(name):
    s1 = name.lower()
    return re.sub('(^| |\.)([a-z])', upperTheGroup, s1)

def upperTheGroup(match):
    if match:
        return match.group(0).upper()

def renameFile(dirname, oldname, newname, test=False):
    oldname = os.path.join(dirname, oldname)
    newname = os.path.join(dirname, newname)
    if test:
        return (oldname, newname)
    else:
        try:
            os.rename(oldname, newname)
            return True
        except:
            return False
