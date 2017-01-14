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
		self.wall_center = self.size.w / 2
		self.wall_dist = self.size.w - 64
		self.beg_scene()
			
		self.timer = 0
		self.speed = 1.0
		time_font = ('Avenir Next Condensed', 32)
		self.time_label = LabelNode('00:00', font=time_font, parent=self)
		self.time_label.anchor_point = (0.5, 1)
		self.time_label.position = (self.size.w/2, self.size.h-16)
		
		self.highscore = self.load_highscore()
		self.show_start_menu()
		
	def beg_scene(self):
		y = 32
		while y < self.size.h:
			self.spawn_walls(y=y, name=iWall)
			self.spawn_walls(x=64, y=y, name=xWall)
			y += 64
	
	def new_game(self):
		self.wall_dist = (4*self.size.w) / 10
		self.lives_left = 3
		self.score = 0
		self.game_over = False
		self.players = []
		self.spawn_player()
		self.time_label.text = '00:00'
		self.start_time = self.t
		
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
		if self.timer % 16 == 0:
			#Time to make a new row
			if random.random() < 0.15:
				#Turn is happening
				if random.random() < 0.5 and self.can_turn(32):
					self.wall_center += 32
				elif random.random() > 0.5 and self.can_turn(-32):
					self.wall_center -= 32
					
				x = self.wall_center - 32
	#			while x > 
				self.speed = min(3, self.speed+0.05)
				
				
			self.spawn_walls()
		self.move_walls()
		self.timer += 1		

	def can_turn(self, dir):
		if(self.wall_center+dir > 0 and self.wall_center+dir < self.size.w):
			return True
		return False

	def spawn_walls(self, x=0, y=None, name=xWall):
		#Not allowed to use 'self' in args
		if y == None:
			y = self.size.h+8
		
		ltile = SpriteNode(name, position=(x, y), parent=self)
		rtile = SpriteNode(name, position=(self.size.w-x, y), parent=self)
		
		ltile.rotation=-math.pi/2
		rtile.rotation=math.pi/2
		
		self.walls.append(ltile)
		self.walls.append(rtile)
		
	def move_walls(self):
		dy = -1*self.speed
		for tile in self.walls:
			tile.position += 0, dy
			if tile.position.y < -32:
				tile.remove_from_parent()
				self.walls.remove(tile)
			
	def check_wall_collision(self):
		for ship in self.players:
			if ship.position.x-ship.size[0]/2 < 96:
				self.player_crash(ship)
			elif ship.position.x+ship.size[0]/2 > self.size.w-96:
				self.player_crash(ship)
	
	def player_crash(self, p):
		sound.play_effect('digital:ZapThreeToneDown')
		p.remove_from_parent()
		self.players.remove(p)
		self.lives_left -= 1
		if self.lives_left == 0:
			self.end_game()
		else:
			#After a delay, respawn
			self.run_action(A.sequence(A.wait(2), A.call(self.spawn_player)))
		
	def spawn_player(self):
		new_player = SpriteNode('spc:PlayerLife1Blue', parent=self)
		new_player.anchor_point = (0.5, 0)
		new_player.position = (self.size.w/2, 16)
		self.player_target = self.size.w/2
		self.players.append(new_player)
		
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
