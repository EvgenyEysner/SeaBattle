# имортируем Enum константы могут иметь только тип (int), потом их можно сравнить
from enum import Enum  # перечисления

Title = 'Морской бой'

Tipps = '''
        - После начала игры вы ходите первым
        - Вы можете нажать Ctrl + C, чтобы выйти из игры в любое время
        - Исходный код доступен здесь: 
       '''


class AxisDirection(Enum):
    x = 1
    y = 0


class HitStatus:
    unknown = 0
    miss = 1
    miss_repeated = 2
    damaged = 3
    destroyed = 4


class Console:
    wrong_input = 0