import asyncio
import aiohttp
import aiohttp_cors
from datetime import datetime
from aiohttp import web
import redis.asyncio as redis
from aiohttp_session import get_session, setup, redis_storage


async def _init(app):
    connection = await redis.from_url("redis://localhost")

    # print("redis connected")  # debug
    app["connection"] = connection
    async with connection.pubsub() as pubsub:
        await pubsub.psubscribe("lablup-chat")
        # print("pubsub subscribed")  # debug

        app["pubsub"] = pubsub

        storage = redis_storage.RedisStorage(connection, httponly=True)
        setup(app, storage)

        # print('Connection opened')  # debug


class WebsocketHandler(web.View):
    async def post(self, ):
        # print("++++++++++++++++++++++++Websocket Handler++++++++++++++++++++++++++") # debug
        data = await self.request.post()
        # print("data: "+str(data))  # debug
        name = data.get("name")
        # print("name: "+name)  # debug
        await app["connection"].set(name, name+"-val")

        # print('app["connection"]: '+str(app["connection"]))  # debug

        global session
        session = await get_session(self.request)
        session["name"] = name
        session['last_visit'] = str(datetime.now())

        # print('session: '+str(session))  # debug

        return web.Response(status=200, text="Success")


class ChatRoomHandler(web.View):
    async def get(self, ):
        # print("++++++++++++++++++++++++ChatRoom Handler++++++++++++++++++++++++++") # debug
        data = await self.request.read()
        # print("self.request.read(): "+str(data))  # debug

        global session
        print("global session: "+str(session))

        name = session["name"]

        ws = web.WebSocketResponse()
        app["websockets"].add(ws)
        await ws.prepare(self.request)
        # print("ws prepared")  # debug

        pubsub = app["pubsub"]
        await pubsub.psubscribe("lablup-chat")
        # print("pubsub subscribed")  # debug

        # print("app['connection']: "+str(app["connection"]))  # debug

        redis_task = asyncio.create_task(handle_redis(pubsub))
        ws_task = asyncio.create_task(handle_ws(ws, name))

        await app["connection"].publish("lablup-chat", f"{name}님이 입장하셨습니다. 나가시려면 quit을 입력해주세요.")

        await ws_task

        await app["connection"].publish("lablup-chat", f"{name}님이 퇴장하셨습니다.")

        app["websockets"].discard(ws)
        await app["connection"].delete(name)
        redis_task.cancel()

        return ws


async def handle_ws(ws, name):
    async for msg in ws:
        if msg.data == "quit":
            await ws.close()
        else:
            await app["connection"].publish("lablup-chat", f"{name}: {msg.data}")


async def handle_redis(pubsub):
    while True:
        msg_redis = await pubsub.get_message(ignore_subscribe_messages=True)
        if msg_redis:
            # print("msg_redis['data'].decode(): " +
            #       str(msg_redis["data"].decode()))  # debug
            await broadcast(msg_redis["data"].decode())


async def broadcast(message):
    websockets = asyncio.Queue()
    msgBody = {
        "content": f"{message}",
        "time": str(datetime.now()),
    }
    # print("messages: "+str(messages))  # debug
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

    web.run_app(app, host="127.0.0.1", port=8080)


# TO DO
# 1. redis, http 연동
# - ㄱㄱ
# 2. 프론트 느낌 살리기
# - 로그인(없으면 만들어주고 있으면 그대로 감)
# - 그냥 모달 쓰자 ㅋㅋ
# - 채팅(보내는 사람에 따라서 방향 다르게!)
# 3. docker로 말기
# - 3 tier로 분리(구성도 작성): WEB, WAS, DB(그런데 이제 docker-compose를 이용하는,,, 그러니까 container를 이용한 3 tier)
# - github 연동해서 CI/CD(docker image build 각 디렉토리 별로!)
# 4.
