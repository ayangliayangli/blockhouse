#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
@version:
@author: leo Yang
@license: none
@contact: yangliw3@foxmail.com
@site:
@software:PyCharm
@file:core.py
@time(UTC+8):16/10/2-08:35
'''

# 这里是把项目的目录导入
# 当把程序放到其他地方执行的时候, 项目目录不会默认加入 sys.path
# 此功能已经移动到  /bin/start.py
# import sys,os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from src import data_durable_via_mysql
from src import my_paramiko
from etc import setting

# global variable
logined_user = {"username":"", "password":""}


def cmd_help():
    s = """
    help information for you :
        conn : make a connection with specified host
        exit : exit blockhouse system
        help : help infomation
        log  : log infomation under current user
        add host group  : add group of host
        add host user   : add host user
        add host        : add a host, depend on host group and host user
        add user        : add a blockhouse system user
        """
    print(s)


def login():
    if logined_user["username"]:
        print("{}, you have logined".format(logined_user["username"]))
    else:
        # 用户还没有登录
        print("you should login first")
        name = input("name:")
        password = input("password:")
        login_sussess_flag = data_durable_via_mysql.login(username=name,
                                                          password=password)
        if login_sussess_flag:
            logined_user["username"] = name
            logined_user["password"] = password
            print("[{}] welcome to blockhouse".format(logined_user["username"]))
            cmd_help()
        else:
            print("logined failure, check user and password")


def connect_host():

    user_id, host_id = data_durable_via_mysql.select_host_with_user(logined_user["username"],
                                                 logined_user["password"],)
    print("user_id", user_id)
    print("host_id", host_id)

    session = data_durable_via_mysql.get_session()
    host = session.query(data_durable_via_mysql.Host).filter(data_durable_via_mysql.Host.id==host_id).first()
    ip = host.ip
    port = host.port
    username = host.host_users.name
    password = host.host_users.password
    print(type(ip), ip)
    print(type(port), port)
    print(type(username), username)
    print(type(password), password)

    # 这个方法天荒地老死循环,直到ctrl + c 退出那个tty
    my_paramiko.run(host=ip, port=port, username=username, password=password, blockhouseuser_id=user_id)




def main():
    login()
    # connect_host()
    while True:
        cmd = input("type ? for more >>").strip()
        if cmd == "help" or cmd == "?":
            cmd_help()
        elif cmd == "conn":
            connect_host()
        elif cmd == "log":
            data_durable_via_mysql.show_record_via_username(logined_user["username"])
        elif cmd == "add host group":
            data_durable_via_mysql.add_host_group()
        elif cmd == "add host user":
            data_durable_via_mysql.add_host_user()
        elif cmd == "add host":
            data_durable_via_mysql.add_host()
        elif cmd == "add user":
            data_durable_via_mysql.add_user()
        elif cmd == "exit":
            break
        elif cmd == "":
            continue
        else:
            cmd_help()



if __name__ == '__main__':
    main()