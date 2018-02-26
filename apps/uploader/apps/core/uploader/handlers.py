import logging
import traceback

import tornado.web

from core.settings import SECURE_COOKIE_NAME
from core.tasks import save_file_send_to_decomposer_service
from core.utils import Routers

logger = logging.getLogger(__name__)


class BaseHandler(tornado.web.RequestHandler):
    schema = None

    def write_error(self, status_code, **kwargs):
        self.set_header("Content-Type", 'application/json')

        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            self.set_header('Content-Type', 'text/plain')
            for line in traceback.format_exception(*kwargs["exc_info"]):
                self.write(line)
            self.finish()
        else:
            self.finish({
                "code": status_code,
                "message": self._reason
            })


@Routers("/")
class UploaderRoot(BaseHandler):

    async def get(self, *args, **kwargs):
        self.render("base.html")


@Routers("/upload")
class Upload(BaseHandler):
    accept_content_type = 'application/pdf'

    async def post(self, *args, **kwargs):
        filename = self.get_arguments("data.name")
        file_path = self.get_arguments("data.path")
        content_type = self.get_arguments("data.content_type")
        user_id = self.get_secure_cookie(SECURE_COOKIE_NAME)

        for p, f in [(p, f) for p, f, c in zip(file_path, filename, content_type)
                     if c == self.accept_content_type]:
            logging.warning("{}, {}, {}".format(p, f,  user_id))
            save_file_send_to_decomposer_service.delay(p, f, user_id.decode())
        self.redirect("/")
