# Author: Sergio Machi
# Creation date: 11/Apr/2021
# Last edit: 16/Apr/2021

import time
import random
import numpy as np
import pygame as pg
from pygame.locals import *
from colorama import Fore, Style

# Pyreman
WINDOW_CAPTION = 'Pyreman'
# 1800*900
WINDOW_SIZE = (1800, 900)
# 100
BLOCK_SIZE = 100

BLOCK_TYPES = ('FIRE', 'GRASS', 'HOUSE', 'WATER')
PYREMAN_IMG_PATH = 'resources/pyreman.png'
TURNS = 15


class Pyreman:
    def __init__(self, parent_screen, row=0, col=0):
        self.parent_screen = parent_screen
        self.row = row
        self.col = col
        self.bombs = TURNS - 3

    def draw(self):
        block = pg.image.load(PYREMAN_IMG_PATH).convert_alpha()
        self.parent_screen.blit(block, (self.row * BLOCK_SIZE, self.col * BLOCK_SIZE))
        pg.display.flip()

        # Log.
        print(Fore.YELLOW + self.__str__() + Style.RESET_ALL)

    def bomb(self):
        if self.bombs != 0:
            self.bombs -= 1
            return True
        return False

    def move_up(self):
        if self.col != 0:
            self.col -= 1
        self.draw()

    def move_down(self):
        if self.col != int(WINDOW_SIZE[1] / BLOCK_SIZE) - 1:
            self.col += 1
        self.draw()

    def move_left(self):
        if self.row != 0:
            self.row -= 1
        self.draw()

    def move_right(self):
        if self.row != int(WINDOW_SIZE[0] / BLOCK_SIZE) - 1:
            self.row += 1
        self.draw()

    def __str__(self):
        return f'X: {self.row}, ' \
               f'Y = {self.col}, ' \
               f'Bombs left: {self.bombs}, ' \
               f'Turns: {TURNS}'


class Block:
    def __init__(self, block_type):
        self.block_type = block_type
        self.image_path = 'resources/' + block_type.lower() + '.png'
        self.is_destroyed = False
        self.is_in_danger = False

    def __str__(self):
        return f'Block type: {self.block_type.title()}, ' \
               f'Is it destroyed?: {self.is_destroyed}, ' \
               f'Is it in danger?: {self.is_in_danger}'


class City:
    def __init__(self, parent_screen):
        self.parent_screen = parent_screen

        self.city_matrix = np.zeros([
            int(WINDOW_SIZE[0] / BLOCK_SIZE),
            int(WINDOW_SIZE[1] / BLOCK_SIZE)
        ], dtype=object)

    def draw(self):
        for rowi in range(int(WINDOW_SIZE[0] / BLOCK_SIZE)):
            for coli in range(int(WINDOW_SIZE[1] / BLOCK_SIZE)):
                block = pg.image.load(self.city_matrix[rowi, coli].image_path).convert()
                self.parent_screen.blit(block, (rowi * BLOCK_SIZE, coli * BLOCK_SIZE))
        pg.display.flip()

    def build(self):
        for rowi in range(int(WINDOW_SIZE[0] / BLOCK_SIZE)):
            for coli in range(int(WINDOW_SIZE[1] / BLOCK_SIZE)):
                ran = random.randint(1, len(BLOCK_TYPES) - 1)
                self.city_matrix[rowi, coli] = Block(BLOCK_TYPES[ran])
        self.draw()

    def destroy_block(self, pyreman):
        is_destroyed = pyreman.bomb()

        if is_destroyed:
            self.city_matrix[pyreman.row, pyreman.col] = Block(BLOCK_TYPES[3])
            self.draw()
        pyreman.draw()

    def set_first_fire(self):
        row = random.randint(0, int(WINDOW_SIZE[0] / BLOCK_SIZE) - 1)
        col = random.randint(0, int(WINDOW_SIZE[1] / BLOCK_SIZE) - 1)
        self.city_matrix[row, col] = Block(BLOCK_TYPES[0])

        block = pg.image.load(self.city_matrix[row, col].image_path).convert()
        self.parent_screen.blit(block, (row * BLOCK_SIZE, col * BLOCK_SIZE))
        pg.display.flip()

    def expand_fire(self):
        self.set_danger()

        for rowi in range(int(WINDOW_SIZE[0] / BLOCK_SIZE)):
            for coli in range(int(WINDOW_SIZE[1] / BLOCK_SIZE)):
                if self.city_matrix[rowi, coli].is_in_danger:
                    self.city_matrix[rowi, coli] = Block(BLOCK_TYPES[0])
        self.draw()

    def set_danger(self):
        for rowi in range(int(WINDOW_SIZE[0] / BLOCK_SIZE)):
            for coli in range(int(WINDOW_SIZE[1] / BLOCK_SIZE)):

                if self.city_matrix[rowi, coli].block_type == BLOCK_TYPES[0]:

                    if rowi - 1 >= 0 and \
                            self.city_matrix[rowi - 1, coli].block_type != BLOCK_TYPES[0] and \
                            self.city_matrix[rowi - 1, coli].block_type != BLOCK_TYPES[3]:
                        self.city_matrix[rowi - 1, coli].is_in_danger = True

                    if rowi + 1 <= WINDOW_SIZE[0] / BLOCK_SIZE - 1 and \
                            self.city_matrix[rowi + 1, coli].block_type != BLOCK_TYPES[0] and \
                            self.city_matrix[rowi + 1, coli].block_type != BLOCK_TYPES[3]:
                        self.city_matrix[rowi + 1, coli].is_in_danger = True

                    if coli + 1 <= WINDOW_SIZE[1] / BLOCK_SIZE - 1 and \
                            self.city_matrix[rowi, coli + 1].block_type != BLOCK_TYPES[0] and \
                            self.city_matrix[rowi, coli + 1].block_type != BLOCK_TYPES[3]:
                        self.city_matrix[rowi, coli + 1].is_in_danger = True

                    if coli - 1 >= 0 and \
                            self.city_matrix[rowi, coli - 1].block_type != BLOCK_TYPES[0] and \
                            self.city_matrix[rowi, coli - 1].block_type != BLOCK_TYPES[3]:
                        self.city_matrix[rowi, coli - 1].is_in_danger = True

    def place_pyreman(self, pyreman):
        while True:
            row = random.randint(0, int(WINDOW_SIZE[0] / BLOCK_SIZE) - 1)
            col = random.randint(0, int(WINDOW_SIZE[1] / BLOCK_SIZE) - 1)

            if self.city_matrix[row, col].block_type == BLOCK_TYPES[2]:
                pyreman.row = row
                pyreman.col = col
                pyreman.draw()
                break


class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption(WINDOW_CAPTION)

        self.surface = pg.display.set_mode(WINDOW_SIZE)
        self.city = City(self.surface)
        self.city.build()
        self.city.set_first_fire()
        self.pyreman = Pyreman(self.surface)
        self.city.place_pyreman(self.pyreman)

    def run(self):
        running = True

        time_elapsed_since_last_action = 0
        clock = pg.time.Clock()

        while running:

            for event in pg.event.get():

                if event.type == KEYDOWN:
                    self.city.draw()

                    if event.key == K_LEFT:
                        self.pyreman.move_left()
                    if event.key == K_RIGHT:
                        self.pyreman.move_right()
                    if event.key == K_UP:
                        self.pyreman.move_up()
                    if event.key == K_DOWN:
                        self.pyreman.move_down()

                    if event.key == K_RETURN:
                        self.city.destroy_block(self.pyreman)

                    if event.key == K_ESCAPE:
                        running = False

                    print(Fore.LIGHTMAGENTA_EX + '-' * 35 + Style.RESET_ALL)

                elif event.type == QUIT:
                    running = False

            dt = clock.tick()
            time_elapsed_since_last_action += dt

            if time_elapsed_since_last_action > 1000:
                self.city.expand_fire()
                # Should this line be here or in a class?
                self.pyreman.draw()
                print('This line is executed every two seconds.')
                time_elapsed_since_last_action = 0

            time.sleep(0.1)


if __name__ == '__main__':
    game = Game()
    game.run()