import asyncio


class Storage:
    '''Хранилище {metric: {timestamp: value}, ...}. 
    Возвращает словарь метрик с отсортированными данными по timestamp.
    {metric: [(timestamp: value), ...], ...}'''
    def __init__(self):
        self._data = {}

    def get(self, key):
        data = self._data
        # получаем конкретную метрику, если запрошены не все
        if key != '*':
            data = {
                key: data.get(key, {})
            }

        result = {}
        # присваиваем ключу список кортежей, отсортированный по timestamp
        for key, values in data.items():
            result[key] = sorted(values.items())

        return result

    def put(self, key, value, timestamp):
        if key not in self._data:
            self._data[key] = {}

        self._data[key][timestamp] = value


class ParserError(ValueError):
    pass


class Parser:
    @staticmethod
    def encode(responses):
        '''Кодирует ответ сервера в строку
        [{metric: [(timestamp, value), (..) ..]}, {}, ...]
        =====
        `ok\nmetric value timestamp\nmetric value timestamp\n\n`
        '''
        rows = []

        for response in responses:
            if not response:
                continue

            for metric, values in response.items():
                if not values:
                    continue

                for tpl in values:
                    # tpl[0] - timestamp
                    # tpl[1] - value
                    rows.append(f'{metric} {tpl[1]} {tpl[0]}')

        result = 'ok\n'

        if rows:
            result += '\n'.join(rows) + '\n'

        return result + '\n'

    @staticmethod
    def decode(data):
        '''Декодирует и конвертирует данные, возвращает список кортежей с командами.
        Может вернуть ошибку ParserError

        'put <key> <value:float> <timestamp:int>\n'
        'get <key>\n'
        =====
        [('put', 'key', value:float, timestamp: int), ...]
        [('get', 'key'), ...]
        '''
        lines = data.split('\n')
        result = []

        for line in lines:
            if not line:
                continue

            try:
                method, data = line.strip().split(' ', 1)
                
                if method == 'get':
                    key = data
                    result.append(
                        (method, key)
                    )
                elif method == 'put':
                    key, value, timestamp = data.strip().split()
                    result.append(
                        (method, key, float(value), int(timestamp))
                    )
                else:
                    raise ValueError('unknown method')
            except ValueError:
                raise ParserError('wrong command')

        return result


class ClientServerProtocol(asyncio.Protocol):
    _storage = Storage()

    def __init__(self):
        super().__init__()

        self._parser = Parser()
        self._buffer = b''

    def connection_made(self, transport):
        self._transport = transport

    def data_received(self, data):
        self._buffer += data
        try:
            decoded_data = self._buffer.decode('utf8')
        except UnicodeDecodeError:
            return

        if not decoded_data.endswith('\n'):
            return

        self._buffer = b''

        try:
            commands = self._parser.decode(decoded_data)
            response = self._procesed_data(commands)
        except ValueError as err:
            rsp = f'error\n{err}\n\n'
            self._transport.write(rsp.encode('utf8'))   
            return 
            
        self._transport.write(response.encode('utf8'))
    
    def _procesed_data(self, commands):
        responses = []

        for cmd in commands:
            resp = self._run(*cmd)
            responses.append(resp)

        return self._parser.encode(responses)

    def _run(self, method, *params):
        # проверка правильности методов и данных происходит в Parser.decode()
        if method == 'get':
            return self._storage.get(*params)
        elif method == 'put':
            self._storage.put(*params)


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
    print('Starting server 127.0.0.1:2121')
    run_server('127.0.0.1', 2121)
