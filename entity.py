import pygame
import random
import os
from threading import Thread


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = SCREEN_WIDTH * .8

#define colors
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GOLD = (255, 223, 0)

class Entity():
	def __init__(self, char_type, x, y, scale):
		self.alive = True
		self.char_type = char_type
		self.direction = 1
		self.vel_y = 0
		self.jump = False
		self.flip = False
		self.attacking = False
		self.running = False
		self.hit = False
		self.animation_list = []
		self.frame_index = 0
		self.action = 0
		self.update_time = pygame.time.get_ticks()
		#ai specific variable
		self.vision = pygame.Rect(0, 0, 175, 20)

		self.move_counter = 0 
		self.idling = False
		self.idling_counter = 0
		self.lucky_skel = False
		self.respawn_timer = 0
		self.close_enough = False
		self.seen = False
		#1 in 25 chance for skeleton to be boss mob
		if random.randint(1, 25) == 10 and self.char_type == "Skeleton":
			self.lucky_skel = True

		#load all images 
		animation_types = ['idle', 'run', 'jump', 'attack', 'death', 'hit', 'react']
		for animation in animation_types:
			#reset temporary list of images
			temp_list = []
			#count number of files in the folder
			self.num_of_frames = len(os.listdir(f"img/{self.char_type}/{animation}"))-2
			for i in range(self.num_of_frames):
				orig_img = pygame.image.load(f"img/{self.char_type}/{animation}/{i}.png").convert_alpha()
				crop_rect = orig_img.get_bounding_rect()
				crop_img = orig_img.subsurface(crop_rect).copy()
				img = pygame.transform.scale(crop_img,(crop_img.get_width()*scale, crop_img.get_height()*scale))
				temp_list.append(img)
			self.animation_list.append(temp_list)

		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		if self.char_type == 'Player':
			self.health = 100
			self.attacking_rect = pygame.Rect(0, 0, 2.5*self.rect.width, self.rect.height)
		if self.char_type == 'Skeleton' and not self.lucky_skel:
			self.health = 40
			self.attacking_rect = pygame.Rect(0, 0, 1.2*self.rect.width, self.rect.height)
			self.pseudo_rect = pygame.Rect(0, 0, 1.2*self.rect.width, self.rect.height)
		elif self.char_type == "Skeleton" and self.lucky_skel:
			self.attacking_rect = pygame.Rect(0, 0, self.rect.width, self.rect.height)
			self.pseudo_rect = pygame.Rect(0, 0, self.rect.width, self.rect.height)
			self.health = 80
		self.collected = False
		self.score = 0

	def update(self):
		#update player actions
		if self.alive:
			#if self.seen:
				#self.update_action(6) #6 is react
			if self.hit:
				self.update_action(5) #5 is hit
			elif self.attacking:
				self.update_action(3) #3 means attack
			elif self.jump and self.char_type == 'Player':
				self.update_action(2) #2 means jump
			elif self.running:
				self.update_action(1)  #1 means run 
			else:
				self.update_action(0) #0 means idle

		self.check_alive()

		#update animation
		ANIMATION_COOLDOWN = 100
		#update img depending on current frame
		self.image = self.animation_list[self.action][self.frame_index]
		#check if enough time has passed since the last update
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		#if animation run out of frames reset to start
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 6:
				self.seen = False
				self.frame_index = 0
			elif self.action == 5:
				self.hit = False
				self.frame_index = 0
			elif self.action == 4: #4 means dead end animations if dead
				self.frame_index = len(self.animation_list[self.action]) - 1
				self.alive = False
			elif self.action == 3:
				self.attacking = False
				self.frame_index = 0
			else:
				self.frame_index = 0
		

	
	def move(self, SCREEN_HEIGHT, surface, target):
		SPEED = 7
		GRAVITY = .75
		dx = 0
		dy = 0
		self.running = False

		#store keypresses
		key = pygame.key.get_pressed()

		#can only perform other action if not dead and not attacking
		if self.alive and self.attacking == False:
			#movement
			if key[pygame.K_a]:
				dx = -SPEED
				self.flip = True #left
				self.direction = -1
				self.running = True

			if key[pygame.K_d]:
				dx = SPEED
				self.flip = False #right
				self.direction = 1
				self.running = True

			#jump
			if key[pygame.K_w] and self.jump == False:
				self.vel_y = -11
				self.jump = True

			#attack
			if key[pygame.K_f]:
				self.attack(surface, target)
				self.attacking = True

		#apply gravity
		self.vel_y += GRAVITY 
		dy += self.vel_y

		#ensure stays on screen
		if self.rect.bottom + dy > SCREEN_HEIGHT - 66:
			self.vel_y = 0
			self.jump = False
			dy = SCREEN_HEIGHT - 66 - self.rect.bottom	

		#update player position
		self.rect.x += dx
		self.rect.y += dy

	def ai(self, surface, target):
		SPEED = 1
		GRAVITY = .75
		dx = 0
		dy = 0
		self.running = False

		#can only perform other action if not dead and not attacking
		if self.alive and self.attacking == False:
			if self.idling == False and random.randint(1, 200) == 1: #1 in 200 chance to stop
				self.idling = True
				self.idling_counter = 200
			#pygame.draw.rect(surface, GREEN, self.pseudo_rect)
			if self.hit:
				if target.direction == 1:
					self.direction = -1
					self.flip = True
				elif target.direction == -1:
					self.direction = 1
					self.flip = False
			#check if the ai is near to the player and go close enough to attack
			self.pseudo_rect.center = (self.rect.centerx + 50 * self.direction, self.rect.centery)
			#update vision
			self.vision.center = (self.rect.centerx + 90 * self.direction, self.rect.centery)
			if self.vision.colliderect(target.rect): #if player is seen
				#stop running and face player
				self.seen = True
				self.running = False
				
				if not self.close_enough: #walk to the player 
					if self.direction == -1:
						dx = -SPEED
						self.flip = True #left 
						self.running = True
						if self.pseudo_rect.colliderect(target.rect): #if attackable close_enough
							self.close_enough = True 
					elif self.direction == 1: #walk to the player other direction 
						dx = SPEED
						self.flip = False #right
						self.running = True
						if self.pseudo_rect.colliderect(target.rect): #if attackable close_enough
							self.close_enough = True
					self.vision.center = (self.rect.centerx + 90 * self.direction, self.rect.centery)
				elif self.close_enough and target.alive:
					if not self.pseudo_rect.colliderect(target.rect):
						self.close_enough = False
					self.attack(surface, target)
					self.attacking = True

			elif self.idling == False:
				#movement
				if self.direction == -1:
					dx = -SPEED
					self.flip = True #left 
					self.running = True 

				elif self.direction == 1:
					dx = SPEED
					self.flip = False #right
					self.running = True

				self.move_counter += 1
				#update vision
				self.vision.center = (self.rect.centerx + 90 * self.direction, self.rect.centery)

				if self.move_counter > 30:
					self.direction *= -1
					self.move_counter *= -1

			else:
				self.idling_counter -= 1
				if self.idling_counter <= 0:
					self.idling = False

		#apply gravity
		self.vel_y += GRAVITY 
		dy += self.vel_y

		#ensure stays on screen
		if self.rect.bottom + dy > SCREEN_HEIGHT - 66:
			self.vel_y = 0
			self.jump = False
			dy = SCREEN_HEIGHT - 66 - self.rect.bottom	

		#update ai position
		self.rect.x += dx
		self.rect.y += dy

	def attack(self, surface, target):
		if self.char_type == 'Player':
			self.attacking_rect.center = (self.rect.centerx + 90 * self.direction, self.rect.centery)
		if self.char_type == 'Skeleton':
			self.attacking_rect.center = (self.rect.centerx + 50 * self.direction, self.rect.centery)
		if self.attacking_rect.colliderect(target.rect) and self.char_type == 'Player':
			target.health -= random.randint(8, 20)
			target.hit = True
			if target.hit:
				target.check_alive()
				if target.lucky_skel and not target.alive and not target.collected:
					self.score += random.randint(25,50)
					target.collected = True
					print(self.score)
				elif not target.alive and not target.collected:
					self.score += random.randint(10,16)
					target.collected = True
					print(self.score)
		if self.attacking_rect.colliderect(target.rect) and self.char_type == 'Skeleton':
			target.health -= random.randint(8, 18)
			target.hit = True
		elif self.lucky_skel and self.attacking_rect.colliderect(target.rect) and self.char_type == 'Skeleton':
			target.health -= random.randint(20, 45)
			target.hit = True


		#pygame.draw.rect(surface, (0, 0, 255), self.attacking_rect)

	def update_action(self, new_action):
		#check if the new action is different to the previous one
		if new_action != self.action:
			self.action = new_action
			#update/reset the animation settings 
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()

	#function for drawing health bars
	def draw_health_bar(self, surface):
		if self.char_type == 'Player':
			ratio = self.health/100
			health_bar_len = 63
		if self.char_type == 'Skeleton' and not self.lucky_skel:
			ratio = self.health/40
			health_bar_len = 66
		if self.char_type == 'Skeleton' and self.lucky_skel:
			ratio = self.health/80
			health_bar_len = 66 
		if self.alive and not self.lucky_skel:
			pygame.draw.rect(surface, BLACK, (self.rect.x-1, self.rect.y-6, health_bar_len+2, 7)) #health bar outline
			pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y-5, health_bar_len, 5)) #health previously
			pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y-5, health_bar_len*ratio, 5)) #health remaining
		#gold health bar for boss skeleton
		elif self.alive and self.lucky_skel:
			pygame.draw.rect(surface, BLACK, (self.rect.x-1, self.rect.y-6, health_bar_len+2, 7)) #health bar outline
			pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y-5, health_bar_len, 5)) #health previously
			pygame.draw.rect(surface, GOLD, (self.rect.x, self.rect.y-5, health_bar_len*ratio, 5)) #health remaining

	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(4)


	def draw(self, surface):
		img = pygame.transform.flip(self.image, self.flip, False)
		#pygame.draw.rect(surface, (255, 0 , 0), self.rect)
		#pygame.draw.rect(surface, GREEN, self.vision)
		if self.alive:
			surface.blit(img, self.rect)
		elif self.respawn_timer < 250:
			self.respawn_timer += 1
			surface.blit(img, (self.rect.x, 715))
			


	




		