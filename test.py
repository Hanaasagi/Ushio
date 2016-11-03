import tornado.web
import tornado.httpserver
import tornado.ioloop
from torndsession.sessionhandler import SessionBaseHandler


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/", MainHandler),
        ]
        settings = dict(
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(SessionBaseHandler):

    def get(self):
        self.write("Hello, Session.<br/>")
        if 'data' in self.session:
            data = self.session['data']
        else:
            data = 0
        self.write('data=%s' % data)
        self.session["data"] = data + 1


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
