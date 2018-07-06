import asyncio


class ClientServerProtocol(asyncio.Protocol):
    #   {metric: [(timestamp, value), ...], ...}
    _storage = {}

    def connection_made(self, transport):
        self._transport = transport

    def data_received(self, data):
        if not data.endswith(b'\n'):
            self._send_err()
            return
        
        rcvd = data.decode('utf8').strip().split()

        if len(rcvd) < 2:
            self._send_err()
            return

        cmd = rcvd.pop(0)

        if cmd == 'put':
            self._put(rcvd)
        elif cmd == 'get':
            self._get(rcvd[0])
        else:
            self._send_err()

    def _put(self, data):
        if len(data) < 3:
            self._send_err()
            return
        # data[0] - metric
        if data[0] not in self._storage:
            self._storage[data[0]] = []
        
        try:
            self._storage[data[0]].append((
                    int(data[2]),   # timestamp
                    float(data[1])  # value
                ))
            self._transport.write(b'ok\n\n')
        except ValueError:
            self._send_err()

    def _get(self, metric):
        self._transport.write(b'ok\n')
        metric = metric.strip()

        if metric == '*':
            for key, value in self._storage.items():
                for tpl in value:
                    # tpl = [(timestamp, value), ...]
                    answer = f'{key} {tpl[1]} {tpl[0]}\n'
                    self._transport.write(answer.encode('utf8'))
        else:
            tmp = self._storage.get(metric)
            if tmp is not None:
                for tpl in tmp:
                    # tpl = [(timestamp, value), ...]
                    answer = f'{metric} {tpl[1]} {tpl[0]}\n'
                    self._transport.write(answer.encode('utf8'))

        self._transport.write(b'\n')
    
    def _send_err(self):
        self._transport.write(b'error\nwrong command\n\n')


def run_server(host, port):
    loop = asyncio.get_event_loop()
    coro = loop.create_server(ClientServerProtocol, host, port)
    srv = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    srv.close()
    loop.run_until_complete(srv.wait_closed())
    loop.close()

if __name__ == '__main__':
    run_server('127.0.0.1', 2121)
    print('Server started! 127.0.0.1:2121')