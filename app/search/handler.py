# -*-coding:UTF-8-*-
import re
import pymongo
import tornado.web
import tornado.gen
from ushio._base import BaseHandler


class SearchHandler(BaseHandler):

    def initialize(self):
        super(SearchHandler, self).initialize()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        keyword = self.get_query_argument('keyword', '')
        if not keyword:
            self.custom_error('关键词不能为空')
        keyword = '.*{}.*'.format(re.escape(keyword))
        limit = 20
        page = int(self.get_query_argument('page', default=1))
        page = 1 if page <= 0 else page
        cursor = self.db.topic.find({
            'title': {'$regex': keyword, '$options': 'i'}
        })
        count = yield cursor.count()
        cursor.sort([('time', pymongo.DESCENDING)]).limit(
            limit).skip((page - 1) * limit)
        posts = yield cursor.to_list(length=limit)
        self.render('search.html', posts=posts, page=page, keyword=keyword,
                    count=count, each=limit)
