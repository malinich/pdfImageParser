import os.path
import sys
parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent)

import asyncio
import json
import logging
import os.path
from functools import partial

import aioamqp
import requests
from sqlalchemy.orm import sessionmaker

from core.image.models import Pdfs, PdfImages
from core.settings import eng, MEDIA_PREFIX

logger = logging.getLogger(__name__)


class Subscriber:
    host = "127.0.0.1"
    port = 5672
    ex_name = "pdf"
    routing_key = "pdf"
    notify_service = "http://127.0.0.1:3001/notify"

    async def initialize(self):
        Session = sessionmaker(eng)
        self.session = Session()

    async def connect(self):
        self.transport, self.protocol = await aioamqp.connect(self.host, self.port)
        self.channel = await self.protocol.channel()
        await self.channel.exchange(self.ex_name, "direct")

        self.queue = await self.channel.queue(queue_name='')
        self.queue_name = self.queue['queue']
        await self.channel.queue_bind(exchange_name=self.ex_name,
                                      queue_name=self.queue_name,
                                      routing_key=self.routing_key)

    async def subscribe(self, waiter: asyncio.Event):
        await asyncio.wait_for(
            self.channel.basic_consume(self.receive_image_event,
                                       queue_name=self.queue_name), timeout=10)
        await waiter.wait()

    async def receive_image_event(self, channel, body, envelope, properties):
        path_func = partial(os.path.join, MEDIA_PREFIX)
        data = json.loads(body)
        pdf = Pdfs(
            name=data['filename'],
            path=path_func(os.path.basename(data['file_path'])),
            user_id=int(data['user_id']))
        pdf_images = [PdfImages(
            image=path_func(os.path.basename(image_path))) for image_path in data['images']]
        pdf.images = pdf_images

        self.session.add(pdf)
        self.session.commit()
        print("consumer {} received {} ({})".format(envelope.consumer_tag, body, envelope.delivery_tag))
        r = requests.post(self.notify_service, {"count": len(pdf_images)})
        print(r.text)


if __name__ == '__main__':
    subscriber = Subscriber()
    waiter = asyncio.Event()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(subscriber.initialize())
    loop.run_until_complete(subscriber.connect())
    loop.run_until_complete(subscriber.subscribe(waiter))
