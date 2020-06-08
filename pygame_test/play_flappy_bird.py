import os
import random
import time
import pygame

pygame.font.init() # creating the pygame font
WIN_WIDTH = 500
WIN_HEIGHT = 800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("../static", "imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("../static", "imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("../static", "imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("../static", "imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("../static", "imgs", "base.png")))
BACKGROUND_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("../static", "imgs", "bg.png")))
FONT = pygame.font.SysFont("comicsans", 100) # sets the style of the font in pygame

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
            if self.tilt < self.MAX_ROTATION:
                # set the tilt of the bird to look up
                self.tilt = self.MAX_ROTATION
        # else, then we're moving the downwards so tilt the bird down
        else:
            if self.tilt > -90:
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

        if self.tilt <= -80:
            # if the bird has been falling for awhile then don't flap
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        rect = rotated_img.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        window.blit(rotated_img, rect.topleft)

    def get_mask(self):
        '''Returns a Mask for the bird'''
        return pygame.mask.from_surface(self.img)


class Pipe():
    '''Represents a pipe object'''
    GAP = 190 # the space between the two pipes
    VEL = 5 # the speed at which the background (pipes and base) moves in the x direction

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
        self.height = random.randrange(80, 450)
        bottom_pipe_height = WIN_HEIGHT-self.height-self.GAP
        bottom_pipe_coords = WIN_HEIGHT-bottom_pipe_height
        self.top = WIN_HEIGHT-self.GAP-bottom_pipe_height-self.pipe_top.get_size()[1]
        self.bottom = WIN_HEIGHT-bottom_pipe_height

    def draw(self, window):
        '''Draws the pipe image onto the background window'''
        pipe_height = self.pipe_top.get_size()[1]
        bottom_pipe_height = WIN_HEIGHT-self.height-self.GAP
        bottom_pipe_coords = WIN_HEIGHT-bottom_pipe_height
        window.blit(self.pipe_top, (self.x, WIN_HEIGHT-self.GAP-bottom_pipe_height-pipe_height))
        window.blit(self.pipe_bottom, (self.x, bottom_pipe_coords))

    def move(self):
        '''Moves the pipes a fixed distance based on VEL'''
        self.x -= self.VEL

    def collision(self, bird):
        '''Determins if the pipe has collided with the bird'''
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.pipe_top)
        bottom_mask = pygame.mask.from_surface(self.pipe_bottom)
        top_mask_offset = (int(self.x - bird.x), self.top - round(bird.y)) 
        bottom_mask_offset = (int(self.x - bird.x), self.bottom - round(bird.y)) 

        top_overlap = bird_mask.overlap(top_mask, top_mask_offset)
        bottom_overlap = bird_mask.overlap(bottom_mask, bottom_mask_offset)

        if top_overlap or bottom_overlap:
            return True
        else:
            return False

class Base():
    '''Represents the base (ground) of the game'''
    VEL = 5 # the speed at which the background (pipes and base) moves in the x direction
    BASE_WIDTH = BASE_IMG.get_width()

    def __init__(self):
        self.x = 0 # the position in the x direction where the base starts
        self.x2 = self.BASE_WIDTH # position where the second base starts which makes it look like one continuous movement
        self.y = WIN_HEIGHT-100 # the position in the y direction where the base will be
        self.base = BASE_IMG # the image of the base

    def draw(self, window):
        '''Draws the base on the window in its x and y coordinates'''
        window.blit(self.base, (self.x, self.y))
        window.blit(self.base, (self.x2, self.y))

    def move(self):
        '''Moves the base left by VEL pixels'''
        self.x -= self.VEL
        self.x2 -= self.VEL
        if (self.x + self.BASE_WIDTH < 0):
            # if the first base has moved off the screen, redraw it at the end of the second base
            self.x = self.x2 + self.BASE_WIDTH
        if (self.x2 + self.BASE_WIDTH < 0):
            # if the second base has moved off the screen
            self.x2 = self.x + self.BASE_WIDTH

    def collision(self, bird):
        '''Determins if the base has collided with the bird'''
        return bird.y >= self.y-40

    def get_x(self):
        '''Return the x coordinate of the base'''
        return self.x



def draw_window(window, base, bird, pipes, score):
    '''Draws the assets onto the game window'''
    window.blit(BACKGROUND_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(window)
    text = FONT.render(str(score), 1, (255,255,255))
    window.blit(text, (WIN_WIDTH-10-text.get_width(), 10))
    base.draw(window)
    bird.draw(window)
    pygame.display.update()


def main():

    # set up game assets
    bird = Bird(WIN_WIDTH/2-25, WIN_HEIGHT/2-100) # create a new bird and set its position in the middle
    pipe = Pipe(WIN_WIDTH)
    pipes = [pipe] # create the first pipe and set its height randomly
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT)) # create the game window
    base = Base()
    run = True
    clock = pygame.time.Clock()

    score = 0

    while run:
        clock.tick(30) # sets the tick rate so that only 30 frames pass per game tick
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                bird.jump()
        base.move()
        bird.move()
        add_pipe = False
        pipes_to_remove = []
        for pipe in pipes:
            # for every bird, check if it has collided with a pipe
            if pipe.collision(bird):
                run = False
                print("bird has collided! Your score was {}".format(score))
            if pipe.x + PIPE_IMG.get_width() < bird.x and not pipe.passed:
                if bird.y < 0:
                    # case where the bird flies up off the game screen and passes a pipe, it should collide
                    run = False
                    print("bird has collided! Your score was {}".format(score))
                else:
                    # if pipe has passed the bird, need to draw another pipe
                    pipe.passed = True
                    add_pipe = True
                    score += 1
            if pipe.x + PIPE_IMG.get_width() <= 0:
                # if the pipe has moved off the screen need to remove the pipe
                pipes_to_remove.append(pipe)
            pipe.move()
        if add_pipe:
            # if we need to add a pipe, create one and add it to the pipes list
            new_pipe = Pipe(WIN_WIDTH)
            pipes.append(new_pipe)
        for pipe in pipes_to_remove:
            # remove the pipes that have passed and moved off screen
            pipes.remove(pipe)
        # check if each bird has hit the ground
        if base.collision(bird):
            run = False
            print("bird has collided! Your score was {}".format(score))
        draw_window(win, base, bird, pipes, score)


if __name__ == "__main__":
    main()
