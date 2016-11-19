# -*-coding:UTF-8-*-

from app.topic.handler import TopicHandler, HomeHandler, \
    TagHandler, TopicNewHandler, TopicUpdateHandler,\
    TopicLikeHandler

urlpattern = (
    (r'/', HomeHandler),
    (r'/topics/new', TopicNewHandler),
    # 匹配 url 编码的中文
    (r'/tag/([%a-fA-F0-9]+)', TagHandler),
    (r'/topics/(\w+)', TopicHandler),
    (r'/topics/update/(\w+)', TopicUpdateHandler),
    (r'/favorite', TopicLikeHandler),
)
