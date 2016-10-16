# -*-coding:UTF-8-*-

from ushio._model import Model


class TopicModel(Model):
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
        }
    }
