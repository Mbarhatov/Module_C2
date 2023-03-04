from random import randint


# Собственный тип данных "точка"
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):  # метод отвечает за сравнения двух объектов, есть ли точка в списке
        return self.x == other.x and self.y == other.y

    def __repr__(self):  # метод отвечает за вывод точек
        return f"Dot ({self.x}, {self.y})"


# Собственные классы исключений
class BoardException(Exception):  # общией (родительский) клас содержит все остальные виды исключений
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


# Класс "Корабль"
class Ship:
    def __init__(self, bow, l, o):  # Конструктор корабля
        self.bow = bow  # кординаты носа корабля
        self.l = l  # длинна
        self.o = o  # горизонталь (0) / вертикаль (1)
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:  # корабль по горизонтали
                cur_x += i

            elif self.o == 1:  # Корабль по вертикали
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot):  # метод показывает попали мы в корабль или нет
        return shot in self.dots


# Класс "Игровое поле"
class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0  # Колличество пораженных корабдей

        self.field = [["O"] * size for _ in range(size)]  # сетка

        self.busy = []  # список хранятся занятые кораблем или при стрельбе куда был произведен выстрел
        self.ships = []  # список кораблей доски

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"  # выводим номер строки и через метод join клетки строки

        if self.hid:  # если метод hid True заменяем символ "■" на "O"
            res = res.replace("■", "O")
        return res

    def out(self, d):  # метод определяет находится ли точка за пределами доски
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    # Контур корабля и добавление его на доску
    def contour(self, ship, verb=False):  # точки вокруг корабля
        near = [(-1, -1), (-1, 0), (-1, 1),
                (0, -1), (0, 0), (0, 1),
                (1, -1), (1, 0), (1, 1)
                ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):  # метод для размещения корабля
        for d in ship.dots:
            if self.out(d) or d in self.busy:  # проверяет, чтобы точки не выходили за границы и не были заняты
                raise BoardWrongShipException()  # выводит ошибку
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    # Стрельба по доске
    def shot(self, d):
        if self.out(d):
            raise BoardOutException()  # если выстрел выходит за границы поля, выводится исключения

        if d in self.busy:
            raise BoardUsedException()  # если выстрел в занятую точку, выводится исключения

        self.busy.append(d)  # вносим в список, точка теперь занята

        # Проходим по списку короблей
        for ship in self.ships:
            if d in ship.dots:  # если было поподание уменьшаем жизнь и ставим "X"
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:  # в случае уничтожения прибавляем в счетчике и проводим контур
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:  # корабль ранен, повторяем ход
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."  # ставим "." и обозначаем, что выстрел произведен "Мимо!"
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []

    def defeat(self):  # метод проверяет колличество кораблей на доске
        return self.count == len(self.ships)


# Класс "Игрок"
class Player:
    def __init__(self, board, enemy):  # аргументы передаваемые для доски
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):  # в бесконечном цикле делаем выстрел и игрок и компьютер
        while True:
            try:
                target = self.ask()  # просим игроков дать кординаты выстрела
                repeat = self.enemy.shot(target)  # делаем выстрел
                return repeat
            except BoardException as e:
                print(e)


# Классы "игрок-компьютер" , "игрок-пользователь"
class AI(Player):  # Класс компьютера
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))  # случайно генерируем точку от 0 до 5
        m = Board()
        if d in m.ships:
            print("dfdsfdf")
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):  # Класс пользователя
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()  # запрос кординат

            if len(cords) != 2:  # проверка, введены ли две кординаты
                print(" Введите 2 координаты!")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):  # проверка на числа
                print("Введите число! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)  # возврат кординат


# Класс "игра" и генерация досок
class Game:
    def __init__(self, size=6):  # Конструктор доски
        self.size = size
        pl = self.random_board()  # доска для игрока
        co = self.random_board()  # доска для комьютера
        co.hid = True  # скрываем растоновку кораблей от игрока True/False будем видеть

        # Создаем игроков
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]  # Список кораблей
        board = Board(size=self.size)  # создаем доску
        attempts = 0
        for l in lens:  # раставляем корабли
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)  # Если прошло все хорошо, ставим корабль
                    break
                except BoardWrongShipException:  # если произашла ошибка повторяем операцию занова
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    # Конструктор и приветствие
    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def print_bords(self):
        print("-" * 20)
        print("Доска пользователя:")
        print(self.us.board)
        print("-" * 20)
        print("Доска компьютера:")
        print(self.ai.board)
        print("-" * 20)

    # Игровой цикл
    def loop(self):
        num = 0  # номер хода
        while True:
            self.print_bords()
            if num % 2 == 0:  # если четное ход пользователя
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1  # при попадание уменьшаем на еденицу, чтобы ход остался у того же игрока

            if self.ai.board.defeat():  # проверка количества кораблей на доске
                self.print_bords()
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.defeat():  # проверка количества кораблей на доске
                self.print_bords()
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1  # счет хода

    # Метод 'start'
    def start(self):
        self.greet()
        self.loop()


# Запуск игры
g = Game()
g.start()