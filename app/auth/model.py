# -*-coding:UTF-8-*-

from ushio._model import Model


class LoginModel(Model):
    __rules__ = {
        'title': {
            'label': '标题',
            'required': True,
            'type': unicode,
            'max_length': 36,
            'min_length': 1,
        },
        'content': {
            'label': '内容',
            'required': True,
            'type': unicode
        },
        'price': {
            'label': '价格',
            'type': int,
            'min': 0,
            'max': 10
        }
    }


class RegisterModel(Model):
    __rules__ = {
        'username': {
            'label': '用户名'
        }
    }
