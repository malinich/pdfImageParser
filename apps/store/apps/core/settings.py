import os.path
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

APPS = [
    'user',
    'image',
]
BASE_DIR = os.path.dirname(__file__)

SECURE_COOKIE_NAME = "user"

SECRET_COOKIE = "d41d8cd98f00b204e9800998ecf8427e"

MEDIA_PREFIX = "/media"

TORNADO_SETTINGS = {
    "title": "PDF converter to image",
    "template_path":  os.path.join(BASE_DIR, "templates"),
    "cookie_secret": SECRET_COOKIE,
    "static_path": os.path.join(BASE_DIR, "static"),
}

eng = create_engine('sqlite:////tmp/db.db', connect_args={'check_same_thread': False},
                    poolclass=StaticPool)
