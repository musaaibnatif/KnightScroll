import pygame
from entity import Entity
import random

pygame.init()

#create game window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = SCREEN_WIDTH * .8

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("A Knight's Last Stand")
#set framerate
clock = pygame.time.Clock()
FPS = 60

#define colors
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)


#load bg image
bg_image = pygame.image.load("img/Background/Background.png").convert_alpha()

#function for drawing bg 
def draw_bg():
	scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT)) #scale bg img to fit screen dimensions
	screen.blit(scaled_bg, (0, 0))	

#create instance of player
player = Entity("Player", 90, 678, 3)
def call_player():
	player.draw_health_bar(screen) #healthbar
	player.move(SCREEN_HEIGHT, screen, skeleton) #input
	player.update()  #refresh actions
	player.draw(screen) #refresh frames

#create instance of skeleton
random_x = random.randint(100, 900)
skeleton = Entity("Skeleton", random_x, 688, 3)

def call_skeleton():
	skeleton.draw_health_bar(screen) #healthbar
	skeleton.ai(screen, player)
	skeleton.update() #refresh actions
	skeleton.draw(screen) #refresh frames


#function that shows score
def show_score():
	font = pygame.font.Font('freesansbold.ttf', 26)
	score = player.score
	text = font.render(f'{score}', True, BLACK) 
	score = player.score
	screen.blit(text, (0, 0))

respawn_timer = 0

#game loop
run = True
while run: 

	#set fps
	clock.tick(FPS)

	#draw bg
	draw_bg() 

	call_player()
	call_skeleton()

	skeleton.check_alive()

	if not skeleton.alive and respawn_timer == 500:
		random_x = random.randint(100, 900)
		skeleton = Entity("Skeleton", random_x, 688, 3)
		respawn_timer = 0
	elif not skeleton.alive:
		respawn_timer += 1




	#display score
	show_score()

	#event handler
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	#update display
	pygame.display.update()

#exit pygame
pygame.quit()