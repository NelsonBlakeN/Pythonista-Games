from scene import *
from game_menu import MenuScene
import sound
import random
import math
import time
A = Action

class Game (Scene):
	def setup(self):
		self.background_color = '#004f82'
		self.l_wall = Node(parent=self)
		self.r_wall = Node(parent=self)
		self.walls = []
		#Center between the walls
		#Walls are spawned an equal distance in both directions
		#Will be shifted in the game
		self.wall_center = self.size.w / 2
		self.wall_dist = (4*self.size.w) / 10
		y = 32
		while y <= self.size.h:
			self.spawn_walls(y)
			y += 64
			
		self.timer = 0
		self.speed = 2.0
		self.lives_left = 3
		time_font = ('Avenir Next Condensed', 32)
		self.time_label = LabelNode('00:00', font=time_font, parent=self)
		self.time_label.anchor_point = (0.5, 1)
		self.time_label.position = (self.size.w/2, self.size.h-16)
		self.start_time = self.t
		
		self.highscore = self.load_highscore()
		self.show_start_menu()
	
	def new_game(self):
		self.lives_left = 3
		self.score = 0
		self.game_over = False
		self.players = []
		self.spawn_player()
		
	def load_highscore(self):
		try:
			with open('.Match3Highscore', 'r') as f:
				return int(f.read())
		except:
			return 0
	
	def update(self):
		self.move_ship()
		self.update_walls()
		self.check_wall_collision()
		sec_in = int(self.t - self.start_time)
		self.time_label.text = '%02d:%02d' % (sec_in/60, sec_in%60)
		
	def update_walls(self):
		if self.timer % 16 == 0:
			self.spawn_walls()
		self.move_walls()
		self.timer += 1		

	def spawn_walls(self, y=None):
		if y is None:
			y = self.size.h+8
		
		l_tile = SpriteNode('plf:Ground_DirtCenter', position=(self.wall_center - self.wall_dist, y))
		r_tile = SpriteNode('plf:Ground_DirtCenter', position=(self.wall_center + self.wall_dist, y))
		self.l_wall.add_child(l_tile)
		self.r_wall.add_child(r_tile)
		self.walls.append(l_tile)
		self.walls.append(r_tile)
		
	def move_walls(self):
		dy = -1*self.speed
		for tile in self.walls:
			tile.position += 0, dy
			
	def check_wall_collision(self):
		for ship in self.players:
			if ship.position.x-ship.size[0]/2 < 64:
				self.player_crash(ship)
			elif ship.position.x+ship.size[0]/2 > self.size.w-64:
				self.player_crash(ship)
	
	def player_crash(self, p):
		p.remove_from_parent()
		self.players.remove(p)
		self.lives_left -= 1
		print(self.lives_left)
		if self.lives_left == 0:
			self.end_game()
		else:
			self.run_action(A.sequence(A.wait(2), A.call(self.spawn_player)))
		
	def spawn_player(self):
		new_player = SpriteNode('spc:PlayerLife1Blue', parent=self)
		new_player.anchor_point = (0.5, 0)
		new_player.position = (self.size.w/2, 16)
		print("Spawn player at "+str(new_player.position))
		self.player_target = self.size.w/2
		self.players.append(new_player)
		
	def end_game(self):
		if self.score > self.highscore:
			self.highscore = self.score
			self.save_highscore()
		self.paused = True
		self.menu = MenuScene('Game Over', 'Highscore: %i' % self.highscore, ['New Game'])
		self.present_modal_scene(self.menu)
		
	def show_start_menu(self):
		self.paused = True
		self.menu = MenuScene('Maze Run', 'Highscore: %i' % self.highscore, ['Play'])
		self.present_modal_scene(self.menu)
		
	def menu_button_selected(self, title):
		if title in ('New Game', 'Play'):
			self.dismiss_modal_scene()
			self.menu = None
			self.paused = False
			self.new_game()
	
	def move_ship(self):
		for ship in list(self.players):
			dx = self.player_target - ship.position.x
			ship.position += dx, 0
	
	def touch_began(self, touch):
		x, y = touch.location
		self.player_target = x
	
	def touch_moved(self, touch):
		x, y = touch.location
		self.player_target = x
	
	def touch_ended(self, touch):
		pass

if __name__ == '__main__':
	run(Game(), show_fps=True)
