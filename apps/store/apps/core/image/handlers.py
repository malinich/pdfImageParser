import logging
import uuid
from itertools import groupby

import tornado.websocket

from core.handlers import BaseHandler, login_required
from core.image.models import AsyncOpPdfImage
from core.image.serializers import PdfSchema, PdfImageSchema
from core.utils import Routers


@Routers("/", name="home")
class ImageList(BaseHandler):
    schema = PdfImageSchema(many=True)

    def initialize(self):
        self.pdf_model = AsyncOpPdfImage(self.db_session)

    @login_required
    async def get(self, *args, **kwargs):
        fobj = self.pdf_model.get_all()
        result = await fobj.result()
        # 0 because only one user can upload files, we take first of them
        data = self.jsonify(result)
        grouped = ((k, list(g)) for k,g in groupby(data['data'],
                                                   key=lambda d: d['pdf']['id']))
        self.render("main.html", items=grouped, count=data['count'])


@Routers("/notify", name="notify")
class ConvSocketNotify(BaseHandler):
    def post(self, *args, **kwargs):
        error = self.get_argument("error", None)
        count = self.get_argument("count", None)

        msg = {
            "count": count,
            "error": error
        }

        ConvSocketHandler.send_updates(msg)
        self.write("OK")


@Routers("/convsocket", name="conv_socket")
class ConvSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 200

    def check_origin(self, origin):
        return True

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        self.waiters.add(self)

    def on_close(self):
        self.waiters.remove(self)

    @classmethod
    def update_cache(cls, msg):
        cls.cache.append(msg)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    @classmethod
    def send_updates(cls, msg):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(msg)
            except:
                logging.error("Error sending message", exc_info=True)

    def on_message(self, message):
        logging.info("got message %r", message)

        chat = {
            "id": str(uuid.uuid4()),
            "body": message,
        }

        self.update_cache(chat)
        self.send_updates(chat)
