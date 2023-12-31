import asyncio
from asyncio import CancelledError
from aiohttp import web
import aiohttp_cors
from aiohttp_session import redis_storage, setup, get_session
import redis.asyncio as redis
from datetime import datetime
import os


async def init_all(app):
    # 1. WebSocket set init
    app["websockets"] = set()
    # 2. Web init
    app = _init_web(app)
    # 3. DB connection init
    app = await _init_db(app)


def _init_web(app):
    # Add routers
    app.router.add_routes([
        web.post('/', InitHandler),
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
    return app


async def _init_db(app):
    redis_conn = await redis.from_url(os.environ["REDIS_ADDR"])
    app["redis_conn"] = redis_conn

    # Init pubsub
    pubsub = redis_conn.pubsub()
    await pubsub.psubscribe("lablup-chat")
    app["pubsub"] = pubsub

    # Setup storage for session
    storage = redis_storage.RedisStorage(redis_conn)
    setup(app, storage)
    return app


async def dispose_all(app):
    # WebSocket close tasks
    tasks = [ws.close() for ws in app["websockets"]]
    try:
        await asyncio.gather(*tasks)
    except CancelledError:
        print("Disposing websocket task cancel detected.")
        raise
    # DB connection dispose
    await app["redis_conn"].close()


class InitHandler(web.View):
    async def post(self, ):
        # Name init(from request body)
        data = await self.request.post()
        name = data.get("name")

        # Make redis connection with name
        await app["redis_conn"].set(name, "connected")

        # Get session from primary request
        session = await get_session(self.request)
        session["name"] = name
        session['last_visit'] = str(datetime.now())

        # Maintain session for later use
        app["session"] = session

        return web.Response(status=200, text="Success")


class ChatRoomHandler(web.View):
    async def get(self, ):
        # Get maintained session
        session = app["session"]
        name = session["name"]

        # Create WebSocket
        ws = web.WebSocketResponse()
        app["websockets"].add(ws)
        await ws.prepare(self.request)

        # Get redis pubsub
        pubsub = app["pubsub"]

        # Create tasks for redis and websocket
        redis_task = asyncio.create_task(handle_redis(pubsub))
        ws_task = asyncio.create_task(handle_ws(ws, name))

        # Intro
        await app["redis_conn"].publish("lablup-chat", f"server: {name}님이 입장하셨습니다.")

        # Chatting(websocket) task
        try:
            await ws_task
        except CancelledError:
            print("WebSocket task cancel detected.")
            raise

        # Discard websocket and redis task
        app["websockets"].discard(ws)
        await app["redis_conn"].delete(name)
        redis_task.cancel()

        return ws


async def handle_redis(pubsub):
    while True:
        msg_redis = await pubsub.get_message(ignore_subscribe_messages=True)
        if msg_redis:
            await broadcast(msg_redis["data"].decode())


async def handle_ws(ws, name):
    async for msg in ws:
        # Closing message
        if msg.data == "quit":
            # Outro
            await app["redis_conn"].publish("lablup-chat", f"server: {name}님이 퇴장하셨습니다.")
            await ws.close()
        else:
            await app["redis_conn"].publish("lablup-chat", f"{name}: {msg.data}")


async def broadcast(message):
    # Broadcasting messages to websockets
    msgBody = {
        "content": f"{message}",
        "time": str(datetime.now()),
    }
    # Gather all ws tasks and execute at once
    tasks = [ws.send_json(msgBody) for ws in app["websockets"]]
    try:
        await asyncio.gather(*tasks)
    except CancelledError:
        print("Broadcasting task cancel detected.")
        raise


if __name__ == "__main__":
    app = web.Application()

    app.on_startup.append(init_all)
    app.on_shutdown.append(dispose_all)

    web.run_app(app, port=8080)
