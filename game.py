from board import Board
from tetriminos import *
import random
import pygame

class Game:
    def __init__(self):
        self.grid = Board()
        self.tetriminos = [ITetrimino(), JTetrimino(), LTetrimino(), OTetrimino(), STetrimino(), TTetrimino(), ZTetrimino()]
        self.current_tetrimino = self.get_random_tetrimino()
        self.next_tetrimino = self.get_random_tetrimino()
        self.game_over = False
        self.score = 0
        self.rotate_sound = pygame.mixer.Sound("Sounds/rotate.ogg")
        self.clear_sound = pygame.mixer.Sound("Sounds/clear.ogg")

        pygame.mixer.music.load("Sounds/music.ogg")
        pygame.mixer.music.play(-1)

    def update_score(self, lines_cleared, move_down_points):
        if lines_cleared == 1:
            self.score += 100
        elif lines_cleared == 2:
            self.score += 300
        elif lines_cleared == 3:
            self.score += 500
        self.score += move_down_points

    def get_random_tetrimino(self):
        if len(self.tetriminos) == 0:
            self.tetriminos = [ITetrimino(), JTetrimino(), LTetrimino(), OTetrimino(), STetrimino(), TTetrimino(), ZTetrimino()]
        tetrimino = random.choice(self.tetriminos)
        self.tetriminos.remove(tetrimino)
        return tetrimino

    def move_left(self):
        self.current_tetrimino.move(0, -1)
        if self.tetrimino_inside() == False or self.tetrimino_fits() == False:
            self.current_tetrimino.move(0, 1)

    def move_right(self):
        self.current_tetrimino.move(0, 1)
        if self.tetrimino_inside() == False or self.tetrimino_fits() == False:
            self.current_tetrimino.move(0, -1)

    def move_down(self):
        self.current_tetrimino.move(1, 0)
        if self.tetrimino_inside() == False or self.tetrimino_fits() == False:
            self.current_tetrimino.move(-1, 0)
            self.lock_tetrimino()

    def lock_tetrimino(self):
        tiles = self.current_tetrimino.get_cell_positions()
        for position in tiles:
            self.grid.grid[position.row][position.column] = self.current_tetrimino.id
        self.current_tetrimino = self.next_tetrimino
        self.next_tetrimino = self.get_random_tetrimino()
        rows_cleared = self.grid.clear_full_rows()
        if rows_cleared > 0:
            self.clear_sound.play()
            self.update_score(rows_cleared, 0)
        if self.tetrimino_fits() == False:
            self.game_over = True

    def reset(self):
        self.grid.reset()
        self.tetriminos = [ITetrimino(), JTetrimino(), LTetrimino(), OTetrimino(), STetrimino(), TTetrimino(), ZTetrimino()]
        self.current_tetrimino = self.get_random_tetrimino()
        self.next_tetrimino = self.get_random_tetrimino()
        self.score = 0

    def tetrimino_fits(self):
        tiles = self.current_tetrimino.get_cell_positions()
        for tile in tiles:
            if self.grid.is_empty(tile.row, tile.column) == False:
                return False
        return True

    def rotate(self):
        self.current_tetrimino.rotate()
        if self.tetrimino_inside() == False or self.tetrimino_fits() == False:
            self.current_tetrimino.undo_rotation()
        else:
            self.rotate_sound.play()

    def tetrimino_inside(self):
        tiles = self.current_tetrimino.get_cell_positions()
        for tile in tiles:
            if not self.grid.is_inside(tile.row, tile.column):
                return False
        return True

    def draw(self, screen):
        self.grid.draw(screen)
        self.current_tetrimino.draw(screen, 11, 11)

        if self.next_tetrimino.id == 3:
            self.next_tetrimino.draw(screen, 255, 290)
        elif self.next_tetrimino.id == 4:
            self.next_tetrimino.draw(screen, 255, 280)
        else:
            self.next_tetrimino.draw(screen, 270, 270)

    def get_valid_moves(self, board, tetromino):
        valid_moves = []
        for row in range(board.num_rows):
            for col in range(board.num_cols):
                if board.is_valid_move(tetromino, row, col):
                    valid_moves.append((row, col))
        return valid_moves