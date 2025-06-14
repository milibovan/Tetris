from settings import *
import math
from tetromino import Tetromino
import pygame.freetype as ft
import copy
import ai


class Text:
    def __init__(self, app):
        self.app = app
        self.font = ft.Font(FONT_PATH)

    def get_color(self):
        time = pg.time.get_ticks() * 0.001
        n_sin = lambda t: (math.sin(t) * 0.5 + 0.5) * 255
        return n_sin(time * 0.5), n_sin(time * 0.2), n_sin(time * 0.9)

    def draw(self):
        self.font.render_to(self.app.screen, (WIN_W * 0.595, WIN_H * 0.02),
                            text='TETRIS', fgcolor=self.get_color(),
                            size=TILE_SIZE * 1.65, bgcolor='black')
        self.font.render_to(self.app.screen, (WIN_W * 0.65, WIN_H * 0.22),
                            text='next', fgcolor='orange',
                            size=TILE_SIZE * 1.4, bgcolor='black')
        self.font.render_to(self.app.screen, (WIN_W * 0.64, WIN_H * 0.67),
                            text='score', fgcolor='orange',
                            size=TILE_SIZE * 1.4, bgcolor='black')
        self.font.render_to(self.app.screen, (WIN_W * 0.64, WIN_H * 0.8),
                            text=f'{self.app.tetris.score}', fgcolor='white',
                            size=TILE_SIZE * 1.8)


class Tetris:
    def __init__(self, app):
        self.app = app
        self.sprite_group = pg.sprite.Group()
        self.field_array = self.get_field_array()
        self.tetromino = Tetromino(self)
        self.next_tetromino = Tetromino(self, current=False)
        self.speed_up = False

        self.score = 0
        self.full_lines = 0
        self.points_per_lines = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}

    def copy(self):
        copied_tetris = Tetris(self.app)
        copied_tetris.sprite_group = self.sprite_group.copy()
        copied_tetris.field_array = [row[:] for row in self.field_array]
        copied_tetris.tetromino = self.tetromino.copy(copied_tetris)
        copied_tetris.next_tetromino = self.next_tetromino.copy(copied_tetris)
        copied_tetris.speed_up = self.speed_up
        copied_tetris.score = self.score
        copied_tetris.full_lines = self.full_lines
        copied_tetris.points_per_lines = self.points_per_lines.copy()
        return copied_tetris

    def get_score(self):
        self.score += self.points_per_lines[self.full_lines]
        self.full_lines = 0

    def check_full_lines(self):
        row = FIELD_H - 1
        for y in range(FIELD_H - 1, -1, -1):
            for x in range(FIELD_W):
                self.field_array[row][x] = self.field_array[y][x]

                if self.field_array[y][x]:
                    self.field_array[row][x].pos = vec(x, y)

            if sum(map(bool, self.field_array[y])) < FIELD_W:
                row -= 1
            else:
                for x in range(FIELD_W):
                    self.field_array[row][x].alive = False
                    self.field_array[row][x] = 0

                self.full_lines += 1

    def put_tetromino_blocks_in_array(self):
        for block in self.tetromino.blocks:
            x, y = int(block.pos.x), int(block.pos.y)

            if 0 <= x < FIELD_W and 0 <= y < FIELD_H:
                self.field_array[y][x] = block
            elif 0 <= x < FIELD_W and y >= FIELD_H:
                self.field_array[FIELD_H - 1][x] = block
            else:
                raise ValueError(f"Tetromino block out of field boundaries at position({x},{y})")

    def get_field_array(self):
        return [[0 for x in range(FIELD_W)] for y in range(FIELD_H)]

    def is_game_over(self):
        if self.tetromino.blocks[0].pos.y == INIT_POS_OFFSET[1]:
            pg.time.wait(300)
            return False

    def check_tetromino_landing(self):
        if self.tetromino.landing:
            if self.is_game_over():
                self.__init__(self.app)
            else:
                self.speed_up = False
                self.put_tetromino_blocks_in_array()
                self.next_tetromino.current = True
                self.tetromino = self.next_tetromino
                self.next_tetromino = Tetromino(self, current=False)

    def control(self, pressed_key):
        if pressed_key == pg.K_LEFT:
            self.tetromino.move(direction='left')
        elif pressed_key == pg.K_RIGHT:
            self.tetromino.move(direction='right')
        elif pressed_key == pg.K_UP:
            self.tetromino.rotate()
        elif pressed_key == pg.K_DOWN:
            self.speed_up = True

    def draw_grid(self):
        for x in range(FIELD_W):
            for y in range(FIELD_H):
                pg.draw.rect(self.app.screen, 'black',
                             (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

    def update(self):
        trigger = [self.app.anim_trigger, self.app.fast_anim_trigger][self.speed_up]
        if trigger:
            self.check_full_lines()
            self.tetromino.update()
            self.check_tetromino_landing()
            self.get_score()
        self.sprite_group.update()

    def draw(self):
        self.draw_grid()
        self.sprite_group.draw(self.app.screen)

    def count_holes(self):
        holes = 0
        for x in range(FIELD_W):
            block_found = False
            for y in range(FIELD_H):
                if self.field_array[y][x] != 0:
                    block_found = True
                elif self.field_array[y][x] == 0 and block_found:
                    holes += 1
        return holes

    def get_landing_height(self):
        return INIT_POS_OFFSET[1] - self.tetromino.blocks[0].pos.y

    def count_eroded_cells(self):
        eroded_cells = 0
        for x in range(FIELD_W):
            for y in range(FIELD_H):
                if self.field_array[y][x] == 0:
                    if y < FIELD_H - 1 and self.field_array[y + 1][x] != 0:
                        eroded_cells += 1
        return eroded_cells

    def calculate_cumulative_wells(self):
        cumulative_wells = 0
        for x in range(FIELD_W):
            well_depth = 0
            for y in range(FIELD_H - 1, -1, -1):
                if self.field_array[y][x] == 0:
                    well_depth += 1
                else:
                    cumulative_wells += well_depth * (well_depth + 1) // 2
                    well_depth = 0
            cumulative_wells += well_depth * (well_depth + 1) // 2
        return cumulative_wells

    def count_row_transitions(self):
        row_transitions = 0
        for y in range(FIELD_H):
            prev_block = 1
            for x in range(FIELD_W):
                if (self.field_array[y][x] != 0) != (prev_block != 0):
                    row_transitions += 1
                prev_block = self.field_array[y][x]
            if prev_block == 0:
                row_transitions += 1
        return row_transitions

    def count_column_transitions(self):
        column_transitions = 0
        for x in range(FIELD_W):
            prev_block = 1
            for y in range(FIELD_H - 1, -1, -1):
                if (self.field_array[y][x] != 0) != (prev_block != 0):
                    column_transitions += 1
                prev_block = self.field_array[y][x]
            if prev_block == 0:
                column_transitions += 1
        return column_transitions

    def get_legal_moves(self):
        legal_moves = []

        for _ in range(4):
            for column in range(FIELD_W):
                self.tetromino.pos = vec(column, 0)

                while True:
                    next_positions = [block.pos + MOVE_DIRECTIONS['down'] for block in self.tetromino.blocks]

                    if self.tetromino.is_collide(next_positions) or any(pos.y >= FIELD_H for pos in next_positions):
                        break

                    self.tetromino.move(direction='down')
            landing_position = [vec(block.pos.x, block.pos.y) for block in self.tetromino.blocks]

            if all(0 <= pos.x < FIELD_W and 0 <= pos.y < FIELD_H for pos in landing_position):
                legal_moves.append(landing_position)

            next_rotation_positions = self.tetromino.get_rotation_positions()
            if not self.tetromino.is_collide(next_rotation_positions) and all(
                    0 <= pos.x < FIELD_W and 0 <= pos.y < FIELD_H for pos in next_rotation_positions):
                self.tetromino.rotate()

        return legal_moves

    def ai_move(self):
        _, best_move = ai.evaluate(self, 2)
        if best_move is not None:
            for position in best_move:
                self.tetromino.move_to_position(position)
                self.update()
