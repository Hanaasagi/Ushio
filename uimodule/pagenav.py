# -*-coding:UTF-8-*-

import tornado.web


class PageNav(tornado.web.UIModule):

    def render(self, url, total, limit, now):
        pre='<ul class="am-pagination am-fr admin-content-pagination">'
        end='</ul>'
        html = ''
        span = 5
        if total % limit == 0:
            page = total / limit
        else:
            page = int((total / limit) + 1)

        i = now - 5
        if i < 0:
            span = abs(i) + span + 1
            i = 1
        while (i <= now + span) and (i <= page):
            if now == i:
                html += '<li class="am-active"><a class="am-link-muted" href="">{0}</a></li>'.format(
                    i)
            else:
                html += '<li><a class="am-link-muted" href="{0}?page={1}">{2}</a></li>'.format(
                    url, i, i)
            i += 1

        if now > span + 1:
            html = u'<li><a class="am-link-muted" href="{0}?page=1">首页</a></li><li class="am-disabled"><a href="#">...</a></li>{1}'.format(
                url, html)
        if now + span < page:
            html = u'{0}<li class="am-disabled"><a href="#">...</a></li><li><a class="am-link-muted" href="{1}?page={2}">尾页</a></li>'.format(
                html, url, page)
        # if page <= 1:
        #     html = ''
        html = pre + html + end
        return html
