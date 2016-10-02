#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
@version:
@author: leo Yang
@license: none
@contact: yangliw3@foxmail.com
@site:
@software:PyCharm
@file:start.py
@time(UTC+8):16/10/2-21:24
'''

# 这里是把项目的目录导入
# 当把程序放到其他地方执行的时候, 项目目录不会默认加入 sys.path
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



from src import core
core.main()