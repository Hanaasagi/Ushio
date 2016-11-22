# -*-coding:UTF-8-*-

from app.user.handler import ProfileHandler,\
    UpdateHandler,\
    DeleteHandler,\
    FollowHandler

urlpattern = (
    (r'/user/update', UpdateHandler),
    (r'/user/delete', DeleteHandler),
    (r'/user/follow/(\w+)', FollowHandler),
    (r'/user/(\w+)', ProfileHandler),
)
