# -*-coding:UTF-8-*-

from app.admin.handler import AdminIndexHandler,\
    AdminSettingHandler,\
    AdminUserListHandler, \
    AdminColumnHandler,\
    AdminUserUpdateHandler,\
    AdminTagAddHandler,\
    AdminTagDelHandler

urlpattern = (
    (r'/ushio/index', AdminIndexHandler),
    (r'/ushio/setting', AdminSettingHandler),
    (r'/ushio/users', AdminUserListHandler),
    (r'/ushio/columns', AdminColumnHandler),
    (r'/ushio/user/(\w+)', AdminUserUpdateHandler),
    (r'/ushio/tag/add', AdminTagAddHandler),
    (r'/ushio/tag/del', AdminTagDelHandler),
)
