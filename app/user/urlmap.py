# -*-coding:UTF-8-*-

from app.user.handler import ProfileHandler, UpdateHandler

urlpattern = (
    (r'/user/update', UpdateHandler),
    (r'/user/(\w+)', ProfileHandler),
)
