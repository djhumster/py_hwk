import unittest

from metrics.server import Storage, Parser, ParserError

IN_STORAGE = {
    'test1': {
        12: 2.0,
        11: 0.5,
    },
    'test2': {
        21: 301,
    }
}
METRICS_ALL = {
    'test1': [
        (11, 0.5),
        (12, 2.0),
    ],
    'test2': [
        (21, 301),
    ]
}
METRICS_TEST2 = {'test2': [(21, 301)]}

class TestStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.storage = Storage()

    def test_storage_put(self):
        self.assertEqual(self.storage.put('test', 11.0, 111), None)

    def test_storage_get(self):
        self.storage._data = IN_STORAGE

        params = {'*': METRICS_ALL, 'test2': METRICS_TEST2}

        for param, data in params.items():
            with self.subTest(param=param, data=data):
                self.assertEqual(self.storage.get(param), data)


class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def test_parser_encode(self):
        pass

    def test_parser_decode(self):
        commands = {
            'put test1 0.1 111\n': [('put', 'test1', 0.1, 111)],
            'get test2\n': [('get', 'test2')],
            'get test3\nget test4\n': [
                ('get', 'test3'),
                ('get', 'test4')
            ]
        }

        for cmd, compare_with in commands.items():
            with self.subTest(command=cmd, compare_with=compare_with):
                self.assertEqual(self.parser.decode(cmd), compare_with)

        get_error = ('get_parser_error', 'put test5 bla bla\n')

        for get_err in get_error:
            with self.subTest(get_error=get_err):
                self.assertRaises((ValueError, ParserError), self.parser.decode, get_err)
