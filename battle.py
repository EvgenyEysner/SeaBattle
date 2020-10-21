import random
import console_manager
from enum import Enum  # имортируем Enum константы могут иметь только тип (int), потом их можно сравнить


Title = 'Морской бой'

Tips = '''
        - После начала игры вы ходите первым
        - Вы можете нажать Ctrl + C, чтобы выйти из игры в любое время
        - Исходный код доступен здесь: 
       '''


class AxisDirection(Enum):
    x = 1
    y = 0


class Console(Enum):
    wrong_input = 0


class Color:
    green = '\033[0;32m'
    reset = '\033[0m'  # Color Off
    blue = '\033[0;34m'
    yellow = '\033[0;35m'
    red = '\033[0;31m'
    background = '\033[0;30m'  # Black
    miss = '\033[037m'  # White


# функция которая окрашивает текст в заданный цвет.
def add_color(text, color):
    return color + text + Color.reset


# класс клеток и цвет в зависимости от того что там находитмся
class Cell:
    ship_unit = add_color('▄', Color.blue)  # корабль
    damaged_ship = add_color('x', Color.red)  # корабль подбитый
    destroyed_ship = add_color('▄', Color.red)  # корабль потопленный
    empty_cell = add_color(' ', Color.background)  # пустое поле
    miss_cell = add_color('*', Color.miss)  # поле для прохама и закраски клеток вокруг корабля
    miss_repeated = miss_cell

OFFSETS = (-1, 0, 1)


class Board:

    size = 10  # размер поля
#    is_monitoring = False  # для отладки
    ship_list = ((1, 4), (2, 3), (3, 2), (4, 1))  # корабли, количество - размер

    board_ai = None
    board_player = None

#    text_offset_start = 2  # стартовая позиция для отрисовки обозначений
#    text_offset_center = 1  # стартовая позиция для отрисовки поля

    def __init__(self):
#        self.validate_size()

        self.rows = []  # фактическое поле (ряды ячеек)
        self.ships = []  # все созданные корабли

#        self.is_onside = True
        self.alive_ships_number = sum([ship[0] for ship in self.ship_list])

        self.create_rows()
        self.create_ships()

    def create_rows(self):  # создаю клетки поля
        for row in range(self.size):
            self.rows.append([Cell.empty_cell] * self.size)

    def create_ships(self):  # создаю корабли
        for ship_type in self.ship_list:  # цикл по tuple ship_list = ((1, 4), (2, 3), (3, 2), (4, 1))
            ship_quantity = ship_type[0]  # нулевая позиция это всегда кол-во
            ship_size = ship_type[1]  # 1 тип коробля
            for ship_number in range(ship_quantity):
                Ship(self, ship_size)

    def check_ship_hit(self, x, y):  # проверяю статус корабля
        hit_status = None  # для начала присваиваю "неизвестный"
        cell = self.rows[y][x]  # клетка состоит из координат x,y

        if cell is Cell.empty_cell:
            hit_status = Cell.miss_cell  # если эта клетка была пустой, меняем статус на промах
        if cell in (Cell.miss_cell, Cell.damaged_ship, Cell.destroyed_ship):  # если ход выпадает на клетку подбитого, уничтоженного корабля или ещё раз в пустую клетку
            hit_status = Cell.miss_repeated  # меняю статус на повторный промах и вывожу сообщениие, вывод дальше
        if cell is Cell.ship_unit:  # если клетка является клеткой корабля
            for ship in self.ships:  # запускаем цикл по self.ships = []
                ship_hit_status = ship.check_is_hit(x, y)  # вызываем функцию "попадания"
                if ship_hit_status is not Cell.miss_cell:
                    hit_status = ship_hit_status  # присваиваем соответсвующий статус
                    break

        if hit_status is Cell.miss_cell:
            self.rows[y][x] = Cell.miss_cell
        elif hit_status is Cell.destroyed_ship:  # если корабль потоплен вызываем функцию update_status()
            self.update_status()  # вносим изменения

        return hit_status

    def update_status(self):  # обнавляем статус корабля
        alive_ships_number = 0

        for ship in self.ships:  # запускаем цикл по self.ships = []
            if not ship.is_destroyed:  # если корабль целый добавляем
                alive_ships_number += 1

        if alive_ships_number == 0:  # если кораблей нет, то сумма всех кораблей = 0
            self.alive_ships_number = alive_ships_number

# создаю поле с координатами
    @classmethod
    def print_boards(cls):
        console_manager.clear()

        cls.print_headings()  # название полей, кол-во кораблей
        cls.print_horizontal_numbers()  # координаты

        for row_index in range(cls.size):
            # координаты слева
            print(row_index, end=' ')

            # Поле ИИ:
            row = cls.board_ai.rows[row_index]
            for cell_index in range(cls.size):
                cell = row[cell_index]
                if cell is Cell.ship_unit:
                    cell = Cell.empty_cell
                print(cell, end=' ')
            print(row_index, end=' ')

            # Поле игрока:
            row = cls.board_player.rows[row_index]
            for cell_index in range(cls.size):
                cell = row[cell_index]
                print(cell, end=' ')
            print(row_index)

        cls.print_horizontal_numbers()
        print()

# Надписи над полями для игры
    @classmethod
    def print_headings(cls):
        cls.print_offset_start()

        def get_ship_message(ships_quantity):
            if ships_quantity == 1:
                return "Корабль"
            else:
                return "Кораблей"

        ships_ai = Board.board_ai.alive_ships_number
        ships_player = Board.board_player.alive_ships_number

        header_ai = f' Питон ({ships_ai} {get_ship_message(ships_ai)})'
        header_player = f' Человек ({ships_player} {get_ship_message(ships_player)})'
        heading_player_offset = cls.size * 2 + 2 - len(header_ai)
        indentation = ' ' * heading_player_offset

        print(header_ai, end=indentation)
        print(header_player, end='\n')

# рисуем горизонтальные координаты
    @classmethod
    def print_horizontal_numbers(cls):
        cls.print_offset_start()  # отступ

        for n in range(cls.size):  # цикл по полю, т.е. range(10)
            print(n, end=' ')

        cls.print_offset_center()  # отступ

        for n in range(cls.size):  # цикл по полю, т.е. range(10)
            print(n, end=' ')

        print()

# создаю отступ для верхних координат
    @classmethod
    def print_offset_start(cls):
        print(end=' ' * 2)

    @classmethod
    def print_offset_center(cls):
        print(end=' ' * 2)


class Ship:

    spawn_maximum_attempts_number = 256

    def __init__(self, board, size):
        self.board = board
        self.size = size
        self.x = None
        self.y = None
        self.axis_direction = None
        self.body_status = [True] * self.size
        self.is_destroyed = False

        self.generate_position()
        board.ships.append(self)


    def generate_position(self):
        is_spawning = True
        spawn_attempt = 0

        while is_spawning:
            if spawn_attempt == self.spawn_maximum_attempts_number:
                message = 'Превышено количество попыток {}.'
                message = message.format(self.spawn_maximum_attempts_number)
                raise OverflowError(message)
            else:
                spawn_attempt += 1

            self.axis_direction = random.choice((AxisDirection.x, AxisDirection.y))

            if self.axis_direction is AxisDirection.x:
                x_range = Board.size - self.size
                y_range = Board.size
            else:
                x_range = Board.size 
                y_range = Board.size - self.size

            self.x = random.randrange(x_range)
            self.y = random.randrange(y_range)

            if not self.check_is_collision():
                is_spawning = False

        self.draw_as_new()

    def check_is_collision(self):
        is_collision = False

        for n in range(self.size):
            if self.axis_direction is AxisDirection.x:
                x = self.x + n  # отступы между кораблями
                y = self.y
            else:
                x = self.x
                y = self.y + n

            for x_offset in OFFSETS:
                for y_offset in OFFSETS:
                    x_check = x + x_offset
                    y_check = y + y_offset
                    is_x_on_board = 0 <= x_check < Board.size
                    is_y_on_board = 0 <= y_check < Board.size
                    if is_x_on_board and is_y_on_board:
                        cell = self.board.rows[y_check][x_check]
                        if cell is Cell.ship_unit:
                            is_collision = True
                            return is_collision

        return is_collision

    def check_is_hit(self, hit_x, hit_y):
        hit_status = Cell.miss_cell

        if self.axis_direction is AxisDirection.x:
            a1 = self.x
            a2 = hit_x
            b1 = self.y
            b2 = hit_y
        else:
            a1 = self.y
            a2 = hit_y
            b1 = self.x
            b2 = hit_x

        if b1 == b2 and a1 <= a2 < a1 + self.size:
            damaged_unit_id = a2 - a1
            self.body_status[damaged_unit_id] = False
            hit_status = Cell.damaged_ship
            if not any(self.body_status):
                self.is_destroyed = True
                hit_status = Cell.destroyed_ship
                self.draw_as_destroyed()
            else:
                self.draw_damage(hit_x, hit_y)

        return hit_status

    def draw_as_new(self):
        for n in range(self.size):
            if self.axis_direction is AxisDirection.x:
                x = self.x + n
                y = self.y
            else:
                x = self.x
                y = self.y + n
            self.board.rows[y][x] = Cell.ship_unit

    def draw_as_destroyed(self):
        for n in range(self.size):
            if self.axis_direction is AxisDirection.x:
                x = self.x + n
                y = self.y
            else:
                x = self.x
                y = self.y + n
            self.board.rows[y][x] = Cell.destroyed_ship

            for y_offset in OFFSETS:
                for x_offset in OFFSETS:
                    x_neighbor = x + x_offset
                    y_neighbor = y + y_offset
                    if 0 <= x_neighbor < Board.size and 0 <= y_neighbor < Board.size:
                        cell = self.board.rows[y_neighbor][x_neighbor]
                        if cell is Cell.empty_cell:
                            self.board.rows[y_neighbor][x_neighbor] = Cell.miss_cell

    def draw_damage(self, x, y):
        self.board.rows[y][x] = Cell.damaged_ship


class AI(object):

    is_super_ai = False  # для отладки

    def __init__(self):
        self.x_hit = None
        self.y_hit = None
        self.last_message = ''
        self.is_turn = False

    def make_turn(self):
        self.is_turn = True

        while self.is_turn:
            if self.is_super_ai:
                self.choose_hit_position_strictly()
            else:
                self.choose_hit_position_randomly()

            self.hit_position()
            self.print_data()

            if not Board.board_player:
                self.is_turn = False

    def choose_hit_position_strictly(self):
        x_hit = None
        y_hit = None

        for ship in Board.board_player.ships:
            if ship.is_destroyed:
                continue

            hit_ship_unit_index = None
            for index, ship_unit in enumerate(ship.body_status):
                if ship_unit:
                    hit_ship_unit_index = index
                    break

            if hit_ship_unit_index is not None:
                if ship.axis_direction is AxisDirection.x:
                    x_hit = ship.x + hit_ship_unit_index
                    y_hit = ship.y
                else:
                    x_hit = ship.x
                    y_hit = ship.y + hit_ship_unit_index
                break

        if x_hit is None or y_hit is None: # потом
            raise RuntimeError('ИИ не может найти позицию для точного выстрела.')
        else:
            self.x_hit = x_hit
            self.y_hit = y_hit

    def choose_hit_position_randomly(self):
        x_hit = None
        y_hit = None

        is_guessing = True
        while is_guessing:
            x_hit = random.randrange(Board.size)
            y_hit = random.randrange(Board.size)
            cell = Board.board_player.rows[x_hit][y_hit]
            if cell is Cell.ship_unit or cell is Cell.empty_cell:
                is_guessing = False

        self.x_hit = x_hit
        self.y_hit = y_hit

    def hit_position(self):
        hit_status = Board.board_player.check_ship_hit(self.x_hit, self.y_hit)

        if hit_status is Cell.damaged_ship:
            message = 'ИИ повредил ваш корабль (X: {}, Y: {}).'
        elif hit_status is Cell.destroyed_ship:
            message = 'ИИ уничтожил ваш корабль (X: {}, Y: {}).'
        else:
            self.is_turn = False
            message = 'ИИ промахнулся (X: {}, Y: {}).'

        if hit_status is Cell.damaged_ship or hit_status is Cell.destroyed_ship:
            message = f'{message} и ходит ещё раз.'

        self.last_message = message.format(self.x_hit, self.y_hit)

    def print_data(self):
        Board.print_boards()
        print(self.last_message)
        console_manager.press_enter()


is_intro = True
is_game = True

ai = AI()
Board.board_ai = Board()
Board.board_player = Board()


def intro():
    Board.print_boards()

    message_intro = f"Добро пожалавать в {Title} {Tips}"
    input_value = console_manager.request_input(message_intro, (
        'Расставить корабли',
        'Игра!',
        'Описание',
    ))

    if input_value == 1:
        Board.board_player = Board()
    elif input_value == 2:
        global is_intro
        is_intro = False
    elif input_value == 3:
        console_manager.clear()
        print(f'Описание')
        console_manager.press_enter(action='вернуться в меню')


def game():
    global is_game
    is_player_turn = True

    while is_player_turn:
        Board.print_boards()

        hit_x, hit_y = input('Коордитаты Х: '), input('Коордитаты Y: ')

        hit_x = console_manager.validate_input_coordinate(hit_x, Board.size)
        hit_y = console_manager.validate_input_coordinate(hit_y, Board.size)

#        if hit_x is Console.wrong_input or hit_y is Console.wrong_input:
#            console_manager.press_enter()

        hit_status = Board.board_ai.check_ship_hit(hit_x, hit_y)

        if hit_status is Cell.miss_cell:
            is_player_turn = False
            message = 'Ты промахнулся'

        elif hit_status is Cell.damaged_ship:
            message = 'Ты повредил вражеский корабль.'

        elif hit_status is Cell.destroyed_ship:
            message = 'Ты уничтожил вражеский корабль!'

        elif hit_status is Cell.miss_repeated:
            message = 'Ты уже попал в это место, попробуй ещё раз'

        else:
            message = 'Ошибка хода игрока'
            console_manager.raise_wrong_hit_status(hit_status, hit_x, hit_y, message)

        if hit_status is Cell.damaged_ship or hit_status is Cell.destroyed_ship:
            message = f'{message} и ходит ещё раз.'

        print(message, end=' ')
        console_manager.press_enter()

        if not Board.board_ai:
            is_player_turn = False
            is_game = False
            return

    ai.make_turn()

    if not Board.board_player:
        is_game = False


if __name__ == "__main__":
    while is_intro:
        intro()

    while is_game:
        game()

    if not Board.board_ai:
        message = 'Ты победил! Ты уничтожил все вражеские корабли!'
    elif not Board.board_player:
        message = 'Ты потерпел поражение. Все корабли уничтожены!'
    else:
        message = None

#    Board.is_monitoring = True
    Board.print_boards()

    console_manager.press_enter(message=message, action='Выход')

