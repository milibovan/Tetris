from grid import Grid
from tetraminos import *
import random
import pygame

class Game:
	def __init__(self):
		self.grid = Grid()
		self.Tetraminos = [ITetramino(), JTetramino(), LTetramino(), OTetramino(), STetramino(), TTetramino(), ZTetramino()]
		self.current_Tetramino = self.get_random_Tetramino()
		self.next_Tetramino = self.get_random_Tetramino()
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

	def get_random_Tetramino(self):
		if len(self.Tetraminos) == 0:
			self.Tetraminos = [ITetramino(), JTetramino(), LTetramino(), OTetramino(), STetramino(), TTetramino(), ZTetramino()]
		Tetramino = random.choice(self.Tetraminos)
		self.Tetraminos.remove(Tetramino)
		return Tetramino

	def move_left(self):
		self.current_Tetramino.move(0, -1)
		if self.Tetramino_inside() == False or self.Tetramino_fits() == False:
			self.current_Tetramino.move(0, 1)

	def move_right(self):
		self.current_Tetramino.move(0, 1)
		if self.Tetramino_inside() == False or self.Tetramino_fits() == False:
			self.current_Tetramino.move(0, -1)

	def move_down(self):
		self.current_Tetramino.move(1, 0)
		if self.Tetramino_inside() == False or self.Tetramino_fits() == False:
			self.current_Tetramino.move(-1, 0)
			self.lock_Tetramino()

	def lock_Tetramino(self):
		tiles = self.current_Tetramino.get_cell_positions()
		for position in tiles:
			self.grid.grid[position.row][position.column] = self.current_Tetramino.id
		self.current_Tetramino = self.next_Tetramino
		self.next_Tetramino = self.get_random_Tetramino()
		rows_cleared = self.grid.clear_full_rows()
		if rows_cleared > 0:
			self.clear_sound.play()
			self.update_score(rows_cleared, 0)
		if self.Tetramino_fits() == False:
			self.game_over = True

	def reset(self):
		self.grid.reset()
		self.Tetraminos = [ITetramino(), JTetramino(), LTetramino(), OTetramino(), STetramino(), TTetramino(), ZTetramino()]
		self.current_Tetramino = self.get_random_Tetramino()
		self.next_Tetramino = self.get_random_Tetramino()
		self.score = 0

	def Tetramino_fits(self):
		tiles = self.current_Tetramino.get_cell_positions()
		for tile in tiles:
			if self.grid.is_empty(tile.row, tile.column) == False:
				return False
		return True

	def rotate(self):
		self.current_Tetramino.rotate()
		if self.Tetramino_inside() == False or self.Tetramino_fits() == False:
			self.current_Tetramino.undo_rotation()
		else:
			self.rotate_sound.play()

	def Tetramino_inside(self):
		tiles = self.current_Tetramino.get_cell_positions()
		for tile in tiles:
			if self.grid.is_inside(tile.row, tile.column) == False:
				return False
		return True

	def draw(self, screen):
		self.grid.draw(screen)
		self.current_Tetramino.draw(screen, 11, 11)

		if self.next_Tetramino.id == 3:
			self.next_Tetramino.draw(screen, 255, 290)
		elif self.next_Tetramino.id == 4:
			self.next_Tetramino.draw(screen, 255, 280)
		else:
			self.next_Tetramino.draw(screen, 270, 270)