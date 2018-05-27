def chunk(arr, size):
    '''
    Разбивает список на меньшие, указанного размера
    >>> chunk([1, 2, 3, 4, 5], 2)
    [[1, 2], [3, 4], [5]]
    '''
    from math import ceil

    return list(map(
            lambda x: arr[x * size:x * size + size], 
            list(range(0, ceil(len(arr) / size)))
        ))

def compact(arr):
    '''
    Удаление ложных значений (False, None, 0, и «») из списка
    >>> compact([0, 1, False, 2, '', 3, 'test'])
    [1, 2, 3, 'test']
    '''
    return list(filter(lambda x: bool(x), arr))

def count_by(arr, fn=lambda x: x):
    '''
    Группирует элементы списка и возвращает количество элементов в каждой группе.
    Используется map() для сопоставления значений списка со значениями функции.
    За каждую итерацию счетчик увеличивается.
    >>> count_by(['one', 'two', 'three'], len)
    {3: 2, 5: 1}
    '''
    result = {}

    for item in map(fn, arr):
        result[item] = 0 if item not in result else result[item]
        result[item] += 1
    
    return result

def count_occurences(arr, val):
    '''
    Считает количество повторений заданного значения.
    reduce увеличивает счетчик, когда сталкивается с определенным значением внутри списка.
    >>> count_occurences([1, 1, 2, 1, 2], 1)
    3
    '''
    from functools import reduce

    return reduce(
            (lambda x, y: x + 1 if y == val and type(y) == type(val) else x + 0), arr
        )

def spread(arg):
    '''
    Сглаживает список (не глубоко) и возвращает новый список.
    >>> spread([1,2,3,[4,5,6],[7],8,9])
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
    '''
    result = []
    for item in arg:
        if isinstance(item, list):
            result.extend(item)
        else:
            result.append(item)
    
    return result

def deep_flatten(arr):
    '''
    Выравнивание списка при помощи рекурсии.
    Используется list.extend() вместе с пустым массивом (result) и 
    функция spread() для сглаживания каждого элемента списка.
    >>> deep_flatten([1, [2], [[3], 4], 5])
    [1, 2, 3, 4, 5]
    '''
    result = []
    result.extend(
        spread(list(map(
            lambda x: deep_flatten(x) if isinstance(x, list) else x, arr
        )))
    )

    return result

def difference(a, b):
    '''
    Возвращает разницу между двумя массивами. 
    Создает set из b и сохраняет только те значения, которые не содержатся в b.
    >>> difference([1, 2, 3], [1, 2, 4])
    [3]
    '''
    b = set(b)

    return [item for item in a if item not in b]

def difference_by(a, b, fn):
    '''
    Возвращает разницу между двумя списками, после применения функции к обоим спискам. 
    Создает set, применяя fn к каждому элементу в b, затем использует сочетание fn и a,
    чтобы сохранить только значения, не содержащиеся в ранее созданном set.
    >>> difference_by([2.1, 1.2], [2.3, 3.4], round)
    [1.2]
    >>> difference_by([{ 'x': 2 }, { 'x': 1 }], [{ 'x': 1 }], lambda v: v['x'])
    [{'x': 2}]
    '''
    b = set(map(fn, b))

    return [item for item in a if fn(item) not in b]

def insertion_sort(arr):
    '''
    >>> insertion_sort([7, 4, 2, 3, 1, 5, 6])
    [1, 2, 3, 4, 5, 6, 7]
    '''
    for i in range(0, len(arr)):
        tmp = arr[i]
        j = i - 1

        while j >= 0 and tmp < arr[j]:
            arr[j + 1] = arr[j]
            arr[j] = tmp
            j -= 1

    return arr

def shuffle(arr):
    '''
    Рандомизирует порядок значений списка, возвращая новый список.
    Использует алгоритм Фишера-Йейтса для изменения порядка элементов списка.
    '''
    from copy import deepcopy
    from random import randint

    tmp = deepcopy(arr)
    length = len(tmp)

    while length:
        length -= 1
        i = randint(0, length)
        tmp[length], tmp[i] = tmp[i], tmp[length]
    
    return tmp

def izip(*args, fill_value=None):
    '''
    Создает список элементов, группируя их на основании позиции в оригинальном списке.
    Используется max вместе с list comprehension для получения длины самого длинного списка в аргументах.
    >>> izip(['a', 'b'], [1, 2], [True, False])
    [['a', 1, True], ['b', 2, False]]
    >>> izip(['a'], [1, 2], [True, False], fill_value = '_')
    [['a', 1, True], ['_', 2, False]]
    '''
    max_length = max([len(arr) for arr in args])
    result = []

    for i in range(max_length):
        result.append([
            args[k][i] if i < len(args[k]) else fill_value for k in range(len(args))
        ])
    
    return result

def byte_size(string):
    '''
    Возвращает длину строки в байтах.
    >>> byte_size('Hello World')
    11
    '''
    return len(string.encode('utf-8'))

def capitalize(string, lower_rest=False):
    '''
    >>> capitalize('fooBar')
    'FooBar'
    >>> capitalize('fooBar', True)
    'Foobar'
    '''
    return string[:1].upper() + (string[1:].lower() if lower_rest else string[1:])

if __name__ == '__main__':
    import doctest
    doctest.testmod()