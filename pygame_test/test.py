import pygame
import neat
import time
import os
import random

WIN_WIDTH = 500
WIN_HEIGHT = 800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("../static", "imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("../static", "imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("../static", "imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("../static", "imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("../static", "imgs", "base.png")))
BACKGROUND_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("../static", "imgs", "bg.png")))

class Bird():
    '''Represents a Bird object'''
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25 # how much the bird can rotate
    ROT_VEL = 20 # how fast the bird rotates
    ANIMATION_TIME = 5 # how fast the animation changes between the bird

    def __init__(self, x, y):
        self.x = x # bird's position in the x axis
        self.y = y # bird's position in the y axis
        self.tilt = 0 # the direction the bird is pointing in from -90 (completely down) to MAX_ROTATION (up)
        self.tick_count = 0  # counting the ticks of the game loop, how many ticks went by since the last jump
        self.vel = 0 # how fast the bird is travelling
        self.height = self.y # keeps track of where the bird jumped from
        self.img_count = 0
        self.img = self.IMGS[0]
    
    def jump(self):
        '''Changes the bird to go in the upward direction'''
        self.vel = -10.5 # change the velocity to point up (negative is up)
        self.tick_count = 0 # reset tick count when jump
        self.height = self.y # set the height of where we jumped from

    def move(self):
        '''Calculates how the bird is moving and whether to tilt the bird pointing up or down'''
        self.tick_count += 1
        displacement = self.vel*self.tick_count + 1.5*self.tick_count**2 # how many pixels we are moving the bird
        # terminal velocity in the downward direction
        if displacement > 16:
            displacement = 16
        # if moving upwards, move up a bit more
        elif displacement < 0:
            displacement -= 2
        # change the position in the y axis by the calculated displacement
        self.y += displacement

        #### to calculate the tilt of the bird ###
        # if we're moving upwards or have recently jumped, change the tilt of the bird to look up
        if (displacement < 0) or (self.y < self.height + 50):
            if (self.tilt < self.MAX_ROTATION):
                # set the tilt of the bird to look up
                self.tilt = self.MAX_ROTATION
        # else, then we're moving the downwards so tilt the bird down
        else:
            if (self.tilt > -90):
                # if the bird is not tilted completely downwards, keep turning the bird down by the rotational velocity
                self.tilt -= self.ROT_VEL
    
    def draw(self, window):
        '''Draws and animates the bird flapping'''
        self.img_count += 1

        # To animate the bird flapping, change images based on the animation time of the bird
        # rotates between wings up, wings parallel, and wings down
        if (self.img_count < self.ANIMATION_TIME) or (self.img_count == self.ANIMATION_TIME*4):
            # wings up
            self.img = self.IMGS[0]
            if (self.img_count == self.ANIMATION_TIME*4):
                # reset the animation back to 0
                self.img_count = 0
        elif (self.img_count < self.ANIMATION_TIME*2) or (self.img_count >= self.ANIMATION_TIME*3 and self.img_count < self.ANIMATION_TIME*4):
            # wings parallel
            self.img = self.IMGS[1]
        elif (self.img_count >= self.ANIMATION_TIME*2) and (self.img_count < self.ANIMATION_TIME*3):
            # wings down
            self.img = self.IMGS[2]

        if (self.tilt <= -80):
            # if the bird has been falling for awhile then don't flap
            self.img = self.IMGS[1] 
            self.img_count = self.ANIMATION_TIME*2
        
        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        rect = rotated_img.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        window.blit(rotated_img, rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe():
    '''Represent the pipe object'''
    GAP = 200 # the space between the two pipes
    VEL = 5

    def __init__(self, x):
        self.x = x # position of the pipe in the x axis
        self.height = 0 # the height of the pipe in the y axis
        self.top = 0 # top of the pipe
        self.bottom = 0 # bottom of the pipe
        self.pipe_top = pygame.transform.flip(PIPE_IMG, False, True) # the flipped pipe on the top
        self.pipe_bottom = PIPE_IMG # the pipe on the bottom

        self.passed = False # if bird has passed the pipe
        self.set_height()
    
    def set_height(self):
        '''Randomly generates the height of the pipe'''
        self.height = random.randrange(40, 450)
        self.top = self.height
    
    def draw(self, window):
        '''Draws the pipe image onto the background window'''
        width_height = self.pipe_top.get_size()
        self.pipe_top = pygame.transform.scale(self.pipe_top, (width_height[0], self.height))
        window.blit(self.pipe_top, (0,50))


def draw_window(window, bird, pipe):
    '''Draws the background image on the window and the bird flapping'''
    window.blit(BACKGROUND_IMG, (0, 0))
    bird.draw(window)
    #pipe.set_height()
    pipe.draw(window)
    pygame.display.update()

def main():
    bird = Bird(WIN_WIDTH/2-25, 200)
    pipe = Pipe(20)
    pipe.set_height()
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    run = True
    clock = pygame.time.Clock()
    while run:
        clock.tick(30) # sets the tick rate so that only 30 frames pass per game tick
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        bird.move()
        draw_window(win, bird, pipe)
    pygame.quit()

if __name__ == "__main__":
    main()
