from random import randint  # Подгружаем (импортируем) генерацию случайных чисел


#  Создаем класс игрового поля
class Field:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.count = 0  # Количество пораженных кораблей
        self.field = [["O"] * size for _ in range(size)]
        self.busy = []  # Точки занятые кораблями (хранение)
        self.ships = []

    def add_ship(self,
                 ship):  # Размещение кораблей (учитывая, что точка не занята, а если это так, то срабатывает исключение)
        for d in ship.fields:
            if self.out(d) or d in self.busy:
                raise FieldWrongShipGame()
        for d in ship.fields:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)  # Добавляем список собственных кораблей
        self.contour(ship)  # Обводим корабли по контуру

    #  Границы кораблей (вокруг самих кораблей, так как по правилам, корабли не должны соприкосаться друг с другом)
    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.fields:
            for dx, dy in near:
                cur = Сomparison(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][
                            cur.y] = "."  # Символ ввиде точки, показывающий пользователю, что точка занята
                    self.busy.append(cur)

    #  Вывод кораблей на доску
    def __str__(self):
        res = ""
        res += "  |  1  |  2  |  3  |  4  |  5  |  6  |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} |  " + "  |  ".join(row) + "  |"
        if self.hid:
            res = res.replace("■", "O")
        return res

    #  Ограничение выстрелов в пределах игрового поля
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    #  Стрельба по доске
    def shot(self, d):
        if self.out(d):
            raise ShotOutOfBounds()
        if d in self.busy:
            raise RepeatInput()
        self.busy.append(d)
        for ship in self.ships:
            if d in ship.fields:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"  # Корабль поражен
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)  # Контур пораженного корабля
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True
        self.field[d.x][d.y] = "."
        print("Мазила!")
        return False

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)


#  Игра, генерация игровых полей (компьютера и пользователя)
class Game:
    player_1 = input('Давайте знакомиться! Меня зовут Валли. Как Ваше имя? \n')

    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1,
                1]  # На каждой доске (у ИИ и у игрока) должно находится следующее количество кораблей: 1 корабль на 3 клетки, 2 корабля на 2 клетки, 4 корабля на одну клетку.
        board = Field(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Сomparison(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except FieldWrongShipGame:
                    pass
        board.begin()
        return board

    #  Приветствие
    def greet(self):
        print(f'Приятно познокомиться, {Game.player_1}! Предлагаю сыграть со мной в игру "МОРСКОЙ БОЙ".')
        print("Выигрывает тот, кто поразит первым все корабли противника.")
        print(
            "Формат ввода координат числовой: x - отвечает за горизонталь, y - отвечает за вертикаль. Координаты вводятся через пробел.")

    #  Игровой цикл
    def loop(self):
        num = 0  # Счётчик ходов
        while True:
            print(f"{Game.player_1}, это Ваше игровое поле:")
            print(self.us.board)
            print("Игровое поле Валли:")
            print(self.ai.board)
            if num % 2 == 0:
                repeat = self.us.move()
            else:
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():  # Количиство пораженых кораблей равно количеству кораблей на доске
                print(f"{Game.player_1}, Вы выиграли!!!! Поздравляю!!! Давно меня не обыгрывали!!!")
                break

            if self.us.board.defeat():
                print(f"ХА - мне жаль, но Вы {Game.player_1}, продули!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


#  Создаем класс корабля
class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def fields(self):
        ship_fields = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y
            if self.o == 0:
                cur_x += i
            elif self.o == 1:
                cur_y += i
            ship_fields.append(Сomparison(cur_x, cur_y))
        return ship_fields

    def shooten(self, shot):
        return shot in self.fields

    #  Класс игрока


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
            except FeaturesGame as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Сomparison(randint(0, 5), randint(0, 5))
        print(f"Мой ход: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input(f"{Game.player_1}, Ваш ход:\n ").split()

            if len(cords) != 2:
                print(f"{Game.player_1}, Введите две координаты хода через пробел:\n")
                continue
            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print(f"{Game.player_1}, введите пожалуйста числа:\n")
                continue
            x, y = int(x), int(y)
            return Сomparison(x - 1, y - 1)


#  Создаем классы исключений
class FeaturesGame(Exception):  # Общий класс исключений, содержащий все исключения
    pass


class ShotOutOfBounds(FeaturesGame):
    def __str__(self):
        return f"{Game.player_1}, Вы пытаетесь выстрелить за пределы поля!"


class RepeatInput(FeaturesGame):
    def __str__(self):
        return "Капитан! Мы уже палили по этим координатам! Давай другие цифры!"


class FieldWrongShipGame(FeaturesGame):  # Исключение для размещения кораблей
    pass


#  Создаём класс сравнения точек на полях (ПК и игрока)
class Сomparison:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):  # реальный игрок
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Сomparison({self.x}, {self.y})"


game = Game()
game.start()