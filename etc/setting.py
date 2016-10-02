#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
@version:
@author: leo Yang
@license: none
@contact: yangliw3@foxmail.com
@site:
@software:PyCharm
@file:setting.py
@time(UTC+8):16/10/2-10:03
'''

import os,sys

APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(APP_PATH, "etc", "blockhouse.conf")

sys.path.append(APP_PATH)