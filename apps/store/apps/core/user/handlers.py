import bcrypt as bcrypt
import tornado.escape

from core.handlers import BaseHandler
from core.settings import SECURE_COOKIE_NAME
from core.user.models import User, AsyncOpUsers
from core.utils import Routers


@Routers("/auth/create", name="auth.create")
class AuthCreateHandler(BaseHandler):
    def initialize(self):
        self.user_model = AsyncOpUsers(self.db_session)

    def get(self):
        self.render("create_login.html")

    async def post(self):
        hashed_password = bcrypt.hashpw(
            tornado.escape.utf8(self.get_argument("password")),
            bcrypt.gensalt())
        user = User(name=self.get_argument("name"),
                     email=self.get_argument("email"),
                     password=hashed_password)

        fobj = self.user_model.create(user)
        await fobj.result()

        self.set_secure_cookie(SECURE_COOKIE_NAME, str(user.id))
        self.redirect("/")


@Routers("/auth/login", name="login")
class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html", error=None)

    async def post(self):
        session = self.db_session()
        user = session.query(User).filter(User.email == self.get_argument("email")).first()
        if not user:
            self.render("login.html", error="email not found")
            return
        hashed_password = bcrypt.hashpw(
            tornado.escape.utf8(self.get_argument("password")),
            tornado.escape.utf8(user.password))
        if hashed_password == user.password:
            self.set_secure_cookie(SECURE_COOKIE_NAME, str(user.id))
            self.redirect("/")
        else:
            self.render("login.html", error="incorrect password")


@Routers("/auth/logout")
class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie(SECURE_COOKIE_NAME)
        self.redirect("/")
