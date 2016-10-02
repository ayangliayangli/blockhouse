# 测试步骤


## mysql数据库安装配置
* 建议centos6.5
* yum install -y mysql mysql-server mysql-devel
* /etc/init.d/mysqld start
* create databases blockhouse
* grant all on blockhouse.* to 'db_user'@'%' identified by "db_user_password"


## 修改配置文件
        修改db_host, db_port, db_user, db_password, db_name
        使其符合上面数据库的规则


## 启动程序
        cd bin/  # 切换到项目的bin目录下面
        python manage.py  # 系统初始化的时候没有用户等信息,从这个入口可以添加一个用户信息
        python start.py  # 正式启动系统
        接下来请详细查看帮助信息即可
        
        
        
        help information for you :
            conn : make a connection with specified host
            exit : exit blockhouse system
            help : help infomation
            log  : log infomation under current user
            add host group  : add group of host
            add host user   : add host user
            add host        : add a host, depend on host group and host user
            add user        : add a blockhouse system user
