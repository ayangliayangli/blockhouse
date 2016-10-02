#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
@version:
@author: leo Yang
@license: none
@contact: yangliw3@foxmail.com
@site:
@software:PyCharm
@file:data_durable_via_mysql.py
@time(UTC+8):16/10/2-08:35
'''

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Index, BigInteger
from sqlalchemy.orm import sessionmaker, relationship

import configparser  # 从配置文件中读取数据库的信息
from etc import setting

import time

# 从配置文件里面读取数据库连接信息
config = configparser.ConfigParser()
config.read(setting.CONFIG_PATH, encoding='utf-8')
db_host = config.get("db", "db_host")
db_port = config.get("db", "db_port")
db_user = config.get("db", "db_user")
db_password = config.get("db", "db_password")
db_name = config.get("db", "db_name")


# engine_str = "mysql+pymysql://yangli:yanglipass@192.168.126.250:3306/blockhouse"  # 原始的engine_str
engine_str = "mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}".format(db_user=db_user,
                                                                                            db_password=db_password,
                                                                                            db_host=db_host,
                                                                                            db_port=db_port,
                                                                                            db_name=db_name,
                                                                                            )
# print("engine_str", engine_str)  # 调试信息,注释
engine = create_engine(engine_str, max_overflow=5)
Base = declarative_base()





class HostGroup(Base):
    """server group"""
    __tablename__ = "_t_host_group"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    desc = Column(String(64), default="you can add description by youself")

    def __str__(self):
        s = "id:{}     name:{}     desc:{}".format(self.id, self.name, self.desc)
        return s


class HostUser(Base):
    """
    登录机器的用户,比如 root
    """
    __tablename__ = "_t_host_user"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(32), nullable=False, unique=False)
    password = Column(String(32), nullable=False)

    def __str__(self):
        s = "name:{}     password:{}     id:{}".format(self.name, self.password, self.id)
        return s


class Host(Base):
    """
    服务器
    """
    __tablename__ = "_t_host"
    id = Column(Integer, autoincrement=True, primary_key=True)
    ip = Column(String(64), nullable=False, unique=False)
    port = Column(Integer, nullable=False, unique=False, default=22)
    host_user_id = Column(Integer, ForeignKey("_t_host_user.id"))
    host_group_id = Column(Integer, ForeignKey("_t_host_group.id"))

    # 这里方便连表查询,对表结构没有影响
    host_users = relationship(HostUser, backref="host")
    host_groups = relationship(HostGroup, backref="host")


class User(Base):
    """user to login blockhouse
        因为这里存放了用户关联的主机信息,所以用户名以及密码不使用uniq
        其实也可以把用户和主机的对应信息放在host表钟,或者在做一张表
    """
    __tablename__ = "_t_user"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(32), nullable=False, unique=False)
    password = Column(String(32), nullable=False, unique=False)
    host_id = Column(Integer, ForeignKey("_t_host.id"))

    hosts = relationship(Host, backref="user")


class Record(Base):
    """
    每条操作记录,写入数据库中保存
    """
    __tablename__ = "_t_record"
    id = Column(Integer, autoincrement=True, primary_key=True)
    timestamp = Column(BigInteger, nullable=False)
    content = Column(String(64), nullable=False)
    user_id = Column(Integer, ForeignKey("_t_user.id"))

    user = relationship(User, backref="records")

    def __str__(self):
        timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timestamp))
        s = '''user:{} date:{} content:{}'''.format(self.user.name, timestr, self.content)
        return s


def init_db():
    Base.metadata.create_all(engine)


def drop_db():
    Base.metadata.drop_all(engine)


def get_session():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def add_host_group():
    session = get_session()
    name = input("group name:")
    desc = input("description:")
    host_group_obj = HostGroup(name=name, desc=desc)
    session.add(host_group_obj)
    session.commit()  # commit之后数据才会真正的持久化


def add_host_user():
    session = get_session()
    name = input("name:")
    password = input("password:")
    session.add(HostUser(name=name, password=password))
    session.commit()


def add_host():
    session = get_session()
    ip = input("host ip:")
    port = input("host port:")

    # select host group
    host_groups_all = session.query(HostGroup).all()
    print("host group as following:")
    for index, item in enumerate(host_groups_all, 1):
        print("key:{}  {}".format(index, item))
    inp = input("select key:")
    sel_host_group_id = host_groups_all[int(inp) - 1].id



    # select host user
    host_user_all = session.query(HostUser).all()
    print("host user as following:")
    for index, item in enumerate(host_user_all, 1):
        print("key:{}  {}".format(index, item))
    inp = input("select key:")
    sel_host_user_id = host_user_all[int(inp) - 1].id

    # 判断是有这条数据,如果没有就插入,如果存在就提示已经存在了,不在重复插入
    obj_is_exist_flag = session.query(Host).filter(Host.ip==ip,
                                                   Host.port==port,
                                                   Host.host_group_id==sel_host_group_id,
                                                   Host.host_user_id==sel_host_user_id,
                                                   ).first()
    if not obj_is_exist_flag:
        session.add(Host(ip=ip, port=port,
                         host_user_id=sel_host_user_id,
                         host_group_id = sel_host_group_id,
                         ))
        session.commit()
    else:
        print("host is exist in db, do not need insert one more")


def add_user():
    session = get_session()

    print("add blockhouse user:")
    name = input("username:")
    password = input("password:")

    # 选择一台机器来授权 host host_user
    hosts_all = session.query(Host).all()
    for index, host in enumerate(hosts_all, 1) :
        s = "index:{}  ----  ip:{}  port:{} host_group:{} hostname:{}  password:{}".format(index,
                                                                                            host.ip,
                                                                                            host.port,
                                                                                            host.host_groups.name,
                                                                                            host.host_users.name,
                                                                                            host.host_users.password,
                                                                                            )
        print(s)
    inp = input("choose index:")
    sel_host_id = hosts_all[int(inp) - 1].id

    # 判断是否已有该用户
    user_exist_flag = session.query(User).filter(User.name==name,
                                    User.password==password,
                                    User.host_id==sel_host_id,
                                    ).first()
    if not user_exist_flag:
    # 创建一个user对象,然后添加到mysql中
        user_obj = User(name=name, password=password, host_id=sel_host_id)
        session.add(user_obj)
        session.commit()
    else:
        print("user is exist , do not need create one more time")


def select_host_with_user(username,password):
    """

    :param username:
    :return: 返回想要连接的host的id 以及user_id
    """
    session = get_session()
    users = session.query(User).filter(User.name==username, User.password==password).all()

    # 显示该用户所有的主机
    for index, user in enumerate(users, 1):
        host = user.hosts  # User 的名字取的不好,最好用   host
        s = "index:{}  ----  ip:{}  port:{} host_group:{} hostname:{}  password:{}".format(index,
                                                                                            host.ip,
                                                                                            host.port,
                                                                                            host.host_groups.name,
                                                                                            host.host_users.name,
                                                                                            host.host_users.password,
                                                                                            )
        print(s)
    # 获取用户的输入
    while True:
        inp = input("which one do you want to connect:")
        if inp.isnumeric():
            break
        elif inp == "":
            continue
        else:
            print("just input index, is a number")
            continue

    sel_host_id = users[int(inp) - 1].hosts.id
    sel_user_id = users[int(inp) - 1].id

    ret = (sel_user_id, sel_host_id)
    return ret



def login(username,password):
    session = get_session()
    user_obj = session.query(User).filter(User.name==username, User.password==password).first()
    if user_obj:
        # 登录成功
        return True
    else:
        return False


def make_record_via_mysql(timestamp, content, blockhouseuser_id):
    session = get_session()
    session.add(Record(timestamp=timestamp, content=content, user_id=blockhouseuser_id))
    print("----","start write record to mysql")
    session.commit()

def show_record_via_username(username):
    """
    根据用户当前登录的用户,来显示该用户的所有操作记录
    :param username:
    :return:
    """
    session = get_session()
    # [(1),(3),(5)] 下面
    user_ids = session.query(User.id).filter(User.name==username).all()
    # (1,3,5) 下面
    ids = list(zip(*user_ids))[0]
    records = session.query(Record).filter(Record.user_id.in_(ids)).all()

    for record in records:
        print(record)


def main():
    # init_db()
    # drop_db()
    # add_host_group()
    # add_host_user()
    # add_host()
    # add_user()
    # print("return:", select_host_with_user("yangli","123456"))
    show_record_via_username("yangli")

if __name__ == '__main__':
    main()