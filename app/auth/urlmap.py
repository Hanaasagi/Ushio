# -*-coding:UTF-8-*-

from app.auth.handler import LoginHandler,\
    RegisterHandler, LogoutHandler

urlpattern = (
    (r'/login', LoginHandler),
    (r'/register', RegisterHandler),
    (r'/logout', LogoutHandler),
)
