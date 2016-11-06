# -*- coding: utf-8 -*-
import app.user.urlmap
import app.topic.urlmap
import app.auth.urlmap
import app.admin.urlmap
import app.captcha.urlmap
import app.comment.urlmap
import app.search.urlmap

urlpattern = ()

urlpattern += app.user.urlmap.urlpattern
urlpattern += app.topic.urlmap.urlpattern
urlpattern += app.auth.urlmap.urlpattern
urlpattern += app.admin.urlmap.urlpattern
urlpattern += app.captcha.urlmap.urlpattern
urlpattern += app.comment.urlmap.urlpattern
urlpattern += app.search.urlmap.urlpattern
