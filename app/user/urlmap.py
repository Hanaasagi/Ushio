# -*-coding:UTF-8-*-

from app.user.handler import ProfileHandler,\
    UpdateHandler,\
    DeleteHandler,\
    FollowHandler,\
    FollowerHandler,\
    FollowingHandler,\
    FavoriteHandler

urlpattern = (
    (r'/user/update', UpdateHandler),
    (r'/user/delete', DeleteHandler),
    (r'/user/follow/(\w+)', FollowHandler),
    (r'/user/(\w+)', ProfileHandler),
    (r'/user/(\w+)/follower', FollowerHandler),
    (r'/user/(\w+)/following', FollowingHandler),
    (r'/user/(\w+)/favorite', FavoriteHandler),
)
