import pygame
from colors import Colors


class Board:
    def __init__(self):
        self.num_rows = 20
        self.num_cols = 10
        self.cell_size = 30
        self.grid = [[0 for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        self.colors = Colors.get_cell_colors()

    def copy(self):
        new_board = Board()
        new_board.num_rows = self.num_rows
        new_board.num_cols = self.num_cols
        new_board.cell_size = self.cell_size
        new_board.grid = [row[:] for row in self.grid]
        new_board.colors = self.colors.copy()
        return new_board

    def print_grid(self):
        for row in range(self.num_rows):
            for column in range(self.num_cols):
                print(self.grid[row][column], end=" ")
            print()

    def is_inside(self, row, column):
        if 0 <= row < self.num_rows and 0 <= column < self.num_cols:
            return True
        return False

    def is_empty(self, row, column):
        if self.grid[row][column] == 0:
            return True
        return False

    def is_row_full(self, row):
        for column in range(self.num_cols):
            if self.grid[row][column] == 0:
                return False
        return True

    def clear_row(self, row):
        for column in range(self.num_cols):
            self.grid[row][column] = 0

    def move_row_down(self, row, num_rows):
        for column in range(self.num_cols):
            self.grid[row + num_rows][column] = self.grid[row][column]
            self.grid[row][column] = 0

    def clear_full_rows(self):
        completed = 0
        for row in range(self.num_rows - 1, 0, -1):
            if self.is_row_full(row):
                self.clear_row(row)
                completed += 1
            elif completed > 0:
                self.move_row_down(row, completed)
        return completed

    def reset(self):
        for row in range(self.num_rows):
            for column in range(self.num_cols):
                self.grid[row][column] = 0

    def draw(self, screen):
        for row in range(self.num_rows):
            for column in range(self.num_cols):
                cell_value = self.grid[row][column]
                cell_rect = pygame.Rect(column * self.cell_size + 11, row * self.cell_size + 11,
                                        self.cell_size - 1, self.cell_size - 1)
                pygame.draw.rect(screen, self.colors[cell_value], cell_rect)

    def count_holes(self):
        num_holes = 0
        for col in range(self.num_cols):
            hole_found = False
            for row in range(self.num_rows):
                if self.grid[row][col] != 0:
                    hole_found = True
                elif self.grid[row][col] == 0 and hole_found:
                    num_holes += 1
        return num_holes

    def get_landing_height(self, current_block):
        block_cells = current_block.get_cells()
        max_height = 0
        for cell in block_cells:
            row = cell.row
            if row > max_height:
                max_height = row
        return max_height

    def count_eroded_cells(self, rows_cleared, num_cols):
        return rows_cleared * num_cols

    def calculate_cumulative_wells(self):
        cumulative_wells = 0
        for col in range(self.num_cols):
            well_depth = 0
            for row in range(self.num_rows - 1, -1, -1):
                if self.grid[row][col] == 0:
                    well_depth += 1
                else:
                    cumulative_wells += well_depth * (well_depth + 1) // 2
                    well_depth = 0
            cumulative_wells += well_depth * (well_depth + 1) // 2
        return cumulative_wells

    def count_row_transitions(self):
        num_row_transitions = 0
        for row in range(self.num_rows):
            for col in range(self.num_cols - 1):
                cell1 = self.grid[row][col]
                cell2 = self.grid[row][col + 1]
                if (cell1 == 0 and cell2 != 0) or (cell1 != 0 and cell2 == 0):
                    num_row_transitions += 1
        return num_row_transitions

    def count_column_transitions(self):
        num_column_transitions = 0
        for col in range(self.num_cols):
            for row in range(self.num_rows - 1):
                cell1 = self.grid[row][col]
                cell2 = self.grid[row + 1][col]
                if (cell1 == 0 and cell2 != 0) or (cell1 != 0 and cell2 == 0):
                    num_column_transitions += 1
        return num_column_transitions

    def apply_move(self, tetrimino, move):
        rotation, column = move
        tetrimino_matrix = tetrimino.get_rotation(rotation)
        tetrimino_width = len(tetrimino_matrix[0])
        tetrimino_height = len(tetrimino_matrix)

        for row in range(tetrimino_height):
            for col in range(tetrimino_width):
                if tetrimino_matrix[row][col] != 0:
                    board_row = self.row_offset + row
                    board_col = self.column_offset + column + col
                    if self.is_inside(board_row, board_col):
                        self.grid[board_row][board_col] = tetrimino.id

