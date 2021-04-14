import time
import random
import numpy as np
import pygame as pg
from pygame.locals import *
from colorama import Fore, Style  # Tracking purposes.

WINDOW_CAPTION = 'Pyreman'
WINDOW_SIZE = (1800, 900)  # 1800*900
BLOCK_SIZE = 100  # 100

BLOCK_TYPES = ('FIRE', 'GRASS', 'HOUSE', 'WATER')
PYREMAN_IMG_PATH = 'resources/pyreman.png'
TURNS = 15


class Pyreman:
    def __init__(self, parent_screen, row=0, col=0):
        self.parent_screen = parent_screen
        self.row = row
        self.col = col
        self.dynamites = TURNS - 3

    def draw(self):
        block = pg.image.load(PYREMAN_IMG_PATH).convert_alpha()
        self.parent_screen.blit(block, (self.row * BLOCK_SIZE, self.col * BLOCK_SIZE))
        pg.display.flip()
        print(Fore.YELLOW + f'Pyreman position: x={self.row}, y={self.col}' + Style.RESET_ALL)

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

    def build(self):
        for rowi in range(int(WINDOW_SIZE[0] / BLOCK_SIZE)):
            for coli in range(int(WINDOW_SIZE[1] / BLOCK_SIZE)):
                ran = random.randint(1, len(BLOCK_TYPES) - 1)
                self.city_matrix[rowi, coli] = Block(BLOCK_TYPES[ran])
        self.draw()

    def draw(self):
        for rowi in range(int(WINDOW_SIZE[0] / BLOCK_SIZE)):
            for coli in range(int(WINDOW_SIZE[1] / BLOCK_SIZE)):
                block = pg.image.load(self.city_matrix[rowi, coli].image_path).convert()
                self.parent_screen.blit(block, (rowi * BLOCK_SIZE, coli * BLOCK_SIZE))
        pg.display.flip()

    def set_first_fire(self):
        row = random.randint(0, int(WINDOW_SIZE[0] / BLOCK_SIZE) - 1)
        col = random.randint(0, int(WINDOW_SIZE[1] / BLOCK_SIZE) - 1)
        self.city_matrix[row, col] = Block(BLOCK_TYPES[0])

        block = pg.image.load(self.city_matrix[row, col].image_path).convert()
        self.parent_screen.blit(block, (row * BLOCK_SIZE, col * BLOCK_SIZE))
        pg.display.flip()
        print(Fore.RED + f'\nFirst fire position: x={row}, y={col}' + Style.RESET_ALL)

    def place_pyreman(self, pyreman):
        while True:
            row = random.randint(0, int(WINDOW_SIZE[0] / BLOCK_SIZE) - 1)
            col = random.randint(0, int(WINDOW_SIZE[1] / BLOCK_SIZE) - 1)

            if self.city_matrix[row, col].block_type == BLOCK_TYPES[2]:
                pyreman.row = row
                pyreman.col = col
                pyreman.draw()
                break

    def print_blocks_info(self):
        for rowi in range(int(WINDOW_SIZE[0] / BLOCK_SIZE)):
            for coli in range(int(WINDOW_SIZE[1] / BLOCK_SIZE)):
                print(self.city_matrix[rowi, coli])


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
        while running:
            for event in pg.event.get():

                if event.type == KEYDOWN:

                    self.city.draw()

                    if event.key == K_LEFT:
                        self.pyreman.move_left()
                        print('Last move: left')
                    if event.key == K_RIGHT:
                        self.pyreman.move_right()
                        print('Last move: right')
                    if event.key == K_UP:
                        self.pyreman.move_up()
                        print('Last move: up')
                    if event.key == K_DOWN:
                        self.pyreman.move_down()
                        print('Last move: down')

                    if event.key == K_ESCAPE:
                        running = False

                elif event.type == QUIT:
                    running = False

            time.sleep(0.1)


if __name__ == '__main__':
    game = Game()
    game.run()
