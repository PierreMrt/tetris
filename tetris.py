from random import randint
from functools import partial
import os
import time
import tkinter as tk
import pickle
import winsound

from functions import *


DIR_PATH = os.path.dirname(os.path.realpath(__file__))


class MainFrame(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)

        self.main_window = master
        self.main_window.resizable(width=False, height=False)
        self.main_window.title('Tetris')

        # Compute screen width and height and calculate optimal position for the main_window
        width = int((self.main_window.winfo_screenwidth() - 522) / 2)
        height = int((self.main_window.winfo_screenheight() - 780) / 2)
        self.main_window.geometry(f'522x740+{width}+{height}')

        self.menu_frame = MenuFrame(self.main_window)


class MenuFrame(tk.Frame):

    def __init__(self, main_window):

        self.bg_color = 'black'
        self.fg_color = 'white'
        self.myfont = ('Comic Sans MS', 20)

        self.main_window = main_window
        self.main_window.config(bg=self.bg_color)

        self.image = tk.PhotoImage(file=DIR_PATH + '/bg_image.png')
        background_label = tk.Label(self.main_window, image=self.image)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.menu_frame = tk.Frame(self.main_window, bg=self.bg_color)
        self.menu_frame.grid(row=0, column=2, padx=140, pady=180)

        button_start = tk.Button(self.menu_frame, text='NEW GAME', command=self.new_game)
        button_start.grid(row=1, pady=5)
        self.config_button(button_start)

        button_score = tk.Button(self.menu_frame, text='HIGH SCORES', command=self.display_score)
        button_score.grid(row=2, pady=5)
        self.config_button(button_score)

        button_command = tk.Button(self.menu_frame, text='COMMANDS', command=self.command_label)
        button_command.grid(row=3, pady=5)
        self.config_button(button_command)

        button_exit = tk.Button(self.menu_frame, text='EXIT', command=self.main_window.quit)
        button_exit.grid(row=4, pady=5)
        self.config_button(button_exit)

        button_sound = tk.Button(self.menu_frame)
        button_sound.grid(row=5)
        self.config_button(button_sound)
        play_music('on', button=button_sound)
        button_sound.config(command=partial(play_music, 'off', button=button_sound))

    def config_button(self, button):
        button.config(bg=self.bg_color,
                      fg=self.fg_color,
                      activeforeground='orange',
                      activebackground=self.bg_color,
                      font=self.myfont,
                      width=15,
                      relief=tk.SUNKEN,
                      bd=0,
                      cursor='hand2')

    def new_game(self):
        self.menu_frame.destroy()
        GameFrame(self.main_window, self.menu_frame)

    def command_label(self):
        text = """LEFT to move block to the left\n
RIGHT to move block to the right\n
DOWN to increase block dropping speed\n
R to rotate block
        """
        self.menu_frame.destroy()
        command_frame = tk.Frame(self.main_window, bg=self.bg_color)
        command_frame.grid(padx=70, pady=200)
        label_command = tk.Label(command_frame, text=text, bg=self.bg_color, fg=self.fg_color, font=('Comic Sans MS', 14))
        label_command.grid()

        button_command = tk.Button(command_frame, text='BACK TO MENU', bg=self.bg_color, command=partial(self.back_to_menu, command_frame))
        button_command.grid(pady=40, sticky='nswe')
        button_command.grid_propagate(0)
        self.config_button(button_command)
        button_command.config(font=('Comic Sans MS', 14, 'underline'))

    def display_score(self):

        try:
            list_score = read_score()
        except FileNotFoundError:
            list_score = []

        text = ''
        for index in range(0, 10):
            nb = index + 1
            try:
                text += f'{nb}. {list_score[index][0]}: {list_score[index][1]}\n'
            except IndexError:
                text += f'{nb}.\n'

        self.menu_frame.destroy()
        score_frame = tk.Frame(self.main_window, bg=self.bg_color, width=522)
        score_frame.grid(padx=120, pady=170)
        label_score = tk.Label(score_frame, text=text, bg=self.bg_color, fg=self.fg_color,
                               font=('Comic Sans MS', 14), justify=tk.LEFT)
        label_score.grid(sticky='w')

        button_command = tk.Button(score_frame, text='BACK TO MENU', bg=self.bg_color,
                                   command=partial(self.back_to_menu, score_frame))
        button_command.grid(pady=10, padx=50)
        self.config_button(button_command)
        button_command.config(font=('Comic Sans MS', 14, 'underline'))

    def back_to_menu(self, origin_frame):
        origin_frame.destroy()
        MenuFrame(self.main_window)


class GameFrame(tk.Frame):

    def __init__(self, main_window, menu_frame):
        self.main_window = main_window
        self.menu_frame = menu_frame

        try:
            background_label = self.main_window.place_slaves()[0]
            background_label.destroy()
        except IndexError:
            pass

        self.bg_color = 'black'
        self.fg_color = 'white'
        self.main_window.config(bg='gray4')
        self.main_window.bind('<Left>', self.left_key)
        self.main_window.bind('<Right>', self.right_key)
        self.main_window.bind('<Down>', self.down_key)
        self.main_window.bind('<r>', self.rotate_key)

        self.key_event = 0

        self.play_frame = tk.Frame(self.main_window, width=320, height=680, bg=self.bg_color)
        self.play_frame.grid(padx=(20, 10), pady=20, sticky='nswe')
        self.play_frame.grid_propagate(0)

        self.info_frame = tk.Frame(self.main_window, width=150, height=422, bg='gray4', relief=tk.FLAT)
        self.info_frame.grid(row=0, column=1, pady=20, sticky='nswe')
        self.info_frame.grid_propagate(0)
        self.frame_next = tk.Frame(self.info_frame, bg='gray4')

        self.block_list = ['T', 'I', 'L', 'L_inv', 'Z', 'Z_inv', 'O']
        self.list_next_block = [self.block_list[randint(0, 6)], self.block_list[randint(0, 6)]]
        self.score = 0

        self.load_info()
        self.load_play()

        self.start_game()

    def load_play(self):
        for x in range(0, 10):
            for y in range(0, 20):
                label = tk.Label(self.play_frame, text=' ', bg=self.bg_color, width=4, height=2, bd=1, relief=tk.SOLID)
                label.grid(row=y, column=x)

    def load_info(self):
        label_score = tk.Label(self.info_frame, text=f'SCORE  {self.score}')
        label_score.grid(row=0, column=0, sticky='w', pady=(5, 30), padx=5)
        label_score.config(bg='gray4', fg=self.fg_color, font=('Comic Sans MS', 14))

        label_next = tk.Label(self.info_frame, text='NEXT BLOCK')
        label_next.grid(row=1, column=0, sticky='w', padx=5)
        label_next.config(bg='gray4', fg=self.fg_color, font=('Comic Sans MS', 14))

        self.frame_next.grid(row=2, column=0, sticky='w', pady=10, padx=20)

        for row in range(0, 4):
            for column in range(0, 4):
                label = tk.Label(self.frame_next, text=' ', bg='gray4', width=2, height=1, bd=0, relief=tk.FLAT)
                label.grid(row=row, column=column, padx=1, pady=1)

        positions, color = get_positions(self.list_next_block[1])
        for elt in positions[0]:
            label = self.frame_next.grid_slaves(- 1 * (elt[0]), 3 - 1 * elt[1])[0]
            label.config(bg=color, bd=0, relief=tk.FLAT)

        menu_button = tk.Button(self.info_frame, text='MENU', command=self.back_to_menu)
        menu_button.grid(row=3, column=0, sticky='', pady=(90, 20), padx=20)
        menu_button.config(bg='gray4',
                           fg=self.fg_color,
                           bd=0,
                           font=('Comic Sans MS', 14),
                           relief=tk.SUNKEN,
                           activeforeground='orange',
                           activebackground='gray4',
                           cursor='hand2')

        restart_button = tk.Button(self.info_frame, text='RESTART', command=self.restart_game)
        restart_button.grid(row=4, column=0, padx=20, sticky='')
        restart_button.config(bg='gray4',
                              fg=self.fg_color,
                              bd=0,
                              font=('Comic Sans MS', 14),
                              relief=tk.SUNKEN,
                              activeforeground='orange',
                              activebackground='gray4',
                              cursor='hand2')

        button_sound = tk.Button(self.info_frame, text='sound on')
        button_sound.grid(row=5, pady=5)
        button_sound.config(bg='gray4',
                            fg=self.fg_color,
                            bd=0,
                            font=('Comic Sans MS', 12),
                            relief=tk.SUNKEN,
                            activeforeground='orange',
                            activebackground='gray4',
                            cursor='hand2',
                            command=partial(play_music, 'off', button=button_sound))

    def back_to_menu(self):
        self.play_frame.destroy()
        self.info_frame.destroy()
        MenuFrame(self.main_window)
        self.key_event = 'end'

    def restart_game(self):
        self.play_frame.destroy()
        self.info_frame.destroy()
        GameFrame(self.main_window, self.menu_frame)
        self.key_event = 'end'

    def start_game(self):
        game_continue = True
        while game_continue:
            block, self.list_next_block = get_next_block(self.block_list, self.list_next_block)
            positions, color = get_positions(block)

            row0 = 0
            column0 = 4

            game_continue, end = self.block_drop(positions, color, row0, column0)

        if self.score > 0 and end is False:
            check_high_scores(self.score, self.main_window)

    def block_drop(self, positions, color, row, column):
        index_rotation = 0
        game_continue = True
        block_dropping = True
        row0 = row
        column0 = column
        while block_dropping:

            self.change_color(self.bg_color, positions[index_rotation], row0 - 1, column0)
            self.change_color(color, positions[index_rotation], row0, column0)
            self.play_frame.update()

            row0, column0, index_rotation, end = self.check_event(color, positions, index_rotation, row0, column0)

            if end:
                game_continue = False
                break
            row0 += 1
            if row0 > 19:
                self.fix_block(positions[index_rotation], color, row0 - 1, column0)
                removed_lines = self.remove_finished_rows(0, 0)
                if removed_lines > 0:
                    self.score += 300 * (removed_lines - 1) + 100
                    self.load_info()
                break

            move_possible = self.check_move(positions[index_rotation], row0, column0)
            if move_possible is False:
                self.fix_block(positions[index_rotation], color, row0 - 1, column0)
                block_dropping = False
                removed_lines = self.remove_finished_rows(0, 0)
                if removed_lines > 0:
                    self.score += 300 * (removed_lines - 1) + 100
                    self.load_info()
                defeat = check_defeat(positions[index_rotation], row0 - 1)
                if defeat:
                    game_continue = False

        self.key_event = 0

        return game_continue, end

    def remove_finished_rows(self, count_finished_rows, count_iterations):
        for row in range(19, 0, - 1):
            row_full = True
            for i in range(0, 10):
                if self.play_frame.grid_slaves(row, i)[0].cget('text') != '':
                    row_full = False
                    break
            if row_full:
                count_finished_rows += 1
                for line in range(row, 0, - 1):
                    for i in range(0, 10):

                        text = self.play_frame.grid_slaves(line - 1, i)[0].cget('text')
                        color = self.play_frame.grid_slaves(line - 1, i)[0].cget('bg')

                        label = self.play_frame.grid_slaves(line, i)[0]
                        label.config(text=text, bg=color)

                        label = self.play_frame.grid_slaves(line - 1, i)[0]
                        label.config(text=' ', bg=self.bg_color)

                count_iterations += 1
                count_iterations = self.remove_finished_rows(count_finished_rows, count_iterations)

        self.load_info()

        return count_iterations

    def check_event(self, color, positions, index_rotation, row0, column0):
        end = False
        iteration = 50
        if self.key_event == 'd':
            iteration = 5

        for i in range(iteration):
            if self.key_event == 'end':
                end = True
                break
            if self.key_event == 'l':
                increment = - 1
                self.key_event = 0

            elif self.key_event == 'r':
                increment = 1
                self.key_event = 0

            else:
                increment = 0

            column0 += increment

            if column0 < 0:
                column0 -= increment

            if self.key_event == 'rotate':
                index_temp = index_rotation + 1
                if index_temp >= len(positions):
                    self.change_color(self.bg_color, positions[index_rotation], row0, column0)
                    index_rotation = 0

                else:
                    move_possible = self.check_move(positions[index_temp], row0, column0)
                    if move_possible:
                        self.change_color(self.bg_color, positions[index_rotation], row0, column0)
                        index_rotation = index_temp
                self.key_event = 0

            try:
                move_possible = self.check_move(positions[index_rotation], row0, column0)
                if move_possible:
                    self.change_color(self.bg_color, positions[index_rotation], row0, column0 - increment)
                    self.change_color(color, positions[index_rotation], row0, column0)
                    self.play_frame.update()
                else:
                    column0 -= increment
            except IndexError:
                column0 -= increment

            time.sleep(0.01)

        return row0, column0, index_rotation, end

    def left_key(self, event):
        self.key_event = 'l'

    def right_key(self, event):
        self.key_event = 'r'

    def down_key(self, event):
        self.key_event = 'd'

    def rotate_key(self, event):
        self.key_event = 'rotate'

    def change_color(self, color, positions, row_mod, column_mod):
        for elt in positions:
            row = elt[0] + row_mod
            column = elt[1] + column_mod
            try:
                label = self.play_frame.grid_slaves(row, column)[0]
                label.config(bg=color)
            except (tk.TclError, IndexError) as e:
                pass

    def check_move(self, positions, row0, column0):
        move_possible = True
        for elt in positions:
            row = row0 + elt[0]
            column = column0 + elt[1]
            try:
                if self.play_frame.grid_slaves(row, column)[0].cget('text') == '':
                    move_possible = False
                    break
            except tk.TclError:
                pass
            except IndexError:
                move_possible = False
                break

        return move_possible

    def fix_block(self, positions, color, row0, column0):
        for elt in positions:
            row = row0 + elt[0]
            column = column0 + elt[1]
            try:
                label = self.play_frame.grid_slaves(row, column)[0]
                label.config(text='', fg=color)
            except tk.TclError:
                pass


class NamePrompt(tk.Frame):

    def __init__(self, score, list_score, main_window):

        self.score = score
        self.list_score = list_score

        self.main_window = main_window

        bg_color = 'SkyBlue4'
        fg_color = 'white'
        self.prompt_window = tk.Tk()

        width = int((self.prompt_window.winfo_screenwidth() - 210) / 2)
        height = int((self.prompt_window.winfo_screenheight() - 150) / 2)

        self.prompt_window.config(bg=bg_color)
        self.prompt_window.geometry(f'210x120+{width}+{height}')
        self.prompt_frame = tk.Frame(self.prompt_window, bg=bg_color)
        self.prompt_frame.grid(padx=20)

        my_font = ('Comic Sans MS', 10)

        label = tk.Label(self.prompt_frame, text='Top 10 ! Tell me your name\n'
                         '(2 - 10 characters)', font=my_font, bg=bg_color, fg=fg_color)
        label.grid(row=0, columnspan=2, pady=10)

        self.entry = tk.Entry(self.prompt_frame)
        self.entry.grid(row=1, column=0, padx=(5, 5), pady=10)

        button = tk.Button(self.prompt_frame, text='OK', font=my_font, bg=bg_color, fg=fg_color, bd=0, relief=tk.SUNKEN,
                           cursor='hand2', command=self.check_name)
        button.grid(row=1, column=1)

        self.prompt_window.mainloop()
        self.prompt_window.quit()

    def check_name(self):
        name = self.entry.get()
        expression = r'^[A-Za-z0-9 ]{2,10}$'

        if re.search(expression, name) is not None:
            self.prompt_window.destroy()
            self.add_score(name)

    def add_score(self, name):
        self.list_score.append((name, self.score))
        list_score = sorted(self.list_score, key=lambda tup: tup[1], reverse=True)
        if len(list_score) > 10:
            del list_score[-1]
        self.write_score(list_score)
        self.score = 0

    @staticmethod
    def write_score(list_score):
        with open(DIR_PATH + '/data/score', 'wb+') as score_file:
            my_pickler = pickle.Pickler(score_file)
            my_pickler.dump(list_score)


if __name__ == '__main__':
    root = tk.Tk()
    app = MainFrame(master=root)
    app.mainloop()

