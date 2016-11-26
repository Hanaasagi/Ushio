# -*-coding:UTF-8-*-

from app.message.handler import MessageHandler,MessageWebSocket

urlpattern = (
    (r'/message', MessageHandler),
    (r'/message/status', MessageWebSocket),
)
