import os.path
import sys
parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent)

import asyncio
import tornado.web

from core.decompose import Decomposer
from core.publisher import Publisher
from core.settings import STORE_PATH


class ParserApplication(tornado.web.Application):
    def __init__(self, decomposer):
        self.decomposer = decomposer
        super(ParserApplication, self).__init__(self.get_handlers())

    def get_handlers(self):
        handlers = [
            (r"/", MainHandler),
            (r"/error", MainHandler),
        ]
        return handlers


class ErroorHandler(tornado.web.RequestHandler):
    async def post(self, *args, **kwargs):
        error = self.get_argument("error")
        self.application.decomposer.publish_service.publish({"error": error})


class MainHandler(tornado.web.RequestHandler):
    async def post(self, *args, **kwargs):
        file_path = self.get_argument("file_path")
        filename = self.get_argument("filename")
        user_id = self.get_argument("user_id")
        await self.application.decomposer.decompose_pdf_onto_images(file_path,
                                                                    filename,
                                                                    user_id)


def make_app():
    return ParserApplication(Decomposer(publisher, STORE_PATH))


if __name__ == "__main__":
    publisher = Publisher()
    app = make_app()
    tornado.platform.asyncio.AsyncIOMainLoop().install()
    app.listen(3003)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(publisher.connect())
    loop.run_forever()
