# -*-coding:UTF-8-*-

from app.topic.handler import TopicHandler, HomeHandler, \
    NodeHandler, TopicNewHandler, TopicUpdateHandler

urlpattern = (
    (r'/', HomeHandler),
    (r'/topics/new', TopicNewHandler),
    (r'/node/(\w+)', NodeHandler),
    (r'/topics/(\w+)', TopicHandler),
    (r'/topics/update/(\w+)', TopicUpdateHandler),
)
