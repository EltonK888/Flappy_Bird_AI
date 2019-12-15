import pygame
import neat
import time
import os
import random

WIN_WIDTH = 600
WIN_HEIGHT = 800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("../static", "imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("../static", "imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("../static", "imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("../static", "imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("../static", "imgs", "base.png")))
BACKGROUND_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("../static", "imgs", "bg.png")))

class Bird():
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25 # how much the bird can rotate
    ROT_VEL = 20 # how fast the bird rotates
    ANIMATION_TIME = 5 # how fast the animation changes between the bird

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]
    
    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        displacement = self.vel*self.tick_count + 1.5*self.tick_count**2
        if displacement > 16:
            displacement = 16
        elif displacement < 0:
            displacement -= 2

def main():
    print("test")

if __name__ == "__main__":
    main()
