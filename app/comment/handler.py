# -*-coding:UTF-8-*-

#
# Ajax handler
#

import tornado.web
import tornado.gen
import time
from bson import ObjectId
from ushio._base import BaseHandler


class CommentNewHandler(BaseHandler):

    def initialize(self):
        super(CommentNewHandler, self).initialize()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        tid = self.get_body_argument('tid', None)
        content = self.get_body_argument('content', None)
        current_user = self.current_user
        if tid and current_user and content:
            rtn = yield self.db.topic.find_and_modify({
                '_id': ObjectId(tid)
            }, {
                '$push': {
                    'comment': {
                        'content': content,
                        '_id': current_user['_id'],
                        'username': current_user['username'],
                        'time': time.time()
                    }
                },
                '$set': {
                    'lastcomment': time.time()
                }
            })
            if rtn:
                self.write('{"success":true}')
                self.finish()

        self.custom_error()


class CommentDeleteHandler(BaseHandler):

    def initialize(self):
        super(CommentDeleteHandler, self).initialize()
