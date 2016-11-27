# -*-coding:UTF-8-*-


class Message(object):

    _callbacks = {}

    @staticmethod
    def register(callback):
        Message._callbacks.update(callback)

    @staticmethod
    def unregister(callback_name):
        if callback_name in Message._callbacks:
            del Message._callbacks[callback_name]

    @staticmethod
    def notify(callback_name):
        if callback_name in Message._callbacks:
            Message._callbacks[callback_name]()
