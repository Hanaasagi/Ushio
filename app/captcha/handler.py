# -*-coding:UTF-8-*-
from ushio._base import BaseHandler
from util.captcha import Captcha


class CaptchaHanlder(BaseHandler):

    def initialize(self):
        super(CaptchaHanlder, self).initialize()

    def prepare(self):
        super(CaptchaHanlder, self).prepare()

    def get(self):
        self.set_header("Content-Type", "image/png")
        img = Captcha.get(self)
        self.write(img.getvalue())
