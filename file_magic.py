"""
Класс File должен поддерживать несколько необычных операций.
-Класс инициализируется полным путем.
-Класс должен поддерживать метод write.
-Объекты типа File должны поддерживать сложение.
    В этом случае создается новый файл и файловый объект, в котором содержимое второго файла добавляется к содержимому
    первого файла. Новый файл должен создаваться в директории, полученной с помощью tempfile.gettempdir. Для получения
    нового пути можно использовать os.path.join.
-Объекты типа File должны поддерживать протокол итерации, причем итерация проходит по строкам файла.
-И наконец, при выводе файла с помощью функции print должен печататься его полный путь, переданный при инициализации.
"""
import tempfile


class File:
    def __init__(self, path):
        self._path = path
        # ссылка на файл объект, для итерации по строкам
        self._itero = None

    def __str__(self):
        return self._path

    def __add__(self, obj):
        new_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        try:
            with open(new_file.name, 'a') as nf:
                with open(self._path, 'r') as f:
                    tmp = f.read()

                nf.write(tmp)
                with open(obj.path, 'r') as f:
                    tmp = f.read()

                nf.write('\n' + tmp)

            return File(new_file.name)
        except IOError as err:
            print(f'Ошибка! {err.filename}\n{err.errno} {err.strerror}')
            return None

    def __iter__(self):
        try:
            self._itero = open(self._path, 'r')
        except IOError as err:
            print(f'Ошибка! {err.filename}\n{err.errno} {err.strerror}')
        return self

    def __next__(self):
        if self._itero is None:
            raise StopIteration

        result = self._itero.readline()
        if not result:
            self._itero.close()
            raise StopIteration

        return result

    @property
    def path(self):
        return self._path

    def write(self, line):
        try:
            with open(self._path, 'a') as f:
                f.write(line)
        except IOError as err:
            print(f'Ошибка! {err.filename}\n{err.errno} {err.strerror}')
