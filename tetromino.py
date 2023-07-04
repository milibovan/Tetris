from settings import *
import random


class Block(pg.sprite.Sprite):
    def __init__(self, tetromino, pos):
        self.tetromino = tetromino
        self.pos = vec(pos) + INIT_POS_OFFSET
        self.next_pos = vec(pos) + NEXT_POS_OFFSET
        self.alive = True

        super().__init__(tetromino.tetris.sprite_group)
        self.image = tetromino.image
        self.rect = self.image.get_rect()

        self.sfx_image = self.image.copy()
        self.sfx_image.set_alpha(110)
        self.sfx_speed = random.uniform(0.2, 0.6)
        self.sfx_cycles = random.randrange(6, 8)
        self.cycle_counter = 0

    def copy(self, copied_tetromino):
        copied_block = Block(copied_tetromino, self.pos)
        copied_block.alive = self.alive
        copied_block.image = self.image.copy()
        copied_block.rect = self.rect.copy()
        copied_block.sfx_image = self.sfx_image.copy()
        copied_block.sfx_speed = self.sfx_speed
        copied_block.sfx_cycles = self.sfx_cycles
        copied_block.cycle_counter = self.cycle_counter

        return copied_block

    def sfx_end_time(self):
        if self.tetromino.tetris.app.anim_trigger:
            self.cycle_counter += 1
            if self.cycle_counter > self.sfx_cycles:
                self.cycle_counter = 0
                return True

    def sfx_run(self):
        self.image = self.sfx_image
        self.pos.y -= self.sfx_speed
        self.image = pg.transform.rotate(self.image, pg.time.get_ticks() * self.sfx_speed)

    def is_alive(self):
        if not self.alive:
            if not self.sfx_end_time():
                self.sfx_run()
            else:
                self.kill()

    def rotate(self, pivot_pos):
        translated = self.pos - pivot_pos
        rotated = translated.rotate(90)
        return rotated + pivot_pos

    def set_rect_pos(self):
        pos = [self.next_pos, self.pos][self.tetromino.current]
        self.rect.topleft = pos * TILE_SIZE

    def update(self):
        self.is_alive()
        self.set_rect_pos()

    def is_collide(self, pos):
        x, y = int(pos.x), int(pos.y)
        if 0 <= x < FIELD_W and y < FIELD_H and (
                y < 0 or not self.tetromino.tetris.field_array[y][x]):
            return False
        return True


class Tetromino:
    def __init__(self, tetris, current=True):
        self.tetris = tetris
        self.shape = random.choice(list(TETROMINOES.keys()))
        self.image = random.choice(tetris.app.images)
        self.blocks = [Block(self, pos) for pos in TETROMINOES[self.shape]]
        self.landing = False
        self.current = current

    def copy(self, tetris):
        copied_tetromino = Tetromino(tetris, current=self.current)
        copied_tetromino.shape = self.shape
        copied_tetromino.image = self.image
        copied_tetromino.blocks = [Block(copied_tetromino, block.pos.copy()) for block in self.blocks]
        copied_tetromino.landing = self.landing
        return copied_tetromino

    def get_column(self):
        return min(block.pos.x for block in self.blocks)

    def rotate(self):
        pivot_pos = self.blocks[0].pos
        new_block_positions = [block.rotate(pivot_pos) for block in self.blocks]

        if not self.is_collide(new_block_positions):
            for i, block in enumerate(self.blocks):
                block.pos = new_block_positions[i]

    def is_collide(self, block_positions):
        for block in self.blocks:
            x, y = int(block.pos.x), int(block.pos.y)
            if (0 <= x < FIELD_W and y < FIELD_H and
                    (y < 0 or not self.tetris.field_array[y][x]) and
                    block.pos not in block_positions):
                return False
        return True

    def move(self, direction):
        move_direction = MOVE_DIRECTIONS[direction]
        new_block_positions = [block.pos + move_direction for block in self.blocks]
        is_collide = self.is_collide(new_block_positions)

        if not is_collide:
            for block in self.blocks:
                block.pos += move_direction
        elif direction == 'down':
            self.landing = True

    def update(self):
        self.move(direction='down')

    def move_to_column(self, column):
        current_column = self.get_column()
        move_direction = column - current_column

        if move_direction < 0:
            for _ in range(abs(move_direction)):
                self.move(direction='left')
        elif move_direction > 0:
            for _ in range(move_direction):
                self.move(direction='right')

    def is_valid_position(self):
        for block in self.blocks:
            if block.is_collide(block.pos):
                return False
        return True

    def get_position(self):
        positions = [block.pos for block in self.blocks]
        x_values = [pos.x for pos in positions]
        y_values = [pos.y for pos in positions]
        min_x = min(x_values)
        min_y = min(y_values)
        return vec(min_x, min_y)

    def move_to_position(self, position):
        current_position = self.get_position()
        move_direction = vec(position[0] - current_position.x, position[1] - current_position.y)
        max_distance = max(abs(move_direction.x), abs(move_direction.y))
        for _ in range(int(max_distance)):
            if move_direction.x != 0:
                self.move(direction='right' if move_direction.x > 0 else 'left')
            if move_direction.y != 0:
                self.move(direction='down')

    def get_rotation_positions(self):
        original_positions = [block.pos for block in self.blocks]
        self.rotate()
        rotated_positions = [block.pos for block in self.blocks]

        for block, original_position in zip(self.blocks, original_positions):
            block.pos = original_position
        return rotated_positions
