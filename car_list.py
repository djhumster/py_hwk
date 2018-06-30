"""
Есть данные о разных автомобилях и спецтехнике. Данные представлены в виде таблицы с характеристиками.
Обратите внимание на то, что некоторые колонки присущи только легковым автомобилям, например,
кол-во пассажирских мест. В свою очередь только у грузовых автомобилей есть длина, ширина и высота кузова.

Необходимо реализовать функцию, на вход которой подается имя файла в формате csv. Файл содержит данные
аналогичны строкам из таблицы. Вам необходимо прочитать этот файл построчно при помощи модуля
стандартной библиотеки csv. Затем проанализировать строки и создать список нужных объектов с автомобилями
и специальной техникой. Функция должна возвращать список объектов.
"""
import csv
from os import path


class BaseCar:
    def __init__(self, brand, photo_file_name, carrying):
        if not brand:
            raise ValueError('brand обязательный атрибут!')
        if not photo_file_name:
            raise ValueError('photo_file_name обязательный атрибут!')
        if not carrying:
            raise ValueError('carrying обязательный атрибут!')
        self.brand = brand
        self.photo_file_name = photo_file_name
        self.carrying = float(carrying)

    def get_photo_file_ext(self):
        return path.splitext(self.photo_file_name)[1] or None


class Car(BaseCar):
    car_type = 'car'

    def __init__(self, brand, photo_file_name, carrying, passenger_seats_count):
        super().__init__(brand, photo_file_name, carrying)
        if not passenger_seats_count:
            raise ValueError('passenger_seats_count обязательный атрибут!')
        self.passenger_seats_count = int(passenger_seats_count)


class Truck(BaseCar):
    car_type = 'truck'

    def __init__(self, brand, photo_file_name, carrying, body_whl=None):
        super().__init__(brand, photo_file_name, carrying)
        if body_whl:
            self._body_length, self._body_width, self._body_height = map(float, body_whl.split('x'))
        else:
            self._body_length, self._body_width, self._body_height = 0.0, 0.0, 0.0

    def get_body_volume(self):
        return self._body_length * self._body_width * self._body_height


class SpecMachine(BaseCar):
    car_type = 'spec_machine'

    def __init__(self, brand, photo_file_name, carrying, extra):
        super().__init__(brand, photo_file_name, carrying)
        self.extra = extra


def get_car_list(csv_filename='coursera_week3_cars.csv'):
    car_list = []

    try:
        with open(csv_filename, newline='', encoding='utf-8') as csv_f:
            reader = csv.reader(csv_f, delimiter=';')
            next(reader)

            for row in reader:
                tmp = row[0].split(',')
                row = tmp
                length = len(row)

                if length >= 6:
                    try:
                        if row[0] == 'car':
                            car_list.append(Car(
                                brand=row[1], photo_file_name=row[3], carrying=row[5],
                                passenger_seats_count=row[2]
                            ))
                        elif row[0] == 'truck':
                            car_list.append(Truck(
                                brand=row[1], photo_file_name=row[3], carrying=row[5],
                                body_whl=row[4]
                            ))
                        elif row[0] == 'spec_machine':
                            car_list.append(SpecMachine(
                                brand=row[1], photo_file_name=row[3], carrying=row[5],
                                extra=row[6]
                            ))
                    except ValueError as err:
                        print(f'Ошибка! {err}\nRow: {row}\n')
                else:
                    print(f'Ошибка! Некорректное кол-во столбцов: {length}\nRow: {row}\n')

    except IOError as err:
        print(f'Ошибка! #{err.errno} {err.strerror} {err.filename}')

    return car_list


if __name__ == '__main__':
    test = get_car_list()

    for x in test:
        print(x)
        print(f'Brand: {x.brand}; Photo ext: {x.get_photo_file_ext()}; Carrying: {x.carrying}')

        if isinstance(x, Car):
            print(f'Seats: {x.passenger_seats_count}')
        elif isinstance(x, Truck):
            print(f'whl: {x.get_body_volume()}')
        else:
            print(f'extra: {x.extra}')
