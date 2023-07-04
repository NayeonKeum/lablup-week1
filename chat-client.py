import asyncio

ADDR = "127.0.0.1"
PORT = 8888


class EchoClientProtocol(asyncio.Protocol):
    def __init__(self, name, on_con_lost):
        self.name = name
        self.on_con_lost = on_con_lost

    def connection_made(self, transport):
        self._done = False
        self.transport = transport
        self.on_con_lost.get_loop().call_soon(self.write_chats)

    def write_chats(self, ):
        if self._done:
            return

        message = input("[%s] > " % self.name)

        if message == "quit":
            self._done = True
            self.transport.close()

        message = "[%s]:%s" % (self.name, message)
        self.transport.write(message.encode())

        self.on_con_lost.get_loop().call_later(0.1, self.write_chats)

    def data_received(self, data):
        if "[%s]" % self.name in str(data):  # my chat
            pass
        else:
            print(data.decode())

    def connection_lost(self, exc):
        print('The server closed the connection')
        self._done = True
        self.on_con_lost.set_result(True)


async def main(ADDR, PORT):
    loop = asyncio.get_running_loop()
    on_con_lost = loop.create_future()

    user_name = input("Username plz: ")

    transport, protocol = await loop.create_connection(
        lambda: EchoClientProtocol(user_name, on_con_lost),
        ADDR, PORT)
    try:
        await protocol.on_con_lost
    finally:
        transport.close()


asyncio.run(main(ADDR, PORT))
