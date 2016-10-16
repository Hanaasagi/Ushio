# -*-coding:UTF-8-*-

from app.auth.handler import LoginHandler, RegisterHandler

urlpattern = (
    (r'/login', LoginHandler),
    (r'/register', RegisterHandler),
)
