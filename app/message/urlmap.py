# -*-coding:UTF-8-*-

from app.message.handler import MessageHandler

urlpattern = (
    (r'/message', MessageHandler),
)
