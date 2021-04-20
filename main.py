# Author: Sergio Machi
# Creation date: 11/Apr/2021
# Last edit: 20/Apr/2021

import time
import random
import numpy as np
import pygame as pg
from pygame.locals import *

# Pyreman
WINDOW_CAPTION = 'Pyreman'
# 1800
WINDOW_WIDTH = 1800
# 900
WINDOW_HEIGHT = 900
# 100
BLOCK_SIZE = 100
# 2000
FIRE_EXPANSION_SPEED = 2000
# 0.1
SLEEP_TIME = 0.1
# 0
INITIAL_POINTS = 0
# 1000
ADD_SUB_POINTS = 1000
# 15
TURNS = 150

BOMB_AUDIO_PATH = 'resources/audio/bomb.wav'
BACKGROUND_AUDIO_PATH = 'resources/audio/background.wav'

BLOCK_TYPES = ('FIRE', 'GRASS', 'HOUSE', 'WATER')
PYREMAN_IMG_PATH = 'resources/images/pyreman.png'


class Pyreman:
    def __init__(self, parent_screen, row=0, col=0):
        self.parent_screen = parent_screen
        self.row = row
        self.col = col
        self.bombs = TURNS - 3
        self.points = INITIAL_POINTS
        self.location_type = BLOCK_TYPES[2]

    def draw(self):
        block = pg.image.load(PYREMAN_IMG_PATH).convert_alpha()
        self.parent_screen.blit(block, (self.row * BLOCK_SIZE, self.col * BLOCK_SIZE))
        pg.display.flip()
        print(self.__str__())

    def bomb(self):
        if self.bombs != 0:
            self.bomb_sound()
            self.bombs -= 1

            if self.location_type == BLOCK_TYPES[0]:
                self.add_points()
            elif self.location_type == BLOCK_TYPES[2]:
                self.sub_points()

            return True
        return False

    def bomb_sound(self):
        pg.mixer.music.load(BOMB_AUDIO_PATH)
        pg.mixer.Channel(0).play(pg.mixer.Sound(BOMB_AUDIO_PATH))

    def add_points(self):
        self.points += ADD_SUB_POINTS

    def sub_points(self):
        if self.points > 0:
            self.points -= ADD_SUB_POINTS

    def sub_turns(self):
        global TURNS
        if TURNS > 0:
            TURNS -= 1

    def set_location_type(self, city_matrix):
        self.location_type = city_matrix[self.row, self.col].block_type

    def move_up(self, city_matrix):
        if TURNS == 0:
            return
        else:
            self.sub_turns()

        if self.col != 0:
            self.col -= 1
        else:
            self.col = int(WINDOW_HEIGHT / BLOCK_SIZE) - 1

        self.set_location_type(city_matrix)
        self.draw()

    def move_down(self, city_matrix):
        if TURNS == 0:
            return
        else:
            self.sub_turns()

        if self.col != int(WINDOW_HEIGHT / BLOCK_SIZE) - 1:
            self.col += 1
        else:
            self.col = 0

        self.set_location_type(city_matrix)
        self.draw()

    def move_left(self, city_matrix):
        if TURNS == 0:
            return
        else:
            self.sub_turns()

        if self.row != 0:
            self.row -= 1
        else:
            self.row = int(WINDOW_WIDTH / BLOCK_SIZE) - 1

        self.set_location_type(city_matrix)
        self.draw()

    def move_right(self, city_matrix):
        if TURNS == 0:
            return
        else:
            self.sub_turns()

        if self.row != int(WINDOW_WIDTH / BLOCK_SIZE) - 1:
            self.row += 1
        else:
            self.row = 0

        self.set_location_type(city_matrix)
        self.draw()

    def __str__(self):
        return f'X: {self.row}, ' \
               f'Y: {self.col}, ' \
               f'Location: {self.location_type.title()}, ' \
               f'Points = {self.points}, ' \
               f'Bombs left: {self.bombs}, ' \
               f'Turns: {TURNS}'


class Block:
    def __init__(self, block_type):
        self.block_type = block_type
        self.image_path = 'resources/images/' + block_type.lower() + '.png'
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
            int(WINDOW_WIDTH / BLOCK_SIZE),
            int(WINDOW_HEIGHT / BLOCK_SIZE)
        ], dtype=object)

    def draw(self):
        for rowi in range(int(WINDOW_WIDTH / BLOCK_SIZE)):
            for coli in range(int(WINDOW_HEIGHT / BLOCK_SIZE)):
                block = pg.image.load(self.city_matrix[rowi, coli].image_path).convert()
                self.parent_screen.blit(block, (rowi * BLOCK_SIZE, coli * BLOCK_SIZE))
        pg.display.flip()

    def build(self):
        for rowi in range(int(WINDOW_WIDTH / BLOCK_SIZE)):
            for coli in range(int(WINDOW_HEIGHT / BLOCK_SIZE)):
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
        row = random.randint(0, int(WINDOW_WIDTH / BLOCK_SIZE) - 1)
        col = random.randint(0, int(WINDOW_HEIGHT / BLOCK_SIZE) - 1)
        self.city_matrix[row, col] = Block(BLOCK_TYPES[0])

        block = pg.image.load(self.city_matrix[row, col].image_path).convert()
        self.parent_screen.blit(block, (row * BLOCK_SIZE, col * BLOCK_SIZE))
        pg.display.flip()

    def expand_fire(self):
        self.set_danger()

        for rowi in range(int(WINDOW_WIDTH / BLOCK_SIZE)):
            for coli in range(int(WINDOW_HEIGHT / BLOCK_SIZE)):
                if self.city_matrix[rowi, coli].is_in_danger:
                    self.city_matrix[rowi, coli] = Block(BLOCK_TYPES[0])
        self.draw()

    def set_danger(self):
        # Recursion would be nice here.
        for rowi in range(int(WINDOW_WIDTH / BLOCK_SIZE)):
            for coli in range(int(WINDOW_HEIGHT / BLOCK_SIZE)):

                if self.city_matrix[rowi, coli].block_type == BLOCK_TYPES[0]:

                    if rowi - 1 >= 0 and \
                            self.city_matrix[rowi - 1, coli].block_type != BLOCK_TYPES[0] and \
                            self.city_matrix[rowi - 1, coli].block_type != BLOCK_TYPES[3]:
                        self.city_matrix[rowi - 1, coli].is_in_danger = True

                    if rowi + 1 <= WINDOW_WIDTH / BLOCK_SIZE - 1 and \
                            self.city_matrix[rowi + 1, coli].block_type != BLOCK_TYPES[0] and \
                            self.city_matrix[rowi + 1, coli].block_type != BLOCK_TYPES[3]:
                        self.city_matrix[rowi + 1, coli].is_in_danger = True

                    if coli + 1 <= WINDOW_HEIGHT / BLOCK_SIZE - 1 and \
                            self.city_matrix[rowi, coli + 1].block_type != BLOCK_TYPES[0] and \
                            self.city_matrix[rowi, coli + 1].block_type != BLOCK_TYPES[3]:
                        self.city_matrix[rowi, coli + 1].is_in_danger = True

                    if coli - 1 >= 0 and \
                            self.city_matrix[rowi, coli - 1].block_type != BLOCK_TYPES[0] and \
                            self.city_matrix[rowi, coli - 1].block_type != BLOCK_TYPES[3]:
                        self.city_matrix[rowi, coli - 1].is_in_danger = True

    def place_pyreman(self, pyreman):
        while True:
            row = random.randint(0, int(WINDOW_WIDTH / BLOCK_SIZE) - 1)
            col = random.randint(0, int(WINDOW_HEIGHT / BLOCK_SIZE) - 1)

            if self.city_matrix[row, col].block_type == BLOCK_TYPES[2]:
                pyreman.row = row
                pyreman.col = col
                pyreman.draw()
                break


class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption(WINDOW_CAPTION)

        self.init_background_audio()
        self.surface = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.city = City(self.surface)
        self.pyreman = Pyreman(self.surface)
        self.init_game()

    def init_game(self):
        self.city.build()
        self.city.set_first_fire()
        self.city.place_pyreman(self.pyreman)

    def init_background_audio(self):
        pg.mixer.music.load(BACKGROUND_AUDIO_PATH)
        pg.mixer.Channel(1).play(pg.mixer.Sound(BACKGROUND_AUDIO_PATH), loops=-1)

    def handle_arrow_keys(self, event):
        if event.key == K_LEFT:
            self.pyreman.move_left(self.city.city_matrix)
        elif event.key == K_RIGHT:
            self.pyreman.move_right(self.city.city_matrix)
        elif event.key == K_UP:
            self.pyreman.move_up(self.city.city_matrix)
        elif event.key == K_DOWN:
            self.pyreman.move_down(self.city.city_matrix)

    def run(self):
        running = True

        time_since_last_fire_expansion = 0
        clock = pg.time.Clock()

        while running:

            for event in pg.event.get():
                if event.type == KEYDOWN:
                    self.city.draw()
                    self.handle_arrow_keys(event)

                    if event.key == K_RETURN:
                        self.city.destroy_block(self.pyreman)

                    if event.key == K_ESCAPE:
                        running = False

                elif event.type == QUIT:
                    running = False

            dt = clock.tick()
            time_since_last_fire_expansion += dt

            if time_since_last_fire_expansion > FIRE_EXPANSION_SPEED:
                self.city.expand_fire()
                # Should this line be here or in a class?
                self.pyreman.draw()
                time_since_last_fire_expansion = 0

            time.sleep(SLEEP_TIME)


if __name__ == '__main__':
    game = Game()
    game.run()
