# -*-coding:UTF-8-*-


class cache(dict):

    def __init__(self, request):
        dict.__init__(self)
        self.request = request

    def __getitem__(self, item):
        item = 'cache_%s' % item
        if item in self.request.session:
            value = self.request.session.get(item)
            self.request.session.delete(item)
        else:
            value = None
        return value

    def get(self, k, d=None):
        return self.__getitem__(k)

    def __delattr__(self, item):
        item = 'cache_%s' % item
        self.request.session.delete(item)

    def __setitem__(self, key, value):
        key = 'cache_%s' % key
        self.request.session[key] = value
