# -*-coding:UTF-8-*-]
import json
import tornado.web
import tornado.gen
import time
import tornado.websocket
from ushio._base import BaseHandler
from util.message import Message


class MessageWebSocket(tornado.websocket.WebSocketHandler, BaseHandler):

    def open(self):
        self.check_message()
        Message.register({self.current_user['username']: self.check_message})

    def on_message(self, message):
        pass

    def on_close(self):
        Message.unregister(self.current_user['username'])

    def check_message(self):
        t = self.redis_conn.get('seen:' + self.current_user['username'])
        messages = self.redis_conn.zrangebyscore(
            'mailbox:' + self.current_user['username'], int(float(t)), int(time.time()))
        self.write_message(str(len(messages)))


class MessageHandler(BaseHandler):

    def initialize(self):
        BaseHandler.initialize(self)
        self.method_list = ['del']

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def get(self):
        result = self.redis_conn.zrange(
            'mailbox:' + self.current_user['username'], 0, -1, withscores=True)
        t = self.redis_conn.get('seen:' + self.current_user['username'])
        messages = []
        for msg, t in result:
            msg = json.loads(msg)
            msg['time'] = t.__repr__()
            messages.insert(0, msg)
        # 更新查看信箱时间
        self.redis_conn.set(
            'seen:' + self.current_user['username'], time.time())
        self.render('message/template/message.html', messages=messages)

    @tornado.web.authenticated
    def post(self):
        method = self.get_body_argument('method', default=None)
        id_list = self.get_body_argument('id_list', default='').split('|')
        if method in self.method_list:
            getattr(self, '_%s_action' % method)(id_list)
        else:
            self.custom_error('不存在这个方法')

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def _del_action(self, id_list):
        pipe = self.redis_conn.pipeline()
        try:
            pipe.multi()
            for id_ in id_list:
                print id_
                self.redis_conn.zremrangebyscore('mailbox:' + self.current_user['username'], id_,id_)
                pipe.zremrangebyscore(
                    'mailbox:' + self.current_user['username'], id_, id_)
            pipe.execute()
        except Exception,e:
            print e
        else:
            self.write('{"success":true}')
        self.finish()
