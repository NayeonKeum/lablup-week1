import asyncio

ADDR = "127.0.0.1"
PORT = 8888


class EchoServerProtocol(asyncio.Protocol):
    def __init__(self, clients):
        self.clients = clients

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        # TODO: for users already appended
        self.clients.append(transport)
        print('New connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        self.i = 0
        self._done = False
        message = data.decode()
        self.data = data

        if message.split(":")[-1] == "quit":
            print('Close the client socket')
            self.transport.close()

        asyncio.get_event_loop().call_soon(self.broadcast_chats)

        # for client in self.clients:
        #     client.write(data)

    def broadcast_chats(self,):
        if self._done:
            return
        self.clients[self.i].write(self.data)
        self.i += 1
        if self.i >= len(self.clients):
            self._done = True
            return
        asyncio.get_event_loop().call_later(0.1, self.broadcast_chats)

    def connection_lost(self, exc):
        print('The client %s closed the connection' %
              str(self.transport.get_extra_info('peername')[-1]))
        self.clients.remove(self.transport)
        asyncio.get_event_loop().stop()


async def main(ADDR, PORT):
    loop = asyncio.get_running_loop()

    clients = []

    server = await loop.create_server(
        lambda: EchoServerProtocol(clients),
        ADDR, PORT)

    async with server:
        await server.serve_forever()

asyncio.run(main(ADDR, PORT))
