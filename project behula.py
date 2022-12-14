# -*- coding: utf-8 -*-
"""
Created on Sat Dec 10 23:57:18 2022

@author: Rafid
"""
from pygame import mixer
import pygame
import math
import random
import os

mixer.init()
pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 768

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Project X')

# set framerate
clock = pygame.time.Clock()
FPS = 60

# define game variables
GRAVITY = 0.75

# define player action variables
moving_left = False
moving_right = False
slide = False
global_speed = 10

bg_scroll = 0
# define colours
BG = (144, 201, 120)

# load sound
jump_fx = pygame.mixer.Sound('audio/jump_audio.mp3')
jump_fx.set_volume(1)

# load images
pine1_img = pygame.image.load('asset/pine1.png').convert_alpha()
pine2_img = pygame.image.load('asset/bg2.png').convert_alpha()
mountain_img = pygame.image.load('asset/mountain.png').convert_alpha()
sky_img = pygame.image.load('asset/sky_cloud.png').convert_alpha()
tiles = math.ceil(SCREEN_WIDTH / pine2_img.get_width()) + 1


def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(0, tiles):
        # screen.blit(sky_img, ((x * width) - bg_scroll * 1, 0))
        # screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        # screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        # screen.blit(pine2_img, pine2_img.get_rect())
        screen.blit(pine2_img, (x * SCREEN_WIDTH + bg_scroll, 0))
        pygame.draw.rect(screen, (255, 0, 0), pine2_img.get_rect(), 1)


class Behula(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.flip = False
        self.jump = False
        self.in_air = True
        self.slide = False
        self.is_sliding = False
        self.vel_y = 0
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # load all images for the players
        animation_types = ['run', 'jump', 'slide']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(
                f'asset/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(
                    f'asset/{self.char_type}/{animation}/{i}.png')
                img = pygame.transform.scale(
                    img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self, moving_left, moving_right):
        # reset movement variables
        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1

        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # jump
        if self.jump and not self.in_air:
            self.vel_y = -15
            self.jump = False
            self.in_air = True

        # apply gravity
        if self.in_air:
            self.vel_y += GRAVITY
            if self.vel_y > 100:
                self.vel_y
            dy += self.vel_y
            # check collision
            if self.rect.bottom + dy > 615:
                dy = 615 - self.rect.bottom
                self.in_air = False
        self.rect.y += dy

        # slide
        if self.slide and not self.is_sliding:
            self.vel_y = -15
            self.slide = False
            self.is_sliding = True

        if self.is_sliding:
            self.vel_y += GRAVITY
            if self.vel_y > 50:
                # reset player position after slide
                player.update_action(0)
                self.is_sliding = False
                self.rect.y = 380
            else:
                # keep player sliding
                self.rect.y = 550

        # update rectangle position
        if (self.rect.x + dx >= 10 and self.rect.x + dx <= 1150):
            self.rect.x += dx

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        # dfsdf
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(pygame.transform.flip(
            self.image, self.flip, False), self.rect)


class Obstacle(pygame.sprite.Sprite):

    def __init__(self, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.speed = speed
        self.scale = scale
        self.x = x
        self.y = y
        # Load images for the obstacles
        self.obstacle_images = []
        # 'stone1', 'stone2', 'tree1', 'tree2'
        for image_name in ['stone1', 'stone2', 'tree1']:
            img = pygame.image.load(
                f'asset/{image_name}.png').convert_alpha()
            self.image = pygame.transform.scale(
                img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)
            self.obstacle_images.append(img)

        #
        self.image = random.choice(self.obstacle_images)

        # position the obstacle just off the right side of the screen
        self.x = SCREEN_WIDTH
        # self.y = SCREEN_HEIGHT - self.image.get_height() - 200

        # set initial rect
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def reset(self):
        # assign a new position and reset
        self.image = random.choice(self.obstacle_images)
        self.x = SCREEN_WIDTH
        # self.y = SCREEN_HEIGHT - self.image.get_height()

    def update(self):
        # move obs to left
        self.x -= self.speed
        # update the rect
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        # update the mask
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self):
        # screen.blit(self.image, (self.x, self.y))
        screen.blit(self.image, self.rect)


player = Behula('behula', 200, 520, 0.7, 5)

# create the obstacle
obstacles_group = pygame.sprite.Group()
obstacle = Obstacle(200, 555, 2, global_speed)
obstacles_group.add(obstacle)

# player2 = Soldier('enemy',400, 200, 0.5,5)


run = True
while run:

    clock.tick(FPS)

    draw_bg()
    bg_scroll -= global_speed

    # reset scroll
    if abs(bg_scroll) > pine2_img.get_width():
        bg_scroll = 0

    player.update_animation()
    player.draw()
    # update player actions
    if player.in_air:
        # jump
        player.update_action(1)
    elif player.is_sliding:
        # slide
        player.update_action(2)
    else:
        # run
        player.update_action(0)

    player.move(moving_left, moving_right)

    obstacle.draw()
    obstacle.update()
    # add to score and reset the obstacle when it goes off-screen
    if obstacle.x < obstacle.image.get_width() * -1:
        obstacle.reset()

    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            run = False
        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                if player.in_air == False and not player.is_sliding:
                    player.jump = True
                    jump_fx.play()
                # player.jump = True
                # jump_fx.play()
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_s:
                if not player.is_sliding and not player.slide and not player.in_air:
                    player.slide = True

        # keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                jump = False
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_s:
                slide = False

    pygame.display.update()

pygame.quit()
