import tkinter as tk
from tkinter.messagebox import showinfo, showerror
from random import randint

class MyButton(tk.Button):
    """Класс отвечает за ячейки поля и наделяет их аргументами"""
    def __init__(self, master, row, col, *args, **kwargs):
        super().__init__(master, width=2, height=1, font='Calibri 10 bold', *args, **kwargs)
        self.row = row
        self.col = col
        self.is_mine = False
        self.is_open = False
        self.neighbours = ''


class MineSweeper:

    __COLORS_NUMBERS = {1: '#0000ff', 2: '#08a30f', 3: '#ff0000', 4: '#0f045c',
                        5: '#541d03', 6: '#069e8d', 7: '#72068a', 8: '#030000',
                        '': 'lightgrey'}

    IS_GAME_OVER = False
    IS_FIRST_CLICK = True
    window = tk.Tk()
    window.title("MineSweeper!")

    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.buttons = []
        self.create_buttons()
        MineSweeper.window.mainloop()

    def create_buttons(self):

        menubar = tk.Menu(MineSweeper.window)
        MineSweeper.window.config(menu=menubar)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label='Play again', command=self.reload)
        settings_menu.add_command(label='Parameters', command=self.create_settings_window)
        settings_menu.add_command(label='Exit', command=self.window.destroy)

        menubar.add_cascade(label='Settings', menu=settings_menu)

        for row in range(self.rows):
            self.buttons.append([])
            for col in range(self.cols):
                button = MyButton(MineSweeper.window, row=row, col=col)
                button.config(command=lambda btn=button: self.on_button_click(btn))
                button.bind("<Button-3>", func=self.right_click) #обработчик нажатия правой кнопки мыши
                button.grid(row=row, column=col, stick='NWES')
                self.buttons[row].append(button)

        for row in range(self.rows):
            tk.Grid.rowconfigure(MineSweeper.window, row, weight=1)
        for col in range(self.cols):
            tk.Grid.columnconfigure(MineSweeper.window, col, weight=1)

    def place_mines(self, exc_button):
        """Функция расставляет заданное количество мин случайным образом"""
        mines_placed = 0
        while mines_placed < self.mines:
            row = randint(0, self.rows - 1)
            col = randint(0, self.cols - 1)
            cell = self.buttons[row][col]
            if not cell.is_mine and row != exc_button.row and col != exc_button.col:
                cell.is_mine = True
                mines_placed += 1

    def calculate_neighbours(self):
        """Функция присваивает количество мин соседей для каждой клетки в атрибут mine"""
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.buttons[row][col]
                if not cell.is_mine:
                    cell.neighbours = self.count_neighbours(row, col)
                    if not cell.neighbours:
                        cell.neighbours = '' #если у клетки нет соседей мин, вместо возвращенного нуля, пустая строкуса

    def count_neighbours(self, row, col):
        """Функция считаеn количество мин соседей для заданной клетки"""
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == j == 0:
                    continue
                if 0 <= row + i < self.rows and 0 <= col + j < self.cols:
                    if self.buttons[row + i][col + j].is_mine:
                        count += 1
        return count

    def on_button_click(self, clicked_button):
        clicked_button.is_open = True

        if MineSweeper.IS_GAME_OVER:
            return

        if MineSweeper.IS_FIRST_CLICK:
            self.place_mines(exc_button=clicked_button) #вызов функции, чтобы расставить мины, исключая первую клетку
            self.calculate_neighbours() #вызов функции, чтобы посчитать мины соседи
            MineSweeper.IS_FIRST_CLICK = False
            clicked_button.config(bg='lightgrey')

        elif clicked_button.is_mine:
            clicked_button.config(text="*", state=tk.DISABLED, bg='red', disabledforeground='black')
            MineSweeper.IS_GAME_OVER = True
            self.show_game_over_message()
            self.show_all_mines()

        else:
            clicked_button.config(text=clicked_button.neighbours, bg='lightgrey',
                                  disabledforeground=self.__COLORS_NUMBERS[clicked_button.neighbours])
            if clicked_button.neighbours == '':
                self.open_neighbours(clicked_button)
        clicked_button.config(state=tk.DISABLED, relief=tk.SUNKEN)
        self.check_winning()

    def open_neighbours(self, clicked_button):
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if clicked_button.row + i >= 0 and clicked_button.row + i < self.rows and clicked_button.col + j >= 0 and clicked_button.col + j < self.cols:
                    neighbour_cell = self.buttons[clicked_button.row + i][clicked_button.col + j]
                    if not neighbour_cell.is_open:
                        self.on_button_click(neighbour_cell)

    def show_game_over_message(self):
        showinfo("Game Over", "You hit a mine!")

    def show_all_mines(self):
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.buttons[row][col]
                if cell.is_mine:
                    cell['text'] = '*'

    def reload(self):
        [child.destroy() for child in self.window.winfo_children()] # строка нужна, чтобы при изменении параметров в меньшую сторону, удалялись ненужные ячейки
        MineSweeper.IS_FIRST_CLICK = True
        MineSweeper.IS_GAME_OVER = False
        self.__init__(self.rows, self.cols, self.mines)

    def create_settings_window(self):
        win_settings = tk.Toplevel(self.window)
        win_settings.wm_title('Parameters')

        tk.Label(win_settings, text='Number of rows:').grid(row=0, column=0)
        rows_entry = tk.Entry(win_settings)
        rows_entry.insert(0, self.rows)
        rows_entry.grid(row=0, column=1, padx=20, pady=20)

        tk.Label(win_settings, text='Number of columns:').grid(row=1, column=0)
        columns_entry = tk.Entry(win_settings)
        columns_entry.insert(0, self.cols)
        columns_entry.grid(row=1, column=1, padx=20, pady=20)

        tk.Label(win_settings, text='Number of mines:').grid(row=2, column=0)
        mines_entry = tk.Entry(win_settings)
        mines_entry.insert(0, self.mines)
        mines_entry.grid(row=2, column=1, padx=20, pady=20)

        btn_apply = tk.Button(win_settings, text='Apply',
                              command=lambda: self.change_settings(rows_entry, columns_entry, mines_entry))
        btn_apply.grid(rows=3, column=0, columnspan=2, padx=10, pady=10)

    def change_settings(self, rows: tk.Entry, cols: tk.Entry, mines: tk.Entry):
        #добавить проверки
        self.rows = int(rows.get())
        self.cols = int(cols.get())
        self.mines = int(mines.get())
        self.reload() # при изменении параметров в меньшую сторону, клетки не размещаются пропорционально

    def right_click(self, event): #пишем event, чтобы функция отловила координаты нажатия
        if MineSweeper.IS_GAME_OVER:
            return
        cur_butten = event.widget
        if cur_butten['state'] == 'normal':
            cur_butten['state'] = 'disabled'
            cur_butten['text'] = '🚩'
            cur_butten['disabledforeground'] = 'red'
            cur_butten.is_open = True
        elif cur_butten['text'] == '🚩':
            cur_butten['text'] = ''
            cur_butten['state'] = 'normal'
            cur_butten.is_open = False
        self.check_winning()

    def check_winning(self):
        """Проверяем, открыты ли все клетки"""
        if all(self.buttons[row][col].is_open for row in range(self.rows) for col in range(self.cols)):
            self.show_winning_message()
            MineSweeper.IS_GAME_OVER = True

    def show_winning_message(self):
        showinfo("Winning", "Congratulations, all mines have been found!")

MineSweeper(10, 10, 10)