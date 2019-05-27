#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
'''
@package 
@brief   NUANCE languages team library bootstrap.
@date    May 2, 2012 12:42:18 PM
@author: Roman Schroeder
'''

__author__ = "Roman Schroeder"
__copyright__ = "Copyright Nuance Communications Switzerland AG, 2012"

import os
import sys
try:
    import nuanlib
except ImportError:
    def get_parent_path(path):
        return path[:path.rfind(os.sep)]
    class AddSource(Exception):
        pass
    eggfile = "nuanlib.egg"
    path = os.path.dirname(__file__)
    paths = [os.path.join(path, eggfile),
             os.path.join(path, "lib", eggfile),
             os.path.join(path, "dist", eggfile),
             os.path.join(get_parent_path(path), "lib", eggfile),
             os.path.join(get_parent_path(path), "dist", eggfile),
             os.path.join(get_parent_path(get_parent_path(path)), "lib", eggfile),
             os.path.join(get_parent_path(get_parent_path(path)), "dist", eggfile),
             ]
    try:
        for sourcepath in paths:
            if os.path.exists(sourcepath):
                sys.path.append(sourcepath)
                raise AddSource
    except AddSource:
        import nuanlib
    else:
        raise ImportError("Can not find the NUANLIB.")
