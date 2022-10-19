from random import randint
# Группа классов для обработки исключительных ситуаций
class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass
# Вспомогательный класс для задания координат точки
class Dot:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


#Класс корабля
class Ship:
    def __init__(self, start_dot, len_ship, lives, direct):
        self.start = start_dot
        self.len_ship = len_ship
        self.direct = direct
        self.lives = lives

    @property
    def dots(self):
        list_dots = []
        if self.direct:
            list_dots = [Dot(self.start.x, i) for i in range(self.start.y, self.start.y + self.len_ship)]
        else:
            list_dots = [Dot(i, self.start.y) for i in range(self.start.x, self.start.x + self.len_ship)]
        return list_dots

    def shooten(self, shot):
        return shot in self.dots

# Класс доски
class Board:
    def __init__(self, hid = False):
        self.board_list = [ [" O"]*6 for _ in range(6) ]
        self.hid = hid
        self.count = 0
        self.ships = []
        self.busy = []

    def __str__(self):
        field_str = ''
        field_str += '   | 1 |  2 | 3  | 4  | 5  | 6 |'
        for i, row in enumerate(self.board_list):
            field_str += f"\n {i + 1} |" + " | ".join(row) + '|'
        if self.hid:
            field_str = field_str.replace("■", "O")
        return field_str
    def out_board(self, d):
        return not((0 <= d.x < 6) and (0 <= d.y < 6))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out_board(cur)) and cur not in self.busy:
                    if verb:
                        self.board_list[cur.x][cur.y] = " ."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out_board(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.board_list[d.x][d.y] = " ■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out_board(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.board_list[d.x][d.y] = "X "
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return True
                else:
                    print("Корабль ранен!")
                    return True

        self.board_list[d.x][d.y] = " T"
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []

# Класс игрока
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

# Класс компьютера
class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d

# Класс пользователя
class User(Player):
    def ask(self):
        while True:
            coords = input("Ваш ход(введите координаты корабля(1..6): ").split()

            if len(coords) != 2:
                print(" Введите 2 координаты в диапазоне 1..6! ")
                continue

            x, y = coords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)

# Класс игры
class Game:
    def __init__(self):
        pl = self.random_board()
        co = self.random_board()
        co.hid = False

        self.ai = AI(co, pl)
        self.us = User(pl, co)
    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board()
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, 6), randint(0, 6)), l, l,randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board1 = None
        while board1 is None:
            board1 = self.try_board()
        return board1

    def greet(self):
        print("-------------------")
        print(" Начнем  игру в морской бой ")
        print("-------------------")
        print(" Формат ввода для выстрелов: x y в диапазоне 1..6")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Доска компьютера:")
                print(self.ai.board)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)

                print("Доска пользователя:")
                print(self.us.board)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

# Ну что, сыграем?
g = Game()
g.start()