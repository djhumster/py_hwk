import time
import socket


class ClientError(Exception):
    """Общий класс исключений клиента"""
    pass


class ClientSocketError(ClientError):
    """Исключение, выбрасываемое клиентом при сетевой ошибке"""
    pass


class ClientProtocolError(ClientError):
    """Исключение, выбрасываемое клиентом при ошибке протокола"""
    pass


class Client:
    def __init__(self, srv_ip, srv_port, timeout=None):
        self._srv_ip = srv_ip
        self._srv_port = srv_port
        try:
            self._conn = socket.create_connection((srv_ip, srv_port), timeout)
        except socket.error as err:
            raise ClientSocketError('Ошибка подключения:\n', err)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_trbk):
        self.close()
        
    def put(self, metric, value, timestamp=None):
        '''Подготовка и отправка метрики на сервер'''
        if timestamp is None:
            timestamp = str(int(time.time()))

        msg = f'put {metric} {value} {timestamp}\n'
        self._messenger(msg)

    def get(self, metric):
        '''Запрос метрик с сервера.

        :metric: имя метрики
                 * - все метрики
        :return: {metric: [(timestamp, value), ...], ...}
        '''
        result = {}
        msg = f'get {metric}\n'

        answer = self._messenger(msg)

        if answer == '':
            return result

        for item in answer.split('\n'):
            tmp = item.split()

            if tmp[0] not in result:
                result[tmp[0]] = []
            #   {metric: [(timestamp, value), ...], ...}
            result[tmp[0]].append((int(tmp[2]), float(tmp[1])))

        # сортировка значений метрик по timestamp
        for k in result:
            result[k].sort(key=lambda tpl: tpl[0])

        return result

    def _messenger(self, msg):
        '''Отправка запроса на сервер и получение ответа'''
        answer = ''
    
        try:
            self._conn.sendall(msg.encode('utf8'))
        except socket.error as err:
            raise ClientSocketError(f'Ошибка отправки:\n{msg}\n', err)
        
        while not answer.endswith('\n\n'):
            try:
                answer += self._conn.recv(1024).decode('utf8')
            except socket.error as err:
                raise ClientSocketError('Ошибка полчения данных:\n', err)

        status, data = answer.split('\n', 1)

        if status == 'error' or status != 'ok':
            raise ClientProtocolError(f'Ошибка протокола:\n {answer}')

        return data.strip()

    def close(self):
        '''Закрытие сокета'''
        self._conn.close()