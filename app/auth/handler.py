# -*-coding:UTF-8-*-
import time
import json
import re
import uuid
import tornado.web
import tornado.gen
from hashlib import md5
from util.captcha import Captcha
from util.util import Cipher
from util.mailgun import Email
from ushio._base import BaseHandler
from tornado.escape import url_escape


class RegisterHandler(BaseHandler):

    def initialize(self):
        super(RegisterHandler, self).initialize()

    def prepare(self):
        super(RegisterHandler, self).prepare()
        self.error_map = {
            'email_wrong': 'email格式错误',
            'passworddiff': '两次输入的密码不相同',
            'userexisted': '用户已经被注册',
            'passwordshort': '密码长度不能少于6个字符',
            'invite_wrong': '邀请码错误或不存在',
            'invite_expire': '邀请码已过期',
            'closed': '网站已关闭注册',
            'captcha_wrong': '验证码错误',
        }

    def get(self):
        '''
            显示注册页面 错误信息
        '''
        if self.get_current_user():
            self.redirect('/')
        token = self.get_query_argument('token', None)

        if not token:
            error = self.get_query_argument('error', '')
            error_msg = self.error_map.get(error, '')
            self.render('auth/template/register.html',
                        error=error_msg, cache=self.cache['user_reg'] or {})
        else:
            #
            # 若 url 中存在 + %2B 则会获得空格 ??
            #
            token = token.replace(' ', '+')
            msg = Cipher(self.settings['cookie_secret']).decrypt(token)
            if self.cache['token'] == msg:
                user = self.cache['user_info']
                result = self.db.user.insert(user)
                if not result:
                    self.send_error(status_code=500)
                self.cache['user_reg'] = None
                self.redirect('/login?next=/user/update')
            else:
                self.write('验证失败 请重新注册')

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        '''
            处理用户注册信息
        '''
        username = self.get_body_argument('username', '')
        email = self.get_body_argument('email', '')
        password = self.get_body_argument('password', '')
        repassword = self.get_body_argument('repassword', '')
        captcha = self.get_body_argument('captcha', '')
        self.cache['user_reg'] = {
            'username': username,
            'email': email,
            'password': password
        }
        # 验证逻辑
        if not re.match(r'^(\w)+(\.\w+)*@(\w)+((\.\w+)+)$', email):
            self.redirect('/register?error=email_wrong')
            return
        if not Captcha.verify(captcha, self):
            self.redirect('/register?error=captcha_wrong')
            return
        if self.settings['reg_type'] == 'close':
            self.redirect('/register?error=closed')
            return
        if self.settings['reg_type'] == 'invite':
            invitecode = self.get_body_argument('invitecode', '')
            record = yield self.db.invite.find_one({
                'code': {
                    '$eq': invitecode
                },
                'used': {
                    '$eq': False
                }
            })
            if not record:
                self.redirect('/register?error=invite_wrong')
                return
            elif time.time() - record['time'] > self.settings['invite_expire_time']:
                yield self.db.invite.remove({'code': invitecode})
                self.redirect('/register?error=invite_expire')
                return

        if len(password) < 6:
            self.redirect('/register?error=passwordshort')
            return
        if password != repassword:
            self.redirect('/register?error=passworddiff')
            return
        user = yield self.db.user.find_one({'$or': [{'username': username}, {'email': email}]})
        if user:
            self.redirect('/register?error=userexisted')
            return

        hash_object = md5(password + self.settings['salt'])
        password = hash_object.hexdigest()
        user = {
            'username': username,
            'password': password,
            'money': self.settings['init_money'],
            'register_time': time.time(),
            'favorite': [],
            'email': email,
            'level': 1,
            'qq': '',
            'website': '',
            'address': '',
            'signal': u'这个人太懒，还没有留下任何东西',
            'openemail': 1,
            'openfavorite': 1,
            'openqq': 1,
            'allowemail': 1,
            'logintime': None,
            'loginip': self.request.remote_ip
        }

        if self.settings['reg_type'] == 'invite':
            record['used'] = True
            record['user'] = username
            yield self.db.invite.update({
                'code': invitecode
            }, record
            )

        self.cache['user_info'] = user
        msg = '{}{}'.format(uuid.uuid4(), time.time())
        self.cache['token'] = msg
        token = Cipher(self.settings['cookie_secret']).encrypt(msg)
        url = '{}/register?token={}'.format(
            self.settings['site_url'], url_escape(token)
        )
        Email(self.settings['email']).send(
            to=user['email'],
            origin='',
            title=u'注册 - %s' % self.settings['site']['name'],
            content=u'点击链接完成注册：<br /><a href=\"%s\">%s</a><br />如果不是您本人操作，请忽视这封邮件' % (
                url, url)
        )
        self.write('我们已经发送了一封邮件到{0}，请及时确认'.format(user['email']))
        self.finish()


class LoginHandler(BaseHandler):

    def initialize(self):
        super(LoginHandler, self).initialize()

    def prepare(self):
        super(LoginHandler, self).initialize()
        self.error_map = {
            'verify_wrong': '用户名或密码错误',
            'captcha_wrong': '验证码错误'
        }

    def get(self):
        if self.get_current_user():
            self.redirect('/')
            return
        error = self.get_argument('error', '')
        error_msg = self.error_map.get(error, '')
        next_to = self.get_query_argument('next', '')
        self.render('auth/template/login.html', error=error_msg, next=next_to)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        username = self.get_body_argument('username', '')
        password = self.get_body_argument('password', '')
        captcha = self.get_body_argument('captcha', '')
        remember = self.get_body_argument('remember', False)

        if not Captcha.verify(captcha, self):
            self.redirect('/login?error=captcha_wrong')
            return
        user = yield self.db.user.find_one({
            'username': username
        })
        # 对密码进行验证 util.function
        hash_object = md5(password + self.settings['salt'])
        if user and user['password'] == hash_object.hexdigest():
            cookie = json.dumps(self.set_session(user))
            if remember:
                self.set_secure_cookie(
                    'TORNADOSESSION', cookie, expires_days=30)
            else:
                self.set_secure_cookie(
                    'TORNADOSESSION', cookie, expires_days=1)
            yield self.db.user.find_and_modify({
                'username': username
            }, {
                '$set': {
                    'logintime': time.time(),
                    'loginip': self.request.remote_ip
                }
            })
            self.redirect(self.get_query_argument('next', '/'))
            return
        else:
            self.redirect('login?error=verify_wrong')
            return


class LogoutHandler(BaseHandler):

    def initialize(self):
        super(LogoutHandler, self).initialize()

    def prepare(self):
        super(LogoutHandler, self).prepare()

    def get(self):
        if self.get_cookie('TORNADOSESSION'):
            self.clear_cookie('TORNADOSESSION')
        self.session.delete('user_session')
        self.redirect('/')


class ForgetPasswordHandler(BaseHandler):

    def initialize(self):
        super(ForgetPasswordHandler, self).initialize()

    def prepare(self):
        super(ForgetPasswordHandler, self).prepare()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        token = self.get_argument('token', None)
        if token:
            try:
                token = token.replace(' ', '+')
                msg = Cipher(self.settings['cookie_secret']).decrypt(token)
            except:
                self.send_error(status_code=500)
            # Why need password
            #
            #
            username, password, t = msg.split('|')
            if time.time() - float(t) > 30 * 60:
                error = '链接已过期，请在30分钟内点击链接找回密码'
                self.redirect('')
            user = yield self.db.user.find_one({
                'username': username,
                'password': password
            })
            if user:
                self.render('auth/template/forget-password.html',
                            step=2, token=token)
            else:
                self.send_error(status_code=500)
        else:
            # self.redirct ?
            self.render('auth/template/forget-password.html', step=1)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        '''
            step 1 用户填写邮箱账号，发送重置密码的链接
            step 2 用户填写新密码，进行密码重置
        '''
        step = self.get_query_argument('step', '1')
        if step == '1':
            username = self.get_body_argument('username', None)
            if username:
                captcha = self.get_body_argument('captcha', '')
                if not Captcha.verify(captcha, self):
                    self.custom_error('验证码错误')
                user = yield self.db.user.find_one({
                    'username': username
                })
                if not user:
                    self.custom_error('用户不存在')
                msg = '{}|{}|{}'.format(
                    user['username'], user['password'], time.time()
                )
                token = Cipher(self.settings['cookie_secret']).encrypt(msg)
                url = '{}/forgetpassword?token={}'.format(
                    self.settings['site_url'], url_escape(token)
                )
                Email(self.settings['email']).send(
                    to=user['email'],
                    origin='',
                    title=u'找回密码 - %s' % self.settings['site']['name'],
                    content=u'点击链接找回你的密码：<br /><a href=\"%s\">%s</a><br />如果不是您本人操作，请忽视这封邮件' % (
                        url, url)
                )
                self.write('一封重置密码的邮件已经发送到您的邮箱，请注意查收')
                self.finish()
            else:
                self.custom_error('require username')
        if step == '2':
            token = self.get_body_argument('token', None)
            newpwd = self.get_body_argument('password', None)
            if token and newpwd:
                try:
                    token = token.replace(' ', '+')
                    msg = Cipher(self.settings['cookie_secret']).decrypt(token)
                    username, password, t = msg.split('|')
                except:
                    self.send_error(status_code=500)
                if time.time() - float(t) > 30 * 60:
                    error = '链接已过期，请在30分钟内点击链接找回密码'
                    self.custom_error(error)
                hash_object = md5(newpwd + self.settings['salt'])
                print username, password
                user = yield self.db.user.find_and_modify({
                    'username': username,
                    'password': password
                }, {
                    '$set': {'password': hash_object.hexdigest()}
                })
                if user:
                    self.redirect('/login')
                else:
                    # print '12' * 100
                    self.custom_error('参数错误')
            else:
                self.custom_error('非法访问')
        else:
            self.custom_error()
