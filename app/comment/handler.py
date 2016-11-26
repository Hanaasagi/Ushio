# -*-coding:UTF-8-*-

#
# Ajax handler
#

import re
import time
import json
import tornado.web
import tornado.gen
from bson import ObjectId
from ushio._base import BaseHandler
from util.message import Message


class CommentNewHandler(BaseHandler):

    def initialize(self):
        super(CommentNewHandler, self).initialize()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def post(self):
        tid = self.get_body_argument('tid', None)
        content = self.get_body_argument('content', None)
        title = self.get_body_argument('title', None)
        current_user = self.current_user
        if tid and content:
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
            # comment @
            rtn2 = True
            r = re.compile('(@\w+ )')
            tolist = map(lambda s: s.lstrip('@').rstrip(), r.findall(content))
            if len(tolist) == 0:
                tolist.append(self.get_body_argument('author'))
            for name in tolist:
                message = {
                    'from_id': self.current_user['_id'],
                    'from_name': self.current_user['username'],
                    'title': title,
                    'content': content,
                    'tid': tid,
                }
                rtn2 = self.redis_conn.zadd(
                    'mailbox:' + name, json.dumps(message), time.time())
                Message.notify(name)
            if rtn and rtn2:
                self.write('{"success":true}')
                self.finish()

        self.custom_error()


class CommentDeleteHandler(BaseHandler):

    def initialize(self):
        super(CommentDeleteHandler, self).initialize()
