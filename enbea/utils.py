# -*- coding: utf-8 -*-
import fnmatch
import re
import os

from enbea import consts


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
def get_video_file_filter():
    """returns video file filter for QFileDialog"""
    filter_ = 'Video Files ('
    for ext in consts.VIDEO_EXTS:
        filter_ += ' *.'+ext
    filter_+= ")"
    print filter_
    return filter_

def get_videos(directory):
    """get files recursively"""
    for root, dirs, files in os.walk(directory):
        for basename in files:
            for ext in consts.VIDEO_EXTS:
                if fnmatch.fnmatch(basename, '*.'+ext):
                    filename = os.path.join(root, basename)
                    yield filename
