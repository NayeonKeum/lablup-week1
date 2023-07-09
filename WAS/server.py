import asyncio
import aiohttp
import aiohttp_cors
from datetime import datetime
from aiohttp import web
import redis.asyncio as redis
from aiohttp_session import redis_storage, setup, get_session
import os


async def init_all(app):
    # 1.WebSocket set init
    app["websockets"] = set()
    # 2. Web init
    app = _init_web(app)
    # 3. DB connection init
    app = await _init_db(app)


def _init_web(app):
    # Add routers
    app.router.add_routes([
        web.post('/', WebSocketHandler),
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
    async with redis_conn.pubsub() as pubsub:
        app["pubsub"] = pubsub
        storage = redis_storage.RedisStorage(redis_conn)
        setup(app, storage)
        return app


async def dispose_all(app):
    # WebSocket close tasks
    tasks = [ws.close() for ws in app["websockets"]]
    await asyncio.gather(*tasks)
    # DB connection dispose
    await app["redis_conn"].close()


class WebSocketHandler(web.View):
    async def post(self, ):
        data = await self.request.post()
        name = data.get("name")

        # Make redis connection with name
        await app["redis_conn"].set(name, name+"-val")

        # Maintain session for global use
        global session
        session = await get_session(self.request)
        session["name"] = name
        session['last_visit'] = str(datetime.now())

        return web.Response(status=200, text="Success")


class ChatRoomHandler(web.View):
    async def get(self, ):
        # Get maintained session
        global session
        name = session["name"]

        # Create WebSocket
        ws = web.WebSocketResponse()
        app["websockets"].add(ws)
        await ws.prepare(self.request)

        # Get redis pubsub & subscribe
        pubsub = app["pubsub"]
        await pubsub.psubscribe("lablup-chat")

        # Create tasks for redis and websocket
        redis_task = asyncio.create_task(handle_redis(pubsub))
        ws_task = asyncio.create_task(handle_ws(ws, name))

        # Intro
        await app["redis_conn"].publish("lablup-chat", f"server: {name}님이 입장하셨습니다. 나가시려면 quit을 입력해주세요.")

        # Chatting(websocket) task
        await ws_task

        # Outro
        await app["redis_conn"].publish("lablup-chat", f"server: {name}님이 퇴장하셨습니다.")

        # Discard websocket and redis tasks
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
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    app = web.Application()

    app.on_startup.append(init_all)
    app.on_shutdown.append(dispose_all)

    web.run_app(app, port=8080)
