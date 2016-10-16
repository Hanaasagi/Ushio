# -*-coding:UTF-8-*-
import re


class Model(object):
    '''
    example
    __rules__ = {
        'username': {
            'label': '用户名',
            '_need': True,
            'type': unicode,
            'max_length': 36,
            'min_length': 1,
            'pattern': ur'^[a-zA-Z0-9_\-\u4e00-\u9fa5]+$'
        }
    }
    '''

    def get_label(self):
        label_map = {}
        for k in self.__rules__:
            label_map[k] = self.__rules__[k]['label']
        return label_map

    def __call__(self, *args, **kwargs):
        data = args[0]
        for (k, value) in data.items():
            if k not in self.__rules__:
                continue
            if (not value) and ('required' not in self.__rules__[k]):
                continue
            for (field, limit) in self.__rules__[k].items():
                if field == '_label':
                    continue
                func = '_check_%s' % field
                if hasattr(self, func):
                    ret = getattr(self, func)(limit, value)
                    if not ret:
                        self.error_msg = self.__msg__[
                            field] % self.__rules__[k]['label']
                        return False
        return True

    def _check_type(self, valid, value):
        return type(value) is valid

    def _check_max_length(self, valid, value):
        return len(value) <= valid

    def _check_min_length(self, valid, value):
        return len(value) >= valid

    def _check_max(self, valid, value):
        return value <= valid

    def _check_min(self, valid, value):
        return value >= valid

    def _check_email(self, valid, value):
        return re.match(r'^(\w)+(\.\w+)*@(\w)+((\.\w+)+)$', value)

    def _check_number(self, valid, value):
        return re.match(r'^\d+$', value)

    def _check_url(self, valid, value):
        return value.startswith('http://') or value.startswith('https://')

    def _check_pattern(self, valid, value):
        return re.match(valid, value)
