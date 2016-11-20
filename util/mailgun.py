# -*-coding:UTF-8-*-
import requests


class Email(object):

    def __init__(self, setting):
        self.url = setting.get('url')
        self.key = setting.get('key')
        self.sender = setting.get('sender')

    def send(self, title, content, to, origin=None):
        origin = self.sender if not origin else origin
        url = '%s/messages' % self.url
        data = {
            'from': origin,
            'to': to,
            'subject': title,
            'text': content
        }
        # return requests.post(url, auth=('api', self.key), data=data)


if __name__ == '__main__':
    setting = {
        'key': 'key-',
        'method': 'none',
        'sender': 'root@domain',
        'url': 'https://api.mailgun.net/v3/'
    }
    Email(setting).send(
        title='test',
        to='ambiguous404@gmail.com',
        content='html content'
    )
