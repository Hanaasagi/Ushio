# -*-coding:UTF-8-*-

import datetime
import tornado.web


class TimeSpan(tornado.web.UIModule):

    def render(self, time):
        delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(time)
        if delta.days >= 365:
            return '%d年前' % int(delta.days / 365)
        elif delta.days >= 30:
            return '%d个月前' % int(delta.days / 30)
        elif delta.days > 0:
            return '%d天前' % delta.days
        elif delta.seconds < 60:
            return "%d秒前" % delta.seconds
        elif delta.seconds < 60 * 60:
            return "%d分钟前" % int(delta.seconds / 60)
        else:
            return "%d小时前" % int(delta.seconds / 60 / 60)
