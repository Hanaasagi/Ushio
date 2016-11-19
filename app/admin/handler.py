# -*-coding:UTF-8-*-
import time
import yaml
import json
import tornado.web
import tornado.gen
from ushio._base import BaseHandler
from util.captcha import Captcha
from hashlib import md5
from bson import ObjectId


class AdminIndexHandler(BaseHandler):

    def initialize(self):
        super(AdminIndexHandler, self).initialize()

    def prepare(self):
        super(AdminIndexHandler, self).prepare()
        self.action_map = [
            'topic',
            'user',
            'comment',
            'configure'
        ]

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        cursor = self.db.users.find()
        users = yield cursor.to_list(length=10)
        self.render('admin/template/admin-index.html', users=users)
        # action = self.get_query_arguemnt('action', 'default')
        # if action in self.action_map:
        #     getattr(self, action + '_action')(*args, **kwargs)
        # else:
        #     self.default_action(*args, **kwargs)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        username = self.get_body_argument('username', '')
        password = self.get_body_argument('password', '')
        captcha = self.get_body_argument('captcha', '')
        remember = self.get_body_argument('remember', False)
        if not Captcha.verify(captcha, self):
            self.redirect('/ushio')
        user = yield self.db.admin.find_one({
            'username': username
        })
        _ = md5(password, self.setting['salt'])
        if user['password'] == _.hexdigest():
            session = self.set_session(user)
            if remember:
                cookie = json.dumps(session)
                self.set_secure_cookie('user', cookie, 30)
            yield self.db.admin.find_and_modify({
                'username': username}, {
                '$set': {
                    'logintime': time.time(),
                    'loginip': self.get_ipaddress()
                }}
            )
            self.remember('/ushio/manage/')
        else:
            self.redirect('/ushio?erro=login_')

    def default_action(self, *args, **kwargs):
        pass

    def configure_action(self, *args, **kwargs):
        with open(self.settings['config_file'], 'r') as f:
            config = yaml.load(f)
        config['global']['site'] = {
            'sitename': self.get_body_argument('sitename'),
            'description': self.get_body_argument('description')
        }
        config['global']['money'] = int(self.get_body_argument('money'))
        register_way = self.get_body_argument('register')
        if register_way not in ('opened', 'invited'):
            self.custom_error('register way must be opened or invited')
        config['global']['register'] = register_way
        self.write_config(config)
        self.redirect('/ushio/manage/setting')

    def topic_action(self, *args, **kwargs):
        pass

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def user_action(self, *args, **kwargs):
        uid = self.get_body_argument('uid')
        user = {
            'email': self.get_body_argument('email'),
            'website': self.get_body_argument('website'),
            'qq': self.get_body_argument('qq'),
            'address': self.get_body_argument('address')
        }
        # model 验证
        #
        #
        password = self.get_body_argument('password', '')
        # password 为空则保持
        if password:
            user['password'] = md5(password, self.settings['salt'])
        user = yield self.db.user.find_and_modify({
            '_id': ObjectId(uid)
        }, {
            '$set': user
        })
        self.redirect('/manage/userdetail/{}'.format(uid))

    def comment_action(self, *args, **kwargs):
        comment_id = self.get_body_argument('commentId')
        post_id = self.get_body_argument('post_id')
        yield self.db.topic.find_and_modify({
            '_id': ObjectId(post_id),
        }, {
            '$pull': {
                'comment': {
                    '_id': {'$eq': ObjectId(comment_id)}
                }
            }
        })
        self.redirect('/ushio/manage/?')


class AdminSettingHandler(BaseHandler):

    def initialize(self):
        super(AdminSettingHandler, self).initialize()

    def prepare(self):
        super(AdminSettingHandler, self).prepare()

    def get(self):
        self.render('admin/template/admin-setting.html',
                    **self.settings)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def post(self):
        if self.current_user['level'] != 0:
            self.custom_error()
        settings = {
            'init_money': int(self.get_body_argument('init_money')),
            'reg_type': self.get_body_argument('reg_type'),
            'cookie_secret': self.get_body_argument('cookie_secret') or self.settings['cookie_secret'],
            'site': {
                'name': self.get_body_argument('sitename'),
                'keyword': self.get_body_argument('keyword'),
                'description': self.get_body_argument('description')
            }
        }
        self.settings.update(settings)
        custom_settings = {}
        with open(self.settings['config_file'], 'r') as f:
            custom_settings = yaml.load(f)
            custom_settings['global'].update(settings)
        with open(self.settings['config_file'], 'w') as f:
            yaml.dump(custom_settings, f,
                      default_flow_style=False, default_style='"')
        self.redirect('/ushio/setting')


class AdminUserListHandler(BaseHandler):

    def initialize(self):
        super(AdminUserListHandler, self).initialize()

    def prepare(self):
        super(AdminUserListHandler, self).prepare()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def get(self):
        page = self.get_query_argument('page', 1)
        limit = 5
        cursor = self.db.user.find()
        total = yield cursor.count()
        cursor.limit(limit).skip((page - 1) * limit)
        users = yield cursor.to_list(length=limit)
        self.render('admin/template/admin-userlist.html',
                    users=users, page=page, limit=limit, total=total)

    @tornado.web.authenticated
    def post(self):
        uid = self.get_body_argument('uid', None)
        action = self.get_body_argument('action', None)
        days = self.get_body_argument('days', 7)
        if action in ('delete', 'message', 'ban'):
            getattr(self, '_{}_action'.format(action))(uid, days)
        else:
            self.custom_error()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def _delete_action(self, uid, *args):
        yield self.db.user.remove({
            '_id': ObjectId(uid)
        })
        self.write('{"success":true}')
        self.finish()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def _message_action(self, uid, *args):
        user = yield self.db.user.find_one({
            '_id': ObjectId(uid)
        }, {
            'username': 1
        })

        message = {
            'from_id': self.current_user['_id'],
            'from_name': self.current_user['username'],
            'to_name': user['username'],
            'title': '系统通知',
            'tid': '',
            'read': 0,
        }
        rtn = yield self.db.message.insert(message)
        if rtn:
            self.write('{"success":true}')
            self.finish()
        else:
            self.custom_error()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def _ban_action(self, uid, days):
        rtn = yield self.db.user.update({
            '_id': ObjectId(uid)
        }, {
            '$set': {
                'ban': days
            }
        })
        if rtn:
            self.write('{"success":true}')
            self.finish()
        else:
            self.custom_error()


class AdminTagAddHandler(BaseHandler):

    def initialize(self):
        super(AdminTagAddHandler, self).initialize()

    def prepare(self):
        super(AdminTagAddHandler, self).prepare()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def post(self):
        name = self.get_body_argument('name', None)
        if not name:
            self.custom_error()

        tag = {
            'name': name,
            'nums': 0
        }
        rtn = yield self.db.tag.insert(tag)
        if rtn:
            self.write('{"success":true}')
            self.finish()
        else:
            self.custom_error()


class AdminTagDelHandler(BaseHandler):

    def initialize(self):
        super(AdminTagDelHandler, self).initialize()

    def prepare(self):
        super(AdminTagDelHandler, self).prepare()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def post(self):
        id_ = self.get_body_argument('id', None)
        if not id_:
            self.custom_error()
        rtn = yield self.db.tag.remove({
            '_id': ObjectId(id_)
        })
        if rtn:
            self.write('{"success":true}')
            self.finish()
        else:
            self.custom_error()


#
# 管理员是否应该修改用户的信息
#
class AdminUserUpdateHandler(BaseHandler):

    def initialize(self):
        super(AdminUserUpdateHandler, self).initialize()

    def prepare(self):
        super(AdminUserUpdateHandler, self).prepare()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def get(self, uid):
        pass
        # user = yield self.db.user.find_one({
        #     '_id': ObjectId(uid)
        # })
        # self.render('admin/template/admin-userupdate.html', user=user)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def post(self, uid):
        pass


class AdminColumnHandler(BaseHandler):

    def initialize(self):
        super(AdminColumnHandler, self).initialize()

    def prepare(self):
        super(AdminColumnHandler, self).prepare()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def get(self):
        cursor = self.db.zone.find()
        zones = yield cursor.to_list(length=4)

        cursor = self.db.tag.find()
        tags = yield cursor.to_list(length=100)
        self.render('admin/template/admin-column.html', zones=zones, tags=tags)
