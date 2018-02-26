import os.path
import sys
parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent)

import asyncio

import tornado.platform.asyncio
from sqlalchemy.orm import sessionmaker, scoped_session
from tornado.web import Application

from core.settings import TORNADO_SETTINGS, APPS, eng
from core.utils import Routers


class UploadApplication(Application):

    def __init__(self):
        self.initialize_db()
        self.register_models()
        handlers = self.register_handlers()
        super(UploadApplication, self).__init__(handlers,
                                                **TORNADO_SETTINGS)

    def register_models(self):
        for app_path in APPS:
            __import__(app_path, globals(), locals(), ['models'])

    def register_handlers(self):
        for app_path in APPS:
            __import__(app_path, globals(), locals(), ['handlers'])
        return Routers.get_routers()

    def initialize_db(self):
        self.session = scoped_session(sessionmaker(bind=eng))


def main():
    return UploadApplication()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = main()
    tornado.platform.asyncio.AsyncIOMainLoop().install()
    app.listen(3000)
    asyncio.get_event_loop().run_forever()