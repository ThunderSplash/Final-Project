import pygame
from pygame import mixer
import os
from pygame.locals import *
import random
import csv
import button


mixer.init()
pygame.init()

screen_width = 1920
screen_height = 1080



screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Final_Project')
########################################################################################
#Particle Class
class Particle:
    def __init__(self, pos):
        self.x, self.y = pos[0], pos[1]
        self.vx, self.vy = random.randint(-1, 1), random.randint(-70, 0)*.01
        self.rad = 2

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.rad)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        if random.randint(0, 100) < 40:
            self.rad -= 1

class Dust:
    def __init__(self, pos):
        self.pos = pos
        self.particles = []
        for i in range(100):
            self.particles.append(Particle(self.pos))

    def update(self):
        for i in self.particles:
            i.update()
            self.particles = [particle for particle in self.particles if particle.rad > 0]

    def draw(self, screen):
        for i in self.particles:
            i.draw(screen)
        

#set framerate
clock = pygame.time.Clock()
FPS = 60

#define game variables
GRAVITY = 0.15
SCROLL_THRESH = 210
ROWS = 30
COLS = 150 
TILE_SIZE = screen_height // ROWS
TILE_TYPES = 30
Max_levels = 2
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False

#define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

#load music and sounds
pygame.mixer.music.load('data/audio/game3.mp3')
pygame.mixer.music.set_volume(0.9)
pygame.mixer.music.play(-1, 0.0, 5000)

#load images
#button images
start_img = pygame.image.load('data/images/start_btn.png').convert_alpha()
exit_img = pygame.image.load('data/images/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('data/images/restart_btn.png').convert_alpha()
#background
forest1 = pygame.image.load('data/images/forest1.png').convert_alpha()
forest2 = pygame.image.load('data/images/forest2.png').convert_alpha()
forest3 = pygame.image.load('data/images/forest3.png').convert_alpha()
forest4 = pygame.image.load('data/images/forest4.png').convert_alpha()
forest5 = pygame.image.load('data/images/forest5.png').convert_alpha()
forest6 = pygame.image.load('data/images/forest6.png').convert_alpha()
forest7 = pygame.image.load('data/images/forest7.png').convert_alpha()
forest8 = pygame.image.load('data/images/forest8.png').convert_alpha()
forest9 = pygame.image.load('data/images/forest9.png').convert_alpha()
forest10 = pygame.image.load('data/images/forest10.png').convert_alpha()
forest11 = pygame.image.load('data/images/forest11.png').convert_alpha()
forest12 = pygame.image.load('data/images/forest12.png').convert_alpha()
#store tile in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'data/Tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

#bulltes
bullet_img = pygame.image.load('data/images/bullet1.png').convert_alpha()
#grenade
grenade_img = pygame.image.load('data/images/grenade.png').convert_alpha()
#pick up boxes
health_box_img = pygame.image.load('data/images/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('data/images/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('data/images/grenade_box.png').convert_alpha()
item_boxes = { 
    'Health'  : health_box_img,
    'Ammo'    : ammo_box_img,
    'Grenade' : grenade_box_img
}
   

#define colors
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0,255, 0)
BLACK = (0,0,0)
PINK = (235, 65, 54)

#define font
font = pygame.font.SysFont('Blue', 30)
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg():
    screen.fill(BG)
    width = forest12.get_width()
    for x in range(12):
        screen.blit(forest12, ((x * width) - bg_scroll * 0.05, 0))
        screen.blit(forest11, ((x * width) - bg_scroll * 0.4,screen_height - forest11.get_height()))
        screen.blit(forest10, ((x * width) - bg_scroll * 0.5, screen_height - forest10.get_height()))
        screen.blit(forest9, ((x * width) - bg_scroll * 0.55, screen_height - forest9.get_height()))
        screen.blit(forest8, ((x * width) - bg_scroll * 0.6, screen_height - forest8.get_height()))
        screen.blit(forest7, ((x * width) - bg_scroll * .7, screen_height - forest7.get_height()))
        screen.blit(forest6, ((x * width) - bg_scroll * .8, screen_height - forest6.get_height()))
        screen.blit(forest3, ((x * width) - bg_scroll * .9, screen_height - forest3.get_height()))
        screen.blit(forest4, ((x * width) - bg_scroll * .9, screen_height - forest4.get_height()))
        screen.blit(forest5, ((x * width) - bg_scroll * 1, screen_height - forest5.get_height()))
        screen.blit(forest2, ((x * width) - bg_scroll * 2, screen_height - forest2.get_height()))
        screen.blit(forest1, ((x * width) - bg_scroll * 3, screen_height - forest1.get_height())) 

#function to reset level
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    #create empty tile list
    data = []
    for row in range(ROWS):
        r =[-1] * COLS
        data.append(r)
    
    return data

#EDLEN RING IDLE MONSTERS!!!!!!!!!!!!!
class Elden(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.sprites = []
        self.sprites.append(pygame.image.load('vampire1.png'))
        self.sprites.append(pygame.image.load('vampire2.png'))
        self.sprites.append(pygame.image.load('vampire3.png'))
        self.sprites.append(pygame.image.load('vampire4.png'))
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.topleft = [1400,910]

    def update(self, speed):
        self.current_sprite += speed

        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0

        self.image = self.sprites[int(self.current_sprite)]


# edlen sprite
moving_sprites = pygame.sprite.Group()
elden = Elden(200, 200)
moving_sprites.add(elden)

class Elden2(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.sprites = []
        self.sprites.append(pygame.image.load('woman-idle-1.png'))
        self.sprites.append(pygame.image.load('woman-idle-2.png'))
        self.sprites.append(pygame.image.load('woman-idle-3.png'))
        self.sprites.append(pygame.image.load('woman-idle-4.png'))
        self.sprites.append(pygame.image.load('woman-idle-5.png'))
        self.sprites.append(pygame.image.load('woman-idle-6.png'))
        self.sprites.append(pygame.image.load('woman-idle-7.png'))
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.topleft = [1800,960]

    def update(self, speed):
        self.current_sprite += speed

        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0

        self.image = self.sprites[int(self.current_sprite)]


# edlen sprite
moving_sprites2 = pygame.sprite.Group()
elden2 = Elden2(200, 200)
moving_sprites2.add(elden2)

class Elden3(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.sprites = []
        self.sprites.append(pygame.image.load('hero-idle-1.png'))
        self.sprites.append(pygame.image.load('hero-idle-2.png'))
        self.sprites.append(pygame.image.load('hero-idle-3.png'))
        self.sprites.append(pygame.image.load('hero-idle-4.png'))
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.topleft = [1310,920]

    def update(self, speed):
        self.current_sprite += speed

        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0

        self.image = self.sprites[int(self.current_sprite)]


# edlen sprite
moving_sprites3 = pygame.sprite.Group()
elden3 = Elden3(200, 200)
moving_sprites3.add(elden3)


class Elden4(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.sprites = []
        self.sprites.append(pygame.image.load('ogre-idle1.png'))
        self.sprites.append(pygame.image.load('ogre-idle2.png'))
        self.sprites.append(pygame.image.load('ogre-idle3.png'))
        self.sprites.append(pygame.image.load('ogre-idle4.png'))
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.topleft = [1540,926]

    def update(self, speed):
        self.current_sprite += speed

        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0

        self.image = self.sprites[int(self.current_sprite)]


# edlen sprite
moving_sprites4 = pygame.sprite.Group()
elden4 = Elden4(10000, 10000)
moving_sprites4.add(elden4)


class Elden5(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.sprites = []
        self.sprites.append(pygame.image.load('idle1.png'))
        self.sprites.append(pygame.image.load('idle2.png'))
        self.sprites.append(pygame.image.load('idle3.png'))
        self.sprites.append(pygame.image.load('idle4.png'))
        self.sprites.append(pygame.image.load('idle5.png'))
        self.sprites.append(pygame.image.load('idle6.png'))
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.topleft = [1540,860]

    def update(self, speed):
        self.current_sprite += speed

        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0

        self.image = self.sprites[int(self.current_sprite)]


# edlen sprite
moving_sprites5 = pygame.sprite.Group()
elden5 = Elden5(200, 200)
moving_sprites5.add(elden5)


class Elden6(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.sprites = []
        self.sprites.append(pygame.image.load('demon1.png'))
        self.sprites.append(pygame.image.load('demon2.png'))
        self.sprites.append(pygame.image.load('demon3.png'))
        self.sprites.append(pygame.image.load('demon4.png'))
        self.sprites.append(pygame.image.load('demon5.png'))
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.topleft = [1650,862]

    def update(self, speed):
        self.current_sprite += speed

        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0

        self.image = self.sprites[int(self.current_sprite)]


# edlen sprite
moving_sprites6 = pygame.sprite.Group()
elden6 = Elden6(10, 10)
moving_sprites6.add(elden6)

class Elden7(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.sprites = []
        self.sprites.append(pygame.image.load('centaur1.png'))
        self.sprites.append(pygame.image.load('centaur2.png'))
        self.sprites.append(pygame.image.load('centaur3.png'))
        self.sprites.append(pygame.image.load('centaur4.png'))
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.topleft = [1500,868]

    def update(self, speed):
        self.current_sprite += speed

        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0

        self.image = self.sprites[int(self.current_sprite)]


# edlen sprite
moving_sprites7 = pygame.sprite.Group()
elden7 = Elden7(150, 150)
moving_sprites7.add(elden7)

class Elden8(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.sprites = []
        self.sprites.append(pygame.image.load('angel1.png'))
        self.sprites.append(pygame.image.load('angel2.png'))
        self.sprites.append(pygame.image.load('angel3.png'))
        self.sprites.append(pygame.image.load('angel4.png'))
        self.sprites.append(pygame.image.load('angel5.png'))
        self.sprites.append(pygame.image.load('angel6.png'))
        self.sprites.append(pygame.image.load('angel7.png'))
        self.sprites.append(pygame.image.load('angel8.png'))
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.topleft = [1050,870]

    def update(self, speed):
        self.current_sprite += speed

        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0

        self.image = self.sprites[int(self.current_sprite)]


# edlen sprite
moving_sprites8 = pygame.sprite.Group()
elden8 = Elden8(200, 200)
moving_sprites8.add(elden8)


class Elden9(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.sprites = []
        self.sprites.append(pygame.image.load('a (1).png'))
        self.sprites.append(pygame.image.load('a (2).png'))
        self.sprites.append(pygame.image.load('a (3).png'))
        self.sprites.append(pygame.image.load('a (4).png'))
        self.sprites.append(pygame.image.load('a (5).png'))
        self.sprites.append(pygame.image.load('a (6).png'))
        self.sprites.append(pygame.image.load('a (7).png'))
        self.sprites.append(pygame.image.load('a (8).png'))
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.topleft = [1300,870]

    def update(self, speed):
        self.current_sprite += speed

        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0

        self.image = self.sprites[int(self.current_sprite)]


# edlen sprite
moving_sprites9 = pygame.sprite.Group()
elden9 = Elden9(200, 200)
moving_sprites9.add(elden9)

#######################################################################################

class Character(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        #ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        #load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            #reset temporary list of images
            temp_list = []
            #count number of files in the folder
            num_of_frames = len(os.listdir(f'data/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'data/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
            
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        #reset movemement variables
        screen_scroll = 0
        dx = 0
        dy = 0

        #assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
            dust.append(Dust(self.rect.midbottom))
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
            dust.append(Dust(self.rect.midbottom))
            
        

        #jump
        if self.jump == True and self.in_air == False:
            self.vel_y= -5
            self.jump = False
            self.in_air = True
            
            

        #apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y
    


        #check for collision
        for tile in world.obstacle_list:
            #check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                #if the ai has hit a wall then make it turn around
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            #check collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #check if below the ground (jumping)
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #check if above the ground (falling)
                elif self.vel_y >= 1:
                    self.vel_y = 1
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        #check for collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0 
        
        #check for collision with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True 

        #check if fallen off the map
        if self.rect.bottom > screen_height:
            self.health = 0


        #check if going off the edges of the screen
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > screen_width:
                dx = 0

        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        #update scroll based on player position
        if self.char_type == 'player':
            if (self.rect.right > screen_width - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - screen_width)\
                or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx
        
        return screen_scroll, level_complete

        
    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.5 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            #reduce ammo
            self.ammo -= 1
    
    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 100) == 1:
                self.update_action(0) #0: idle
                self.idling = True
                self.idling_counter = 50
            #check if the ai is near the player
            if self.vision.colliderect(player.rect):
                #stop running and face the player
                self.update_action(0) #0: idle
                #shoot
                self.shoot()
            else:    
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1) #1:run
                    self.move_counter += 1
                    #update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    
                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
            
            #scroll
            self.rect.x += screen_scroll


    def update_animation(self):
        #update animation
        ANIMATION_COOLDOWN = 90
        #update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        #check if eneough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if the animation has run out then reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0


    def update_action(self, new_action):
        #check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()


    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        #iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 24 and tile <= 25:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)  
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)   
                    elif tile == 9:#create player
                        player = Character('player', x * TILE_SIZE, y * TILE_SIZE, 1.2, 1.3, 10, 3)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 23:#create enemies
                        enemy = Character('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.1, 1, 100, 3)
                        enemy_group.add(enemy)
                    elif tile == 26:#create ammo box
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 27:#create grenade box
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 28:#create health box
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 29:#create exit
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)  
        
        return player, health_bar        
                    
    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        #scroll
        self.rect.x += screen_scroll
        #check if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            #check what kind of box it was
            if self.item_type =='Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type =='Ammo':
                player.ammo += 5
            elif self.item_type =='Grenade':
                player.grenades += 3
                #delete the item box
            self.kill()

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        #update with new health
        self.health = health
        #calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y -2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        #move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        #check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > screen_width:
            self.kill()
        
        #check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        #check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()



class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -1
        self.speed = 1
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction     

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y  

    
        #check for collision with level
        for tile in world.obstacle_list:
            #check collsion with walls
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed 
             #check collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                #check if below the ground (jumping) thrown up
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #check if above the ground (falling)
                elif self.vel_y >= 1:
                    self.vel_y = 1
                    dy = tile[1].top - self.rect.bottom

        #update grenade position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        #countdown timer
        self.timer -= 1 
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            #do damage to anyone that is nearby
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50
                    


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 11):
            img = pygame.image.load(f'data/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0  

    def update(self):
        #scroll
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 4
        #update explosion animation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0 
            self.frame_index += 1
            #if the animation is complete then delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]




#create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

class ScreenFade():
    def __init__(self, direction, color, speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:#whole screen fade
            pygame.draw.rect(screen, self.color, (0 - self.fade_counter, 0, screen_width // 2, screen_height))
            pygame.draw.rect(screen, self.color, (screen_width // 2 + self.fade_counter, 0, screen_width, screen_height))
            pygame.draw.rect(screen, self.color, (0, 0 - self.fade_counter, screen_width, screen_height // 2 ))
            pygame.draw.rect(screen, self.color, (0, screen_height // 2 + self.fade_counter, screen_width, screen_height))

        if self.direction == 2:#vertical screen fade down
            pygame.draw.rect(screen, self.color, (0, 0, screen_width, 0 + self.fade_counter))
        if self.fade_counter >= screen_width:
            fade_complete = True

        return fade_complete

#creeate screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)


#create buttons
start_button = button.Button(screen_width // 2 - 130, screen_height // 2 - 150, start_img, 1)
exit_button = button.Button(screen_width // 2 - 110, screen_height // 2 + 50, exit_img, 1)
restart_button = button.Button(screen_width // 2 - 100, screen_height // 2 - 50, restart_img, 2)


#create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
#load in level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)

dust = []
run = True
while run:
    clock.tick(FPS)

    if start_game == False:
        #draw menu
        screen.fill(BG)
        #add buttons
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
    else:
        #update background
        draw_bg()
        #draw world
        world.draw()
        #screen.blit(bg_img, (0, 0))
        #show player health
        health_bar.draw(player.health)
        #show ammo
        draw_text('Spells: ', font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet_img, (90 + (x * 20), 40))
        #show grenades
        draw_text('Magic Potions: ', font, WHITE, 10, 60)
        for x in range(player.grenades):
            screen.blit(grenade_img, (160 + (x * 15), 60))
        
  
        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()
        
        player.move(moving_left, moving_right)

        #update player actions
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)
    
        #show intro
        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0
        #update player actions
        if player.alive:
            #shoot bullets
            if shoot:
                player.shoot()
            #throw grenade
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), \
                            player.rect.top, player.direction)
                grenade_group.add(grenade)
                #reduce grenades
                player.grenades -= 1
                grenade_thrown = True
            if player.in_air:
                player.update_action(2)#2: jump
            elif moving_left or moving_right:
                player.update_action(1)#1: run
            else:
                player.update_action(0)#0: idle
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            #check if player has completed the level
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= Max_levels: 
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)

        else:
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)




        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        #keyboard pressess
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_p:
                shoot = True
            if event.key == pygame.K_o:
                grenade = True
            if event.key == pygame.K_SPACE and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False
             
     
        #keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_p:
                shoot = False
            if event.key == pygame.K_o:
                grenade = False
                grenade_thrown = False

# Activates Dust mechanic NOT SURE IF I LIKE IT OR NOT
    #for d in dust:
        #d.draw(screen)
        #d.update()
    moving_sprites.draw(screen)
    moving_sprites.update(0.08)
    moving_sprites2.draw(screen)
    moving_sprites2.update(0.08)
    moving_sprites3.draw(screen)
    moving_sprites3.update(0.08)
    moving_sprites4.draw(screen)
    moving_sprites4.update(0.02)
    moving_sprites5.draw(screen)
    moving_sprites5.update(0.12)
    moving_sprites6.draw(screen)
    moving_sprites6.update(0.06)
    moving_sprites7.draw(screen)
    moving_sprites7.update(0.08)
    moving_sprites8.draw(screen)
    moving_sprites8.update(0.15)
    moving_sprites9.draw(screen)
    moving_sprites9.update(0.15)
   

    pygame.display.update()

pygame.quit()




