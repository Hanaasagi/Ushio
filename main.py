# -*-coding:UTF-8-*-
import os
import sys
import yaml
from concurrent import futures
from ushio.urlmap import urlpattern
from uimodule import uimodule
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

setting = {
    'ui_modules': uimodule,
    'cookie_secret': '__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__',
    'config_file': './setting.yaml',
    'compress_response': True,
    # 'default_handler_class': controller.base.NotFoundHandler,
    'xsrf_cookies': True,
    'static_path': os.path.join(os.path.abspath('.'), "static"),
    'template_path': os.path.join(os.path.abspath('.'), 'app'),
    'login_url': '/login',
    'download': './download',
    'session': {
        'driver': 'redis',
        'driver_settings': {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'password': '',
            'max_connections': 1024,
        },
        'force_persistence': False,
        'cache_driver': True,
        'cookie_config': {
            'httponly': True
        }
    },
    'database': {
        'address': 'mongodb://localhost:27017/',
        'db': 'ushio',
    },
    'thread_pool': futures.ThreadPoolExecutor(4),
}

custom_setting = {}
try:
    with open(setting['config_file'], 'r') as f:
        custom_setting = yaml.load(f)
    for k, v in custom_setting.items():
        setting[k] = v
except:
    print 'can not load config file'
    sys.exit(0)


def run():
    define('port', default=8090, type=int, help='')
    define('debug', default=False, type=bool, help='')
    parse_command_line()
    setting['debug'] = options.debug
    if setting['debug']:
        print 'debug mode'

    try:
        client = MotorClient(setting['database']['address'])
        setting['connection'] = client[setting['database']['db']]
    except:
        print 'can not connect MongoDB'
        sys.exit(0)

    application = Application(
        handlers=urlpattern,
        **setting
    )

    http_server = HTTPServer(application, xheaders=True)
    http_server.listen(options.port)
    IOLoop.instance().start()


if __name__ == '__main__':
    run()
