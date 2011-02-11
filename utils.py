# -*- coding: utf-8 -*-
import re

def camelCase(name):
    s1 = name.lower()
    return re.sub('(^| |\.)([a-z])', upperTheGroup, s1)

def upperTheGroup(match):
    if match:
        return match.group(0).upper()
