# -*-coding:UTF-8-*-

from app.auth.handler import LoginHandler,\
    RegisterHandler, LogoutHandler, ForgetPasswordHandler

urlpattern = (
    (r'/login', LoginHandler),
    (r'/register', RegisterHandler),
    (r'/logout', LogoutHandler),
    (r'/forgetpassword', ForgetPasswordHandler),
)
