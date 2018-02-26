import os.path
from sqlalchemy import create_engine
from celery import Celery

APPS = [
    'uploader'
]

BASE_DIR = os.path.dirname(__file__)

TEMPLATE_PATH = os.path.join(BASE_DIR, "templates")

STATIC_PATH = os.path.join(BASE_DIR, "static")

STORE_PATH = "/tmp/media"

SECURE_COOKIE_NAME = "user"

SECRET_COOKIE = "d41d8cd98f00b204e9800998ecf8427e"

TORNADO_SETTINGS = {
    "cookie_secret": SECRET_COOKIE,
    "static_path": STATIC_PATH,
    "template_path": TEMPLATE_PATH
}

c_app = Celery('converter',
               backend='redis://127.0.0.1',
               broker='amqp://guest@127.0.0.1//',
               CELERY_TRACK_STARTED=True, include=['core.tasks'])

eng = create_engine('sqlite:////tmp/db.db')

NOTIFY_SERVICE = "http://127.0.0.1:3003"
NOTIFY_SERVICE_ERROR = "http://127.0.0.1:3001/notify"
# import tasks
# from core.tasks import *
