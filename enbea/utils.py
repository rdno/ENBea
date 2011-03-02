# -*- coding: utf-8 -*-
import fnmatch
import glob
import re
import os

from enbea import consts
from enbea.translation import i18n

def camel_case(name):
    s1 = name.lower()
    return re.sub('(^| |\.)([a-z])', upper_the_group, s1)

def upper_the_group(match):
    if match:
        return match.group(0).upper()

def rename_file(dirname, oldname, newname, test=False):
    foldname = os.path.join(dirname, oldname)
    fnewname = os.path.join(dirname, newname)
    if test:
        return (foldname, fnewname)
    else:
        try:
            os.rename(foldname, fnewname)
            rename_subtitles(dirname, oldname, newname)
            return True
        except:
            return False
def rename_subtitles(dirname, oldname, newname):
    fx = fix_square_bracket_issue
    oldbasename = os.path.splitext(oldname)[0]
    newbasename = os.path.splitext(newname)[0]
    foldbasename =  os.path.join(dirname, oldbasename)
    subtitles = []
    for ext in consts.SUBTITLE_EXTS:
        subtitles.extend(glob.glob(fx(foldbasename)+"*"+ext))
    for subtitle in subtitles:
        os.rename(subtitle, subtitle.replace(oldbasename, newbasename))

def fix_square_bracket_issue(name):
    """fix [] issue"""
    return re.sub("\[(.*)\]",
                  lambda x:"[[]"+x.group(1)+"]",
                  name)


def get_video_file_filter():
    """returns video file filter for QFileDialog"""
    filter_ = i18n("Video Files")+' ('
    for ext in consts.VIDEO_EXTS:
        filter_ += ' *.'+ext
    filter_+= ")"
    return filter_

def get_videos(directory):
    """get files recursively"""
    for root, dirs, files in os.walk(directory):
        for basename in files:
            for ext in consts.VIDEO_EXTS:
                if fnmatch.fnmatch(basename, '*.'+ext):
                    filename = os.path.join(root, basename)
                    yield filename

def is_a_video_file(name):
    ext = os.path.splitext(name)[1]
    for video_ext in consts.VIDEO_EXTS:
        if ext == "." + video_ext:
            return True
    return False
