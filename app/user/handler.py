# -*-coding:UTF-8-*-
import os
import tornado.web
import tornado.gen
from hashlib import md5
from bson import ObjectId
from util.captcha import Captcha
from app.user.model import UserModel
from ushio._base import BaseHandler


class ProfileHandler(BaseHandler):

    def initialize(self):
        super(ProfileHandler, self).initialize()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, username):
        user = yield self.db.user.find_one({
            'username': username
        }, {
            'password': 0,
            'loginip': 0,
            'logintime': 0
        })
        if not user:
            self.custom_error('不存在这个用户')
        if not user['allowemail']:
            del user['allowemail']
        if not user:
            self.set_status(status_code=404)

        # 取出 user 的topic
        page = int(self.get_query_argument('page', 1))
        limit = 10
        cursor = self.db.topic.find({
            'author_id': str(user['_id'])
        })
        cursor.sort([('time', -1)]).limit(limit).skip((page - 1) * limit)
        topics = yield cursor.to_list(length=limit)
        self.render('user/template/user.html', userinfo=user, topics=topics,
                    label_map=UserModel().get_label())


class UpdateHandler(BaseHandler):

    def initialize(self):
        super(UpdateHandler, self).initialize()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def get(self):
        user = yield self.db.user.find_one({
            'username': self.current_user['username']
        }, {
            '_id': 0,
            'password': 0
        })
        model = UserModel()
        self.render('user/template/user-update.html', userinfo=user,
                    label_map=model.get_label())

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def post(self):
        profile = {}
        info = {}
        update = self.get_body_argument('update', None)
        if update == 'private':
            info['openqq'] = int(self.get_body_argument('openqq', 1))
            info['openemail'] = int(self.get_body_argument('openemail', 1))
            info['openfavorite'] = int(
                self.get_body_argument('openfavorite', 1))
            info['allowemail'] = int(self.get_body_argument('allowemail', 1))
        elif update == 'profile':
            info['address'] = self.get_body_argument('address', '')
            info['qq'] = self.get_body_argument('qq', '')
            info['website'] = self.get_body_argument('website', '')
        else:
            pass
        model = UserModel()
        if not model(info):
            print model.error_msg
            self.custom_error(model.error_msg)
        else:
            profile.update(info)

        file_metas = self.request.files.get('avatar', '')
        if file_metas:
            for meta in file_metas:
                ext = meta['filename'].split('.')[-1]
                filename = '{0}.{1}'.format(self.current_user['_id'], ext)
                filepath = os.path.join(self.upload_path, filename)
                with open(filepath, 'wb') as f:
                    f.write(meta['body'])

        password = self.get_body_argument('password', '')
        if password:
            new_password = self.get_body_argument('new_password', '')
            re_password = self.get_body_argument('re_password', '')
            if len(new_password) < 6:
                self.custom_error('新密码太短')
            if new_password != re_password:
                self.custom_error('两次输入的密码不相同')
            user = yield self.db.user.find_one({
                'username': self.current_user['username']
            })
            _ = md5(password + self.settings['salt'])
            if user['password'] == _.hexdigest():
                profile['password'] = md5(
                    new_password + self.settings['salt']).hexdigest()
            else:
                self.custom_error('原始密码输入错误')

        yield self.db.user.update({
            'username': self.current_user['username']
        }, {
            '$set': profile
        })

        self.redirect('/user/update')


class UserHandler(BaseHandler):

    def initialize(self):
        super(UserHandler, self).initialize()

    def prepare(self):
        super(UserHandler, self).prepare()
        self.get_action_map = [
            'edit',
            'favorite',
            'publish'
        ]

        self.post_action_map = [
            'edit',
            ''
        ]

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        # 这里应该 self.get_query_argument('action')
        # 还是这样比较好呢
        if args[0] in self.get_action_map:
            getattr(self, 'get' + args[0])(*args[1:])
        else:
            self.detail_action(args[0])

    def post(self, *args, **kwargs):
        if args[0] in self.post_action_map:
            getattr(self, 'post' + args[0])(*args[1:])
        else:
            self.custom_error('参数错误')

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get_detail(self, uid):
        pass

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get_edit(self, *args):
        user = yield self.db.user.find_one({
            'username': self.current_user['username']
        })
        self.render('profile.html', user=user)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post_edit(self, *args):
        profile = {}
        profile['address'] = self.get_body_argument('address', '')
        profile['qq'] = self.get_body_argument('qq', '')
        profile['email'] = self.get_body_argument('email', '')
        profile['website'] = self.get_body_argument('website', '')
        password = self.get_body_argument('password', '')
        if password:
            new_password = self.get_body_argument('newpassword', '')
            re_password = self.get_body_argument('repassword', '')
            if len(new_password) <= 6:
                self.custom_error('新密码太短')
            if new_password != re_password:
                self.custom_error('两次输入的密码不相同')
            user = yield self.db.user.find_one({
                'username': self.current_user['username']
            })
            _ = md5(password, self.settings['salt'])
            if user['password'] == _.hexdigest():
                profile['password'] = md5(
                    new_password, self.settings['salt']).hexdigest()
            else:
                self.custom_error('原始密码输入错误')
        isexisted = yield self.db.user.find_one({
            'email': profile['email']
        })
        if isexisted:
            self.custom_error('邮箱已经被人使用')
        # model 验证
        #
        #
        #

        yield self.db.user.update({
            'username': self.current_user['username']
        }, {
            '$set': profile
        })
        self.redirect('/user/edit')

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get_favorite(self, *arg):
        limit = 10
        page = int(arg[0])
        page = 1 if page <= 0 else page
        cursor = self.db.topics.find({
            'favorite': self.current_user['username']
        })
        cursor.sort([('_id', -1)]).limit(limit).skip((page - 1) * limit)
        posts = yield cursor.to_list()
        self.render('favorite.html', posts, page=page)

    @tornado.gen.coroutine
    def post_favorite(self, *args):
        topic_id = int(args[0])
        yield self.db.topics.find_and_modify({
            '_id': ObjectId(topic_id)
        }, {
            '$pull': {'favorite': self.current_user['username']}
        })
        # Ajax Restful 接口
        #
        #
        self.write('successful')

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get_publish(self, *args):
        limit = 10
        page = int(args[0])
        page = 1 if page <= 0 else page
        topics = yield self.db.topics.find({
            'author': self.current_user['username']
        }).limit(limit).skip((page - 1) * limit)
        topics = topics.to_list()
        self.render('publish.html', topics=topics, page=page)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post_publish(self, *args):
        pass


class DeleteHandler(BaseHandler):

    def initialize(self):
        super(DeleteHandler, self).initialize()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        #
        # 删除数据库用户
        # 删除用户session
        #
        password = self.get_body_argument('password', '')
        if password:
            user = yield self.db.user.find_one({
                'username': self.current_user['username']
            })
            _ = md5(password + self.settings['salt'])
            if user['password'] == _.hexdigest():
                if self.get_cookie('TORNADOSESSION'):
                    self.clear_cookie('TORNADOSESSION')
                self.db.user.remove({
                    '_id': ObjectId(self.current_user['_id'])
                })
                self.session.delete('user_session')
                self.redirect('/')
        self.custom_error('原始密码输入错误')
