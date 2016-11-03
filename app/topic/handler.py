# -*-coding:UTF-8-*-
import time
import tornado.web
import tornado.gen
from bson import ObjectId
import json
from app.topic.model import TopicModel
from ushio._base import BaseHandler


class HomeHandler(BaseHandler):

    def initialize(self):
        super(HomeHandler, self).initialize()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        '''
            首页 tab页
        '''
        tab = self.get_query_argument('tab', '')
        if tab:
            topics = yield self.db.topic.find({
                'tab': tab
            })
        else:
            limit = 20
            page = 1
            cursor = self.db.topic.find({}, {
                'content': 0,
                'like': 0,
                'unlike': 0,
            })
            cursor.sort([('top', -1), ('lastcomment', -1), ('time', -1)]
                        ).limit(limit).skip((page - 1) * limit)
            topics = yield cursor.to_list(length=limit)
        print topics
        self.render('topic/template/topic.html', topics=topics)


class TopicNewHandler(BaseHandler):

    def initialize(self):
        super(TopicNewHandler, self).initialize()

    @tornado.web.authenticated
    def get(self):
        topic = dict()
        if self.cache['topic']:
            topic = self.cache['topic']
        self.render('topic/template/topic-new.html', topic=topic)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        title = self.get_body_argument('title', '')
        content = self.get_body_argument('content', '')
        rtn = {'success': 1, 'tid': 0, 'msg': ''}
        if not self.current_user:
            self.redirect('/login')
        if self.current_user['money'] - self.settings['charge'] < 0:
            rtn['success'] = 0
            rtn['msg'] = '余额不足'
            # self.custom_error('余额不足')

        topic = {
            'title': title,
            'content': content,
            'author_id': self.current_user['_id'],
            'author': self.current_user['username'],
            'view': 0,
            'like': 0,
            'price': 0,  # 价格
            'time': time.time(),
            'star': False,  # 精华
            'comment': [],
            'top': False,   # 置顶
            'lastcomment': time.time()
        }

        model = TopicModel()
        if not model(topic):
            self.cache['topic'] = topic
            rtn['success'] = 0
            # self.custom_error()
            self.write('0')
        tid = yield self.db.topic.insert(topic)
        # self.redirect('/topics/{}'.format(tid))
        # Ajax
        rtn['tid'] = str(tid)
        self.write(json.dumps(rtn))
        self.finish()


class NodeHandler(BaseHandler):

    def initialize(self):
        super(NodeHandler, self).initialize()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, node):
        '''
            结点页面
        '''
        limit = 20
        page = self.get_query_argument('p')
        topics = yield self.db.topics.find().limit(limit).skip((page - 1) * limit)
        self.render('topic/template/node.html', topics=topics)


class TopicHandler(BaseHandler):

    def initialize(self):
        super(TopicHandler, self).initialize()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, topic_id):
        '''
            帖子详情页
        '''
        try:
            tid = ObjectId(topic_id)
            topic = yield self.db.topic.find_one({
                '_id': tid
            })
            assert topic is not None
        except:
            self.custom_error()
        ismine = False
        if topic['author_id'] == self.current_user['_id']:
            ismine = True
        self.render('topic/template/topic-detail.html',
                    topic=topic, ismine=ismine)


class TopicUpdateHandler(BaseHandler):

    def initialize(self):
        super(TopicUpdateHandler, self).initialize()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, tid):
        try:
            tid = ObjectId(tid)
            topic = yield self.db.topic.find_one({
                '_id': tid
            })
            assert topic is not None
            assert topic['author_id'] == self.current_user['_id']
        except:
            self.custom_error('您无权进行修改')
        self.render('topic/template/topic-new.html', topic=topic)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, tid):
        topic = {
            'title': self.get_body_argument('title', ''),
            'content': self.get_body_argument('content', ''),
            'price': self.get_body_argument('price', 0)
        }
        model = TopicModel()
        if model(topic):
            try:
                tid = ObjectId(tid)
            except:
                self.cache['topic'] = topic
                self.custom_error('正在更新一个不存在的帖子')
            yield self.db.topic.update({
                '_id': tid
            }, {
                '$set': topic
            })
            self.redirect('/topics/{}'.format(tid))
        else:
            self.custom_error()
