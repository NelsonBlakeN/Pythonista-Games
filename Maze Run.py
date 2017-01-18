from scene import *
from game_menu import MenuScene
import sound
import random
import math
import time
A = Action

xWall = 'plf:Ground_PlanetMid'
iWall = 'plf:Ground_PlanetCenter'
lTurn = 'plf:Ground_PlanetHill_right'
rTurn = 'plf:Ground_PlanetHill_left'

class Game (Scene):
	def setup(self):
		self.background_color = '#004f82'
		self.walls = []
		#Center between the walls
		#Walls are spawned an equal distance in both directions
		#Will be shifted in the game

		time_font = ('Avenir Next Condensed', 32)
		self.time_label = LabelNode('00:00', font=time_font, parent=self)
		self.time_label.anchor_point = (0.5, 1)
		self.time_label.position = (self.size.w/2, self.size.h-16)
		self.time_label.z_position = 1
		
		self.highscore = self.load_highscore()
		self.show_start_menu()
		
	def beg_scene(self):
		y = 32
		while y < self.size.h+64:
			self.spawn_walls(y=y)
			y += 64
	
	def new_game(self):
		for w in self.walls:
			w.remove_from_parent()
		self.wall_dist = 96
		self.wall_center = self.size.w/2
		self.timer = 0
		self.speed = 1.0
		self.score = 0
		self.game_over = False
		self.spawn_player()
		self.time_label.text = '00:00'
		self.start_time = self.t
		self.beg_scene()
		
	def load_highscore(self):
		try:
			with open('.MazeRun_highscore', 'r') as f:
				return int(f.read())
		except:
			return 0
	
	def update(self):
		self.move_ship()
		self.update_walls()
		self.check_wall_collision()
		self.score = int(self.t - self.start_time)
		sec_in = self.score
		self.time_label.text = '%02d:%02d' % (sec_in/60, sec_in%60)
		
	def update_walls(self):
		if self.timer % 64 == 0:
			self.spawn_walls()
			#Time to make a new row
			if random.random() < 0.45:
				#Turn is happening
				if random.random() < 0.5 and self.can_turn(96):
					self.wall_center += 32
				elif random.random() > 0.5 and self.can_turn(-96):
					self.wall_center -= 32
					
				self.speed = min(15, self.speed+0.025)
				
		self.move_walls()
		self.timer += 1		

	def can_turn(self, dir):
		if(self.wall_center+dir > 0 and self.wall_center+dir < self.size.w):
			return True
		return False

	def spawn_walls(self, y=None):
		#Not allowed to use 'self' in args
		if y == None:
			y = self.size.h+72
			
		ledge = SpriteNode(xWall, position=(self.wall_center-self.wall_dist, y), parent=self)
		redge = SpriteNode(xWall, position=(self.wall_center+self.wall_dist, y), parent=self)
		ledge.rotation=-math.pi/2
		redge.rotation=math.pi/2
		self.walls.append(ledge)
		self.walls.append(redge)
		
		t = 1
		while t <= 3:
			lx = self.wall_center-self.wall_dist-(64*t)
			rx = self.wall_center+self.wall_dist+(64*t)
			ltile = SpriteNode(iWall, position=(lx, y), parent=self)
			rtile = SpriteNode(iWall, position=(rx, y), parent=self)
		
			ltile.rotation=-math.pi/2
			rtile.rotation=math.pi/2
		
			self.walls.append(ltile)
			self.walls.append(rtile)
			
			t+=1
		
	def move_walls(self):
		dy = -1*self.speed
		for tile in self.walls:
			tile.position += 0, dy
			if tile.position.y < -32:
				tile.remove_from_parent()
				self.walls.remove(tile)
			
	def check_wall_collision(self):
		size_x = self.player.size[0]
		size_y = self.player.size[1]
		player_hitbox = Rect(self.player.position.x - size_x/2, 128, size_x, size_y)
		
		for wall in list(self.walls):
			if wall.frame.intersects(player_hitbox):
				print("Crashed")
				self.player_crash(self.player)
	
	def player_crash(self, p):
		sound.play_effect('digital:ZapThreeToneDown')
		p.remove_from_parent()
		self.end_game()
		
	def spawn_player(self):
		self.player = SpriteNode('spc:PlayerLife1Blue', parent=self)
		self.player.anchor_point = (0.5, 0)
		self.player.position = (self.size.w/2, 128)
		self.player_target = self.size.w/2
		self.player.z_position = 1
		
	def end_game(self):
		if self.score > self.highscore:
			self.highscore = self.score
			self.save_highscore()
		self.paused = True
		self.menu = MenuScene('Game Over', 'Highscore: %02d:%02d' % (self.highscore/60, self.highscore%60), ['New Game'])
		self.present_modal_scene(self.menu)
		
	def save_highscore(self):
		with open('.MazeRun_highscore', 'w') as f:
			f.write(str(self.highscore))
	
	def show_start_menu(self):
		self.paused = True
		self.menu = MenuScene('Maze Run', 'Highscore: %02d:%02d' % (self.highscore/60, self.highscore%60), ['New Game'])
		self.present_modal_scene(self.menu)
		
	def menu_button_selected(self, title):
		if title in ('New Game', 'Play'):
			self.dismiss_modal_scene()
			self.menu = None
			self.paused = False
			self.new_game()
	
	def move_ship(self):
		dx = self.player_target - self.player.position.x
		self.player.position += dx, 0
	
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
