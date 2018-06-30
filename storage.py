"""
Написать скрипт, который принимает в качестве аргументов ключи и значения и выводит информацию из хранилища
(в нашем случае — из файла).

Запись значения по ключу:
> storage.py --key key_name --val value
Получение значения по ключу:
> storage.py --key key_name

Ответом в данном случае будет вывод с помощью print соответствующего значения
> value
или
> value_1, value_2

если значений по этому ключу было записано несколько. Метрики сохраняйте в порядке их добавления.
Обратите внимание на пробел после запятой.
Если значений по ключу не было найдено, выводите пустую строку или None.

Для работы с аргументами командной строки используйте модуль argparse. Вашей задачей будет считать аргументы,
переданные вашей программе, и записать соответствующую пару ключ-значение в файл хранилища или вывести
значения, если был передан только ключ. Хранить данные вы можете в формате JSON с помощью стандартного
модуля json.

Напишите декоратор to_json, который можно применить к различным функциям, чтобы преобразовывать их возвращаемое
значение в JSON-формат. Не забудьте про сохранение корректного имени декорируемой функции.
"""
import argparse
import json
from os import path
from tempfile import gettempdir
from functools import wraps


# путь для файла хранилища во временной папке
storage_path = path.join(gettempdir(), 'storage.data')


def to_json(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        return json.dumps(result)
    return wrapped


def read(key=None):
    """
    Чтение из файла-хранилища и поиск по ключу.
    Если вызвана без ключа, возвращает JSON из файла
    :param key: str ключ, который ищем в JSON
    :return: dict | list | None
    """
    tmp = None

    try:
        with open(storage_path, 'r') as f:
            tmp = f.read()
    except FileNotFoundError:
        # Если файла нет - создаем его
        open(storage_path, 'w').close()

    if tmp:
        result = json.loads(tmp)
        # Если фун-ия вызвана с ключом, возвращаем значения из хранилища по ключу или None
        if key:
            return result.get(key, None)
    else:
        result = None

    return result


@to_json
def make(key, value):
    """
    Данные для записи в хранилище
    :param key: str
    :param value: list
    :return: dict
    """
    result = read() or {}

    if key in result:
        result[key].append(*value)
    else:
        result[key] = list(value)

    return result


def _main():
    parser = argparse.ArgumentParser(description='key-value storage')
    parser.add_argument('--key', help='ключ для хранения/чтения')
    parser.add_argument('--val', nargs='*', help='значение, одно и более')
    args = parser.parse_args()

    if args.key is None:
        print('Не передан ключ!\n"{} --help"'.format(path.basename(__file__)))
    elif args.val is None:
        tmp = read(args.key)
        if tmp:
            print(*tmp, sep=', ')
        else:
            print(tmp)
    else:
        tmp = make(args.key, args.val)
        with open(storage_path, 'w') as f:
            f.write(tmp)
            print('OK')


if __name__ == '__main__':
    _main()
