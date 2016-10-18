# -*-coding:UTF-8-*-

from __future__ import absolute_import

import random
from captcha.image import ImageCaptcha

#
# 去除易混淆的字符
#
_chars = 'ABCDEFGHJKMNPRSTWXYZ23456789'


class Captcha(object):

    _image = ImageCaptcha(fonts=['./static/assets/fonts/文泉驿微米黑全字符.ttf'])

    @staticmethod
    def get(request):
        chars = random.sample(_chars, 4)
        chars = ''.join(chars)
        request.session['captcha'] = chars
        return Captcha._image.generate(chars)

    @staticmethod
    def verify(captcha, request):
        #
        # 暂不开启,方便调试
        #
        return True

        # chars = request.session.get('captcha', '')
        # if chars:
        #     request.session.delete('captcha')
        #     if captcha == chars:
        #         return True
        #     return False
