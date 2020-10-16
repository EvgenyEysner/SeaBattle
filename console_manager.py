import os

from constants import *


def press_enter(message=None, action="...."):
    message_press_enter = f"Нажмите Enter для {action}... "

    if message is not None:
        message_press_enter = f"{message} {message_press_enter}"

    input(message_press_enter)


def clear():
    if os.name == 'nt':
        console_command = 'cls'
    else:
        console_command = 'clear'

    os.system(console_command)


def raise_wrong_hit_status(hit_status, x=None, y=None, details=None):
    message = 'Неправильный статус попадания ({}).'
    message = message.format(hit_status)

    if x is not None and y is not None:
        coordinates = '\nКоординаты: x{} y{}.'.format(x, y)
        message += coordinates

    if details is not None:
        details = "\nDetails: {}".format(details)
        message += details

    raise ValueError(message)


def request_input(heading, choices):
    if not heading:
        heading = 'Выбор'

    message = f"### {heading}:"

    for number, choice in enumerate(choices):
        snipped = f"\n {number + 1}. {choice}"
        message += snipped

    message += '\n\nВыберите действие и нажмите Enter'

    input_value = input(message)
    input_value = validate_input(input_value, len(choices))
    return input_value


def validate_integer(value):
    try:
        value = int(value)
    except ValueError:
        print('Ошибка, введите число!')
        return Console.wrong_input
    else:
        return value


def validate_input(value, choices_quantity):
    value = validate_integer(value)

    if value is Console.wrong_input:
        press_enter()
        return Console.wrong_input
    elif 0 < value <= choices_quantity:
        return value
    else:
        message = (
            f'Вы можете выбрать от 1 до {choices_quantity} влючительно.'
            f'\nПобробуйте ещё раз'
        )
        print(message)
        press_enter()
        return Console.wrong_input


def validate_input_coordinate(value, board_size):
    value = validate_integer(value)

    if value is Console.wrong_input:
        return Console.wrong_input
    elif 0 <= value < board_size:
        return value
    else:
        print('Ошибка! Попробуйте ещё раз!')
        return Console.wrong_input