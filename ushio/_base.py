# -*-coding:UTF-8-*-
import time
import json
import tornado.web
import tornado.gen
# from util.email import Email
from torndsession.sessionhandler import SessionBaseHandler
from util.cache import Cache


class BaseHandler(SessionBaseHandler):

    def initialize(self):
        self.db = self.settings['connection']
        self.upload_path = self.settings['upload_path']
        self.backend = self.settings.get('thread_pool')
        self.cache = Cache(self)
        self.redis_conn = self.settings['redis_conn']

    def render(self, template_name, **kwargs):
        super(BaseHandler, self).render(template_name,
                                        site_base=self.settings['site'], **kwargs)

    def custom_error(self, *args, **kwargs):
        if not self._finished:
            status_code = kwargs.get('status_code', 200)
            self.set_status(status_code)
            title = kwargs.get('title', '提示信息')
            msg = kwargs.get('msg', '')
            status = kwargs.get('status', 'warning')
            next_to = kwargs.get('next_to', '#')
            self.render('error.html', info=msg, title=title,
                        status=status, next=next_to)
        raise tornado.web.Finish()

    def set_session(self, user):
        if '_id' in user and 'username' in user:
            session = {
                '_id': str(user['_id']),
                'username': user['username'],
                'level': user['level'],
                'money': user['money'],
                # 'msg_num':len(user['msg'])
                'login_time': time.time()
            }
            self.session.set('user_session', session)
            return session
        else:
            return None

    def get_current_user(self):
        try:
            user = self.session.get('user_session')
            if not user and self.get_cookie('TORNADOSESSION'):
                scookie = self.get_secure_cookie('TORNADOSESSION')
                user = json.loads(scookie)
                if not self.set_session(user):
                    assert False
        except:
            user = None
        return user
