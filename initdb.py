#!/usr/bin/python
# -*-coding:UTF-8-*-

import sys
import time
import yaml
import pymongo
from hashlib import md5

zone_map = {
    '动漫': '一些关于动漫的事情',
    '音乐': '一些关于音乐的事情',
    '轻小说': '一些关于轻小说的事情'
}


def create_admin(db, setting):
    email = raw_input('请输入可用邮箱账号: ')
    username = raw_input('请输入管理员用户名: ')
    password = raw_input('请输入管理员密码: ')
    hash_object = md5(password + setting['salt'])
    password = hash_object.hexdigest()

    user = {
        'username': username,
        'password': password,
        'money': setting['init_money'],
        'register_time': time.time(),
        'favorite': [],
        'email': email,
        'level': 0,
        'qq': '',
        'website': '',
        'address': '',
        'signal': u'这个人太懒，还没有留下任何东西',
        'openemail': 1,
        'openfavorite': 1,
        'openqq': 1,
        'following': [],
        'follower': [],
        'allowemail': 1,
        'logintime': None,
        'loginip': None
    }
    db.user.insert(user)


def create_zone():

    for name, desc in zone_map.items():
        data = {
            'name': name,
            'description': desc,
            'nums': 0
        }
        db.zone.insert(data)


if __name__ == '__main__':
    try:
        with open('setting.yaml', 'r') as f:
            setting = yaml.load(f)
    except:
        print 'can not load setting file'
        sys.exit(0)
    client = pymongo.MongoClient(setting['database']['address'])
    db = client[setting['database']['db']]
    isdo = raw_input('是否创建管理员账户(Y/n): ')
    if isdo in ('Y', 'y'):
        create_admin(db, setting['global'])
    else:
        print '什么都没做'
    isdo = raw_input('是否初始化版块分区(Y/n): ')
    if isdo in ('Y', 'y'):
        create_zone()
    else:
        print '什么都没做'
