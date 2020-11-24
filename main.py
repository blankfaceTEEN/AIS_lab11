import math
import os
import random
import sys

from PyQt5.QtGui import QFont, QIcon, QIntValidator
from PyQt5.QtWidgets import QApplication, QPushButton, QMainWindow, QLineEdit, QLabel, QDialog


class Result(QDialog):
    winner = ''

    def __init__(self, text):
        super(Result, self).__init__()
        self.winner = text
        self.initUI()

    def initUI(self):
        self.setGeometry(500, 500, 135, 80)
        self.setWindowTitle("Крестики-Нолики")
        self.setWindowIcon(QIcon('favicon.png'))
        self.l1 = QLabel(self)
        self.l1.setGeometry(20, 10, 100, 20)
        self.l1.setText(self.winner)
        things = []
        f = open('result.txt')
        for line in f:
            things.append(line)
        f.close()
        number = things[0].split('\n')
        try_count = int(number[0])
        score = int(things[1])
        self.l2 = QLabel(self)
        self.l2.setGeometry(20, 30, 100, 20)
        self.l2.setText('Попыток: ' + str(try_count))
        self.l3 = QLabel(self)
        self.l3.setGeometry(20, 50, 100, 20)
        self.l3.setText('Побед: ' + str(score))


class Menu(QMainWindow):
    def __init__(self):
        super(Menu, self).__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, 200, 160)
        self.setWindowTitle("Крестики-Нолики")
        self.setWindowIcon(QIcon('favicon.png'))
        self.l1 = QLabel(self)
        self.l1.setGeometry(20, 20, 65, 20)
        self.l1.setText('Размерность')
        self.e1 = QLineEdit(self)
        self.e1.setValidator(QIntValidator())
        self.e1.setGeometry(90, 20, 90, 20)
        self.e1.setText('3')
        self.b1 = QPushButton(self)
        self.b1.setGeometry(20, 45, 160, 50)
        self.b1.setText('Продолжить')
        self.b1.clicked.connect(self.load)
        self.b2 = QPushButton(self)
        self.b2.setGeometry(20, 100, 160, 50)
        self.b2.setText('Новая игра')
        self.b2.clicked.connect(self.new)

    def new(self):
        self.w = Game(self.e1.text(), False)
        self.w.show()
        self.hide()

    def load(self):
        self.w = Game(self.e1.text(), True)
        self.w.show()
        self.hide()


class Game(QMainWindow):
    value = 'O'
    board = []
    winner = 'XO'
    end = False
    size = 3
    time = 0
    saved = False
    try_count = 0
    score = 0

    def __init__(self, new_size, new_saved):
        super(Game, self).__init__()
        self.saved = new_saved
        if self.saved:
            f = open('save.txt')
            data = f.read()
            f.close()
            self.size = int(math.sqrt(len(data)))
        else:
            self.size = int(new_size)
        things = []
        f = open('result.txt', 'r+')
        if os.stat('result.txt').st_size == 0:
            f.write('0\n')
            f.write('0')
        for line in f:
            things.append(line)
        f.close()
        number = things[0].split('\n')
        self.try_count = int(number[0])
        self.score = int(things[1])
        print('Продолжение игры? Ответ:', self.saved)
        print('Размерность: ', self.size)
        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, self.size * 100, self.size * 100)
        self.setWindowTitle("Крестики-Нолики")
        self.setWindowIcon(QIcon('favicon.png'))

        for i in range(self.size):
            buffer = []
            for j in range(self.size):
                buffer.append((QPushButton(self)))
            self.board.append(buffer)

        for i in range(self.size):
            for j in range(self.size):
                self.board[i][j].setGeometry(90 * i + 20, 90 * j + 20, 80, 80)
                self.board[i][j].setFont(QFont(QFont('Times', 17)))
                self.board[i][j].clicked.connect(self.move)

        if self.saved:
            f = open('save.txt')
            data = f.read()
            f.close()
            h = 0
            for i in range(self.size):
                for j in range(self.size):
                    self.board[i][j].setText(data[h])
                    if self.board[i][j].text() == 'X' or self.board[i][j].text() == 'O':
                        self.board[i][j].setEnabled(False)
                    h += 1

    def move(self, button):
        if self.value == 'X':
            self.value = 'O'
        else:
            self.value = 'X'
        button = self.sender()
        button.setText(self.value)
        button.setEnabled(False)

        self.time += 1
        if self.time >= 5:
            self.check(self.board)
        self.ai()
        self.time += 1
        if self.time >= 1:
            self.check(self.board)

    def empty_cells(self):
        state = []
        for i in range(self.size):
            for j in range(self.size):
                buffer = []
                if self.board[i][j].text() != 'X' and self.board[i][j].text() != 'O':
                    buffer.append(i)
                    buffer.append(j)
                    state.append(buffer)
        return state

    def ai(self):
        available_cells = self.empty_cells()
        if len(available_cells) > 0:
            random_move = random.choice(available_cells)
            x = random_move[0]
            y = random_move[1]
            if self.value == 'X':
                self.value = 'O'
            else:
                self.value = 'X'
            self.board[x][y].setText(self.value)
            self.board[x][y].setEnabled(False)

    def check(self, board):
        # По столбцу
        scores = 0
        out = 'XO'
        for x in range(self.size):
            for y in range(self.size - 1):
                if board[x][y].text() == board[x][y + 1].text() and board[x][y].text() != '':
                    scores += 1
                    out = board[x][y].text()
            if scores == self.size - 1:
                if out == 'X':
                    self.winner = "X"
                elif out == 'O':
                    self.winner = "O"
                self.end = True
                break
            scores = 0

        # По строке
        scores = 0
        out = 'XO'
        for y in range(self.size):
            for x in range(self.size - 1):
                if board[x][y].text() == board[x + 1][y].text() and board[x][y].text() != '':
                    scores += 1
                    out = board[x][y].text()
            if scores == self.size - 1:
                if out == 'X':
                    self.winner = "X"
                elif out == 'O':
                    self.winner = "O"
                self.end = True
                break
            scores = 0

        # Левая диагональ
        scores = 0
        out = 'XO'
        for x in range(self.size - 1):
            for y in range(self.size - 1):
                if x == y:
                    if board[x][y].text() == board[x + 1][y + 1].text() and board[x][y].text() != '':
                        scores += 1
                        out = board[x][y].text()
            if scores == self.size - 1:
                if out == 'X':
                    self.winner = "X"
                elif out == 'O':
                    self.winner = "O"
                self.end = True
                break

        # Правая диагональ
        scores = 0
        out = 'XO'
        for y in range(self.size - 1):
            for x in range(self.size - 1, 0, -1):
                if y == abs(x - (self.size - 1)):
                    if board[x][y].text() == board[x - 1][y + 1].text() and board[x][y].text() != '':
                        scores += 1
                        out = self.board[x][y].text()
            if scores == self.size - 1:
                if out == 'X':
                    self.winner = "X"
                elif out == 'O':
                    self.winner = "O"
                self.end = True
                break

        if self.end or self.time == self.size ** 2:
            if self.winner == 'X':
                text = "Крестики победили!"
            elif self.winner == 'O':
                text = "Нолики победили!"
            else:
                text = "Ничья!"
            self.result(text)
            self.reset()

    def reset(self):
        self.value = 'X'
        self.winner = 'X'
        self.end = False
        self.time = 0
        for buttons in self.board:
            for button in buttons:
                button.setEnabled(True)
                button.setText("")

    def result(self, text):
        self.try_count += 1
        if self.winner == 'X':
            self.score += 1
        self.save_result()
        self.w = Result(text)
        self.w.show()
        self.close()

    def save(self):
        text_file = open("save.txt", "w")
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j].text() == 'O':
                    text_file.write('O')
                elif self.board[i][j].text() == 'X':
                    text_file.write('X')
                else:
                    text_file.write(' ')
        text_file.close()

    def save_result(self):
        text_file = open("result.txt", "w")
        text_file.write(str(self.try_count) + '\n')
        text_file.write(str(self.score))
        text_file.close()

    def closeEvent(self, event):
        self.save()


def menu():
    app = QApplication(sys.argv)
    m = Menu()
    m.show()
    sys.exit(app.exec_())


menu()
