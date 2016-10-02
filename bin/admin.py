#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
@version:
@author: leo Yang
@license: none
@contact: yangliw3@foxmail.com
@site:
@software:PyCharm
@file:admin.py
@time(UTC+8):16/10/2-21:43
'''

# 这里是把项目的目录导入
# 当把程序放到其他地方执行的时候, 项目目录不会默认加入 sys.path
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import data_durable_via_mysql

# 在数据库中建表
data_durable_via_mysql.init_db()

# 无需登录,完成一个用户的创建
print("start add HOST GROUP ---:")
data_durable_via_mysql.add_host_group()
print("start add HOST USER --- :")
data_durable_via_mysql.add_host_user()
print("start add HOST: --- ")
data_durable_via_mysql.add_host()
print("start add USER: --- ")
data_durable_via_mysql.add_user()