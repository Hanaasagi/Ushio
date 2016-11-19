# -*-coding:UTF-8-*-
import os
import sys
import yaml
from concurrent import futures
from ushio.urlmap import urlpattern
from uimodule.timespan import TimeSpan
from uimodule.pagenav import PageNav
from motor.motor_tornado import MotorClient
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.web import Application
from tornado.options import define, options, parse_command_line


banner = r'''
   __  __       __     _      
  / / / /_____ / /_   (_)____ 
 / / / // ___// __ \ / // __ \
/ /_/ /(__  )/ / / // // /_/ /
\____//____//_/ /_//_/ \____/ 
                              
'''

print banner

settings = {
    'ui_modules': {'timespan': TimeSpan, 'pagenav': PageNav},
    'cookie_secret': '__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__',
    'config_file': './setting.yaml',
    'compress_response': True,
    # 'default_handler_class': controller.base.NotFoundHandler,
    'xsrf_cookies': True,
    'static_path': os.path.join(os.path.abspath('.'), "static"),
    'template_path': os.path.join(os.path.abspath('.'), 'app'),
    'login_url': '/login',
    'download': './download',
    'thread_pool': futures.ThreadPoolExecutor(4),
    'upload_path': os.path.join(os.path.dirname(__file__), 'static/img/avatar/'),
}

custom_setting = {}
try:
    with open(settings['config_file'], 'r') as f:
        custom_setting = yaml.load(f)
    for k, v in custom_setting.items():
        if k == 'global':
            settings.update(custom_setting[k])
        else:
            settings[k] = v
except Exception, e:
    print 'can not load config file', e
    sys.exit(0)


def run():
    define('port', default=8090, type=int, help='')
    define('debug', default=False, type=bool, help='')
    parse_command_line()
    settings['debug'] = options.debug
    if settings['debug']:
        print 'debug mode'

    try:
        client = MotorClient(settings['database']['address'])
        settings['connection'] = client[settings['database']['db']]
    except:
        print 'can not connect MongoDB'
        sys.exit(0)

    application = Application(
        handlers=urlpattern,
        **settings
    )

    http_server = HTTPServer(application, xheaders=True)
    http_server.listen(options.port)
    IOLoop.instance().start()


if __name__ == '__main__':
    run()
