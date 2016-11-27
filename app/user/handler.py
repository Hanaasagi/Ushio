# -*-coding:UTF-8-*-
import os
import tornado.web
import tornado.gen
from hashlib import md5
from bson import ObjectId
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
        total = yield cursor.count()
        cursor.sort([('time', -1)]).limit(limit).skip((page - 1) * limit)
        topics = yield cursor.to_list(length=limit)
        self.render('user/template/user-topic.html', userinfo=user,
                    topics=topics, limit=limit, page=page, total=total,
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
        print user
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


class FollowHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def post(self, following_name):
        user = yield self.db.user.find_one({
            'username': following_name
        }, {
            'following': 1,
            'follower': 1
        })
        me = {
            '_id': self.current_user['_id'],
            'username': self.current_user['username']
        }
        if me in user['follower']:
            rtn = yield self.db.user.find_and_modify({
                '_id': ObjectId(self.current_user['_id'])
            }, {
                '$pull': {
                    'following': {
                        '_id': user['_id'],
                        'username': following_name
                    }
                }
            })

            rtn2 = yield self.db.user.find_and_modify({
                'username': following_name
            }, {
                '$pull': {
                    'follower': me
                }
            })

        else:
            rtn = yield self.db.user.find_and_modify({
                'username': self.current_user['username']
            }, {
                '$push': {
                    'following': {
                        '_id': user['_id'],
                        'username': following_name
                    }
                }
            })
            rtn2 = yield self.db.user.find_and_modify({
                'username': following_name
            }, {
                '$push': {
                    'follower': me
                }
            })
        if rtn and rtn2:
            self.write('{"success":true}')
            self.finish()


class FollowingHandler(BaseHandler):

    def initialize(self):
        super(FollowingHandler, self).initialize()

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
        user['follow'] = user['following']
        self.render('user/template/user-follow.html',
                    userinfo=user)


class FollowerHandler(BaseHandler):

    def initialize(self):
        super(FollowerHandler, self).initialize()

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
        user['follow'] = user['follower']
        self.render('user/template/user-follow.html',
                    userinfo=user)


class FavoriteHandler(BaseHandler):

    def initialize(self):
        super(FavoriteHandler, self).initialize()
