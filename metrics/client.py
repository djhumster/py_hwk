import time
import socket


class ClientSocketError(Exception):
    pass


class ClientProtocolError(Exception):
    pass


class Client:
    def __init__(self, srv_ip, srv_port, timeout=None):
        self._srv_ip = srv_ip
        self._srv_port = srv_port
        self._timeout = timeout

    def put(self, metric, value, timestamp=None):
        if timestamp is None:
            timestamp = str(int(time.time()))

        msg = f'put {metric} {value} {timestamp}\n'
        answer = self._messenger(msg)

        if answer != 'ok\n\n':
            raise ClientProtocolError(answer)

    def get(self, metric):
        result = {}
        msg = f'get {metric}\n'

        answer = self._messenger(msg).split('\n')

        if answer[0] == 'error':
            raise ClientProtocolError(''.join(answer))

        if answer[0] != 'ok':
            raise ClientProtocolError(''.join(answer))

        for idx in range(1, len(answer) - 2):
            tmp = answer[idx].split()

            if tmp[0] not in result:
                #   {metric: [(timestamp, value), ...]}
                result[tmp[0]] = [(int(tmp[2]), float(tmp[1]))]
                continue

            result[tmp[0]].append((int(tmp[2]), float(tmp[1])))

        # сортировка значений метрик по timestamp
        for k in result:
            result[k].sort(key=lambda tpl: tpl[0])

        return result

    def _messenger(self, msg):
        answer = None

        with socket.create_connection(
            (self._srv_ip, self._srv_port), timeout=self._timeout
        ) as sock:

            sock.settimeout(self._timeout)
        
            try:
                sock.sendall(msg.encode('utf8'))
                answer = sock.recv(1024)

            except socket.timeout as err:
                raise ClientSocketError(err)
            except socket.error as err:
                raise ClientSocketError(err)
        
        return answer.decode('utf8')