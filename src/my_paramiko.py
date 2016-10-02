#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
@version:
@author: leo Yang
@license: none
@contact: yangliw3@foxmail.com
@site:
@software:PyCharm
@file:my_paramiko.py
@time(UTC+8):16/10/2-08:34
'''


import paramiko
from paramiko.py3compat import u
import sys,os
import socket
import getpass
from src import data_durable_via_mysql
import time




# vars
blockhouseuser_glo_id = ""

# windows does not have termios...
try:
    import termios
    import tty
    has_termios = True
except ImportError:
    has_termios = False


def interactive_shell(chan):
    if has_termios:
        posix_shell(chan)
    else:
        windows_shell(chan)


def posix_shell(chan):
    import select

    # 存下以前的tty信息,退出后恢复,这样该窗口才能复用
    oldtty = termios.tcgetattr(sys.stdin)
    try:
        # 改变当前tty属性  -- 设置程raw  原始的tty
        # 监听每一个字符的变化,都及时的通知主程序
        #

        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        chan.settimeout(0.0)

        # log 用于记录日志
        log = open('handle.log', 'a+', encoding='utf-8')
        tab_flag = False
        temp_list = []  # 用于存放当前命令,敲回车后及时的写入日志
        while True:
            r, w, e = select.select([chan, sys.stdin], [], [])
            if chan in r:
                # 服务器返回了数据
                try:
                    x = u(chan.recv(1024))  # python3 要注意兼容
                    if len(x) == 0:
                        sys.stdout.write('\r\n*** EOF\r\n')
                        break

                    if tab_flag:
                        if x.startswith('\r\n'):
                            pass
                        else:
                            temp_list.append(x)
                        tab_flag = False

                    sys.stdout.write(x)
                    sys.stdout.flush()
                except socket.timeout:
                    pass

            if sys.stdin in r:
                # 有用户输入的时候
                x = sys.stdin.read(1)  # 因为是监听每个字符,所以这里收一个字符就好
                import json

                if len(x) == 0:
                    break

                if x == '\t':
                    tab_flag = True
                elif x == '\r':
                    # return key : write log to file
                    # 注意这个return 不要写入文件中
                    # 博客里面的代码这里有逻辑错误,由于把每次敲的return也写入了文件
                    # 会导致  文件日志被下一条覆盖
                    print("temp_list", temp_list)
                    content = ''.join(temp_list)

                    if content:
                        # 有内容就开始写

                        # 写到文件
                        log.write(content)
                        log.flush()

                        # 日志写入数据库
                        timestamp = time.time()
                        data_durable_via_mysql.make_record_via_mysql(timestamp=timestamp,
                                                                     content=content,
                                                                     blockhouseuser_id=blockhouseuser_glo_id,)
                        temp_list.clear()  # clear temp_list
                else:
                    temp_list.append(x)

                chan.send(x)  # 这里才是核心逻辑,把输入的字符发送给机器执行

    finally:
        # 最终都要还原tty的属性
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)


# 未使用,不支持Windows
def windows_shell(chan):
    import threading

    sys.stdout.write("Line-buffered terminal emulation. Press F6 or ^Z to send EOF.\r\n\r\n")

    def writeall(sock):
        while True:
            data = sock.recv(256)
            if not data:
                sys.stdout.write('\r\n*** EOF ***\r\n\r\n')
                sys.stdout.flush()
                break
            sys.stdout.write(data)
            sys.stdout.flush()

    writer = threading.Thread(target=writeall, args=(chan,))
    writer.start()

    try:
        while True:
            d = sys.stdin.read(1)
            if not d:
                break
            chan.send(d)
    except EOFError:
        # user hit ^Z or F6
        pass


def run(host, port, username, password, blockhouseuser_id=""):

    # hostname = "192.168.126.230"
    # port = 6322
    # username = "bwweb"
    # pwd = "123456"

    global blockhouseuser_glo_id
    blockhouseuser_glo_id = blockhouseuser_id


    # 先简化代码,只考虑密码登录的状况
    tran = paramiko.Transport((host, port,))
    tran.start_client()
    tran.auth_password(username, password)

    # 打开一个通道
    chan = tran.open_session()
    # 获取一个终端
    chan.get_pty()
    # 激活器
    chan.invoke_shell()

    interactive_shell(chan)

    chan.close()
    tran.close()


if __name__ == '__main__':
    host = "192.168.126.230"
    port = 6322
    username = "bwweb"
    pwd = "123456"

    run(host=host, port=port, username=username, password=pwd)