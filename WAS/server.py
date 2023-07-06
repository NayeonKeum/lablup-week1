import asyncio
import aiohttp
import aiohttp_cors
from datetime import datetime
from aiohttp import web
import redis.asyncio as redis
from aiohttp_session import get_session, setup, redis_storage
import os


async def _init(app):
    # DB init
    connection = await redis.from_url(os.environ["REDIS_ADDR"])
    app["connection"] = connection
    async with connection.pubsub() as pubsub:
        app["pubsub"] = pubsub
        storage = redis_storage.RedisStorage(connection, httponly=True)
        setup(app, storage)


class WebsocketHandler(web.View):
    async def post(self, ):
        data = await self.request.post()
        name = data.get("name")

        # Make redis connection with name
        await app["connection"].set(name, name+"-val")

        # Maintain session for global use
        global session
        session = await get_session(self.request)
        session["name"] = name
        session['last_visit'] = str(datetime.now())

        return web.Response(status=200, text="Success")


class ChatRoomHandler(web.View):
    async def get(self, ):
        # Maintained sessioin
        global session
        name = session["name"]

        # Create WebSocket
        ws = web.WebSocketResponse()
        app["websockets"].add(ws)
        await ws.prepare(self.request)

        # Get redis pubsub
        pubsub = app["pubsub"]
        await pubsub.psubscribe("lablup-chat")

        # Create tasks for redis and websocket
        redis_task = asyncio.create_task(handle_redis(pubsub))
        ws_task = asyncio.create_task(handle_ws(ws, name))

        # Intro
        await app["connection"].publish("lablup-chat", f"server: {name}님이 입장하셨습니다. 나가시려면 quit을 입력해주세요.")

        # Chatting(websocket) task
        await ws_task

        # Outro
        await app["connection"].publish("lablup-chat", f"server: {name}님이 퇴장하셨습니다.")

        # Discard websocket and redis tasks
        app["websockets"].discard(ws)
        await app["connection"].delete(name)
        redis_task.cancel()

        return ws


async def handle_ws(ws, name):
    async for msg in ws:
        # Closing message
        if msg.data == "quit":
            await ws.close()
        else:
            await app["connection"].publish("lablup-chat", f"{name}: {msg.data}")


async def handle_redis(pubsub):
    while True:
        msg_redis = await pubsub.get_message(ignore_subscribe_messages=True)
        if msg_redis:
            await broadcast(msg_redis["data"].decode())


async def broadcast(message):
    # Queue for broadcasting messages to websockets(fifo)
    websockets = asyncio.Queue()
    msgBody = {
        "content": f"{message}",
        "time": str(datetime.now()),
    }
    for websocket in app["websockets"]:
        await websockets.put(websocket)
    while not websockets.empty():
        ws = await websockets.get()
        await ws.send_json(msgBody)

if __name__ == "__main__":
    app = aiohttp.web.Application()
    app.on_startup.append(_init)

    app["websockets"] = set()

    app.router.add_routes([
        web.post('/', WebsocketHandler),
        web.get('/chat', ChatRoomHandler),
    ])

    # Add CORS for WEB Server
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    for route in list(app.router.routes()):
        cors.add(route)

    web.run_app(app, port=8080)
