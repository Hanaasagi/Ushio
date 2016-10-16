# -*-coding:UTF-8-*-

from app.captcha.handler import CaptchaHanlder

urlpattern = (
    (r'^/captcha\.png', CaptchaHanlder),
)
