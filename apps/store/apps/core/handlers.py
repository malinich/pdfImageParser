import traceback

import tornado.web
from core.settings import SECURE_COOKIE_NAME
from core.user.models import User


def login_required(func):
    async def wrap(self, *args, **kwargs):
        if not self.current_user:
            self.redirect("/auth/login")
            return
        await func(self, *args, **kwargs)
    return wrap


class BaseHandler(tornado.web.RequestHandler):
    schema = None

    def get_current_user(self):
        session = self.db_session()

        user_id = self.get_secure_cookie(SECURE_COOKIE_NAME)
        if not (user_id and user_id.isdigit()):
            return None
        user = session.query(User).filter(User.id == int(user_id)).first()
        return user

    @property
    def db_session(self):
        return self.application.session

    def on_finish(self):
        self.db_session.close()

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

    def jsonify(self, images):

        data = {
            "count": len(images),
            "data": self.schema.dump(images).data
        }
        return data


