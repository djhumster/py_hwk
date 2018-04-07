"""
Часто при зачислении каких-то средств на счет с нас берут комиссию.
Давайте реализуем похожий механизм с помощью дескрипторов. Напишите дескриптор Value,
который будет использоваться в нашем классе Account:
class Account:
    amount = Value()

    def __init__(self, commission):
        self.commission = commission
У аккаунта будет атрибут commission. Именно эту коммиссию и нужно вычитать при присваивании значений в amount.
"""


class Value:
    def __init__(self):
        self.value = None

    @staticmethod
    def _prepare_value(value, commission):
        if 1 < commission or commission < 0:
            raise ValueError(f'Комиссия должна быть числом от 0.0 до 1.0\n commission: {commission}')
        return value - (value * commission)

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        self.value = self._prepare_value(value, instance.commission)


class Account:
    amount = Value()

    def __init__(self, commission):
        self.commission = commission


new_account = Account(0.13)
new_account.amount = 200
print(new_account.amount)
