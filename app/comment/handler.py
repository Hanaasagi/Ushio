# -*-coding:UTF-8-*-

#
# Ajax handler
#

import tornado.web
import tornado.gen
import time
import re
from bson import ObjectId
from ushio._base import BaseHandler


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
            if tolist:
                for name in tolist:
                    message = {
                        'from_id': self.current_user['_id'],
                        'from_name': self.current_user['username'],
                        'to_name': name,
                        'title': title,
                        'tid': tid,
                        'read': 0,
                    }
                    rtn2 = self.db.message.insert(message)
                    if not rtn2:
                        break
            else:
                message = {
                    'from_id': self.current_user['_id'],
                    'from_name': self.current_user['username'],
                    'to_name': self.get_body_argument('author'),
                    'title': title,
                    'tid': tid,
                    'read': 0,
                }
                rtn2 = self.db.message.insert(message)
            if rtn and rtn2:
                self.write('{"success":true}')
                self.finish()

        self.custom_error()


class CommentDeleteHandler(BaseHandler):

    def initialize(self):
        super(CommentDeleteHandler, self).initialize()
