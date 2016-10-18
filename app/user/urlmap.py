# -*-coding:UTF-8-*-

from app.user.handler import ProfileHandler, UpdateHandler, DeleteHandler

urlpattern = (
    (r'/user/update', UpdateHandler),
    (r'/user/delete', DeleteHandler),
    (r'/user/(\w+)', ProfileHandler),
)
