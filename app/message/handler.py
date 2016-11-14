# -*-coding:UTF-8-*-
import tornado.web
import tornado.gen
from ushio._base import BaseHandler
from bson import ObjectId


class MessageHandler(BaseHandler):

    def initialize(self):
        BaseHandler.initialize(self)
        self.method_list = ['read', 'del']

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def get(self):
        page = self.get_query_argument('page', 1)
        page = int(page)
        limit = 10
        cursor = self.db.message.find({
            'to_name': self.current_user['username']
        })
        cursor.sort([('time', -1)]
                    ).limit(limit).skip((page - 1) * limit)
        messages = yield cursor.to_list(length=limit)
        self.render('message/template/message.html', messages=messages)

    @tornado.web.authenticated
    def post(self):
        method = self.get_body_argument('method', default=None)
        id_list = self.get_body_argument('id_list', default='').split('|')
        id_list = map(lambda id_: ObjectId(id_), id_list)
        if method in self.method_list:
            getattr(self, '_%s_action' % method)(id_list)
        else:
            self.custom_error('不存在这个方法')

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def _read_action(self, id_list):
        yield self.db.message.update({
            '_id': {
                '$in': id_list
            }
        }, {
            '$set': {
                'read': 1
            }
        })
        print id_list
        self.write('{"success":true}')
        self.finish()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def _del_action(self, id_list):
        yield self.db.message.remove({
            '_id': {
                '$in': id_list
            }
        })
        self.write('{"success":true}')
        self.finish()
