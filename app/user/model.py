# -*-coding:UTF-8-*-

from ushio._model import Model


class UserModel(Model):

    __rules__ = {
        'username': {
            'label': '用户名',
            'required': True,
            'type': unicode,
            'max_length': 36,
            'min_length': 1,
            'pattern': ur'^[a-zA-Z0-9_\-\u4e00-\u9fa5]+$'
        },
        'password': {
            'label': '密码',
            'required': True,
            'type': str,
            'min_length': 6
        },
        'email': {
            'label': 'Email',
            'required': True,
            'type': unicode,
            'max_length': 64,
            'email': True
        },
        'openemail': {
            'label': '公开邮箱'
        },
        'favorite': {
            'label': '喜欢的文章',
            'type': list,
        },
        'openfavorite': {
            'label': '公开收藏'
        },
        'money': {
            'label': '金币',
            'type': int,
            'min': 0
        },
        'website': {
            'label': '个人主页',
            'type': unicode,
            'max_length': 128,
            'url': True
        },
        'address': {
            'label': '地址',
            'type': unicode,
            'max_length': 256
        },
        'signal': {
            'label': '签名',
            'type': unicode,
            'max_length': 512
        },
        'qq': {
            'label': 'QQ',
            'type': unicode,
            'max_length': 16,
            'min_length': 5,
            'number': True
        },
        'loginip': {
            'label': '上次登陆IP'
        },
        'register_time': {
            'label': '注册时间'
        },
        'logintime': {
            'label': '上次登陆时间'
        }
    }
