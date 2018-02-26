import tornado


class Routers(object):
    _routers = []

    def __init__(self, url, name=None):
        self.url = url
        self.name = name

    def __call__(self, handler):
        name = self.name or handler.__class__
        self._routers.append(
            tornado.web.url(self.url, handler, name=name)
        )
        return handler

    @classmethod
    def get_routers(cls):
        return cls._routers
