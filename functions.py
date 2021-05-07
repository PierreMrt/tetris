from random import randint
import pickle
from functools import partial
import re
import os
import tkinter as tk
from tetris import *


DIR_PATH = os.path.dirname(os.path.realpath(__file__))


def play_music(status, **kwargs):
    if status == 'on':
        winsound.PlaySound(DIR_PATH + '/data/Tetris.wav',
                           winsound.SND_LOOP + winsound.SND_ASYNC | winsound.SND_ALIAS)
        sound_command = 'off'

    elif status == 'off':
        winsound.PlaySound(None, winsound.SND_ASYNC)
        sound_command = 'on'

    if len(kwargs) > 0:
        kwargs['button'].config(text=f'sound {status}', command=partial(play_music, sound_command, button=kwargs['button']))


def get_positions(type):
    positions = []

    if type == "T":
        position1 = [
            (0, 0),
            (- 1, 0),
            (- 2, 0),
            (- 1, 1)]

        position2 = [
            (0, 2),
            (0, 1),
            (0, 0),
            (- 1, 1)]

        position3 = [
            (- 2, 1),
            (- 1, 1),
            (0, 1),
            (- 1, 0)]

        position4 = [
            (- 1, 0),
            (0, 1),
            (- 1, 1),
            (- 1, 2)]

        positions.append(position1)
        positions.append(position2)
        positions.append(position3)
        positions.append(position4)
        bg_color = 'medium orchid'

    if type == "I":
        position1 = [
            (0, 0),
            (- 1, 0),
            (- 2, 0),
            (- 3, 0)]

        position2 = [
            (0, 0),
            (0, 1),
            (0, 2),
            (0, 3)]

        positions.append(position1)
        positions.append(position2)
        bg_color = 'cornflower blue'

    if type == "L":
        position1 = [
            (0, 0),
            (- 1, 0),
            (- 2, 0),
            (0, 1)]

        position2 = [
            (0, 0),
            (0, 1),
            (0, 2),
            (- 1, 2)]

        position3 = [
            (- 2, 0),
            (0, 1),
            (- 1, 1),
            (- 2, 1)]

        position4 = [
            (0, 0),
            (- 1, 0),
            (- 1, 1),
            (- 1, 2)]

        positions.append(position1)
        positions.append(position2)
        positions.append(position3)
        positions.append(position4)
        bg_color = 'chocolate1'

    if type == "L_inv":
        position1 = [
            (0, 0),
            (0, 1),
            (- 1, 1),
            (- 2, 1)]

        position2 = [
            (- 1, 0),
            (- 1, 1),
            (0, 2),
            (- 1, 2)]

        position3 = [
            (0, 0),
            (- 1, 0),
            (- 2, 0),
            (- 2, 1)]

        position4 = [
            (0, 0),
            (- 1, 0),
            (0, 1),
            (0, 2)]

        positions.append(position1)
        positions.append(position2)
        positions.append(position3)
        positions.append(position4)
        bg_color = 'dodger blue4'

    if type == "Z":
        position1 = [
            (- 1, 0),
            (0, 1),
            (- 1, 1),
            (0, 2)]

        position2 = [
            (0, 0),
            (- 1, 0),
            (- 1, 1),
            (- 2, 1)]

        positions.append(position1)
        positions.append(position2)
        bg_color = 'firebrick1'

    if type == "Z_inv":
        position1 = [
            (0, 0),
            (0, 1),
            (- 1, 1),
            (- 1, 2)]

        position2 = [
            (- 1, 0),
            (- 2, 0),
            (0, 1),
            (- 1, 1)]

        positions.append(position1)
        positions.append(position2)
        bg_color = 'sea green'

    if type == "O":
        position1 = [
            (0, 0),
            (- 1, 0),
            (0, 1),
            (- 1, 1)]
        positions.append(position1)
        bg_color = 'goldenrod1'

    return positions, bg_color


def get_next_block(block_list, list_next_block):
    block = list_next_block[0]
    del list_next_block[0]

    next_block = block_list[randint(0, 6)]
    list_next_block.append(next_block)

    return block, list_next_block


def check_defeat(positions, row0):
    defeat = False
    for elt in positions:
        row = row0 + elt[0]
        if row < 0:
            defeat = True
            break

    return defeat


def read_score():
    with open(DIR_PATH + '/data/score', 'rb+') as score_file:
        my_pickler = pickle.Unpickler(score_file)
        list_score = my_pickler.load()

    return list_score


def check_high_scores(score, main_window):
    try:
        list_score = read_score()
    except FileNotFoundError:
        list_score = []
        NamePrompt(score, list_score, main_window)
    except EOFError:
        list_score = []

    if len(list_score) == 0:
        NamePrompt(score, list_score, main_window)
    else:
        for elt in list_score:
            if len(list_score) < 10 or score > elt[1]:
                NamePrompt(score, list_score, main_window)

            else:
                main_window.quit()
                root = tk.Tk()
                app = MainFrame(master=root)
                app.mainloop()
