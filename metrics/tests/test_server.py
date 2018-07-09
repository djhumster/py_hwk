import unittest
from unittest.mock import patch

from metrics.server import ClientServerProtocol, Parser, ParserError, Storage

IN_STORAGE_FIXTURE = {
    'test1': {
        12: 2.0,
        11: 0.5,
    },
    'test2': {
        21: 301.0,
    }
}
METRICS_ALL_FIXTURE = {
    'test1': [
        (11, 0.5),
        (12, 2.0),
    ],
    'test2': [
        (21, 301.0),
    ]
}
S_METRICS_ALL_FIXTURE = 'ok\ntest1 0.5 11\ntest1 2.0 12\n' \
                'test2 301.0 21\n\n'
METRICS_TEST2_FIXTURE = {'test2': [(21, 301.0)]}
S_METRICS_TEST2_FIXTURE = 'ok\ntest2 301.0 21\n\n'

class TestStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.storage = Storage()

    def test_storage_put(self):
        self.assertEqual(self.storage.put('test', 11.0, 111), None)

    def test_storage_get(self):
        self.storage._data = IN_STORAGE_FIXTURE

        params = {'*': METRICS_ALL_FIXTURE, 'test2': METRICS_TEST2_FIXTURE}

        for param, data in params.items():
            with self.subTest(param=param, data=data):
                self.assertEqual(self.storage.get(param), data)


class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def test_parser_encode(self):
        compare_empty = [{}]
        s_compare_empty = 'ok\n\n'

        self.assertEqual(self.parser.encode([METRICS_ALL_FIXTURE]), S_METRICS_ALL_FIXTURE)
        self.assertEqual(self.parser.encode(compare_empty), s_compare_empty)

    def test_parser_decode(self):
        commands_fixture = {
            'put test1 0.1 111\n': [('put', 'test1', 0.1, 111)],
            'get test2\n': [('get', 'test2')],
            'get test3\nget test4\n': [
                ('get', 'test3'),
                ('get', 'test4')
            ]
        }

        for cmd, compare_with in commands_fixture.items():
            with self.subTest(command=cmd, compare_with=compare_with):
                self.assertEqual(self.parser.decode(cmd), compare_with)

    def test_parser_decode__err(self):
        get_error = ('get_parser_error', 'put test5 bla bla\n')

        for get_err in get_error:
            with self.subTest(get_error=get_err):
                self.assertRaises((ValueError, ParserError), self.parser.decode, get_err)


class StorageMock:
    def put(self, *args):
        return

    def get(self, key):
        if key == '*':
            return METRICS_ALL_FIXTURE
        elif key == 'test2':
            return METRICS_TEST2_FIXTURE
        else:
            return {key: []}


class TransportMock:
    _rsp_buffer = []

    def write(self, data):
        self._rsp_buffer.append(data)
    
    @classmethod
    def get_data(cls):
        return cls._rsp_buffer.pop(0)


class TestClientServerProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ClientServerProtocol()
        cls.srv.connection_made(TransportMock())

    @patch('metrics.server.Storage.put', StorageMock.put)
    def test_put(self):
        self.srv.data_received(b'put test .2 11\n')
        resp = TransportMock.get_data()

        self.assertEqual(resp, b'ok\n\n')

    @patch('metrics.server.Storage.get', StorageMock.get)
    def test_get__all(self):
        self.srv.data_received(b'get *\n')
        resp = TransportMock.get_data()

        self.assertEqual(resp, S_METRICS_ALL_FIXTURE.encode())

    @patch('metrics.server.Storage.get', StorageMock.get)
    def test_get__test2(self):
        self.srv.data_received(b'get test2\n')
        resp = TransportMock.get_data()

        self.assertEqual(resp, S_METRICS_TEST2_FIXTURE.encode())

    def test_get__empty(self):
        self.srv.data_received(b'get empty\n')
        resp = TransportMock.get_data()

        self.assertEqual(resp, b'ok\n\n')

    @patch('metrics.server.Storage.get', StorageMock.get)
    @patch('metrics.server.Storage.put', StorageMock.put)
    def test_wrong_cmd__err(self):
        get_error = (b'get_error\n', b'put test5 bla\n')

        for get_err in get_error:
            with self.subTest():
                self.srv.data_received(get_err)
                resp = TransportMock.get_data()

                self.assertEqual(resp, b'error\nwrong command\n\n')
