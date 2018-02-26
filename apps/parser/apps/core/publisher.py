import json

import aioamqp
import logging

from core.settings import AIOAMQP_HOST

logger = logging.getLogger(__name__)


class Publisher:
    host = AIOAMQP_HOST
    port = 5672
    ex_name = "pdf"
    routing_key = "pdf"

    async def connect(self):
        self.transport, self.protocol = await aioamqp.connect(self.host, self.port)
        self.channel = await self.protocol.channel()
        await self.channel.exchange(self.ex_name, "direct")

    async def publish(self, message):
        await self.channel.publish(json.dumps(message),
                                   exchange_name=self.ex_name, routing_key=self.routing_key)

    async def close(self):
        await self.protocol.close()
        self.transport.close()
