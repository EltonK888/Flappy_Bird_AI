import os
import random
import time
import neat
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



def draw_window(window, base, birds, pipes, score):
    '''Draws the assets onto the game window'''
    window.blit(BACKGROUND_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(window)
    text = FONT.render(str(score), 1, (255,255,255))
    window.blit(text, (WIN_WIDTH-10-text.get_width(), 10))
    base.draw(window)
    for bird in birds:
        bird.draw(window)
    pygame.display.update()


def main(genomes, config):

    # lists for the neural networks
    birds = []
    networks = []
    ge = []

    for _, g in genomes:
        # create the lists
        networks.append(neat.nn.FeedForwardNetwork.create(g, config))
        birds.append(Bird(WIN_WIDTH/2-25, WIN_HEIGHT/2-100))
        g.fitness = 0
        ge.append(g)

    # set up game assets
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
        base.move()
        # figure out which pipe the neural network should look at when evaluating to jump
        pipe_index = 0 if not pipes[0].passed else 1
        for x, bird in enumerate(birds):
            # determine the output using the following inputs
            # the bird's y position, distance between the bird and the top pipe in the y axis, distance between the bird and the bottom pipe
            # uses the tanh activation function to determine the output
            output = networks[x].activate((bird.y, abs(bird.y-pipes[pipe_index].height), abs(bird.y-pipes[pipe_index].bottom)))
            bird.move()
            ge[x].fitness += 0.1
            # determine if the bird should jump
            if output[0] > 0.5:
                bird.jump()
        add_pipe = False
        pipes_to_remove = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                # for every bird, check if it has collided with a pipe
                if pipe.collision(bird):
                    # if the bird collides, then remove it and its associated
                    # data from all the lists
                    ge[i].fitness -= 1
                    birds.pop(i)
                    networks.pop(i)
                    ge.pop(i)
                if pipe.x + PIPE_IMG.get_width() < bird.x and not pipe.passed:
                    if bird.y < 0:
                        # case where the bird flies up off the game screen and passes a pipe,
                        # it should collide
                        bird.pop(i)
                        ge.pop(i)
                        networks.pop(i)
                    else:
                        # if pipe has passed the bird, need to draw another pipe
                        # add one to the score
                        pipe.passed = True
                        add_pipe = True
                        score += 1
            if pipe.x + PIPE_IMG.get_width() <= 0:
                # if the pipe has moved off the screen need to remove the pipe
                pipes_to_remove.append(pipe)
            pipe.move()
        if add_pipe:
            # create a new pipe if the birds have passed one
            for g in ge:
                # increase the fitness
                g.fitness += 5
            new_pipe = Pipe(WIN_WIDTH)
            pipes.append(new_pipe)
        for pipe in pipes_to_remove:
            # remove pipes that have gone off the screen
            pipes.remove(pipe)
        for i, bird in enumerate(birds):
            # check if each bird has hit the ground. Remove if they have
            if base.collision(bird):
                birds.pop(i)
                ge.pop(i)
                networks.pop(i)
        draw_window(win, base, birds, pipes, score)
        if len(birds) == 0:
            # if we have no more birds, then move onto the next generation
            run = False


def run(config_file):
    '''Sets up the population and the number of generations to run
    the game for.
    '''
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)

    # create population
    pop = neat.population.Population(config)
    
    # statistics report
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.Checkpointer(5))

    # run for 30 generations
    winner = pop.run(main, 30)



if __name__ == "__main__":
    path = os.path.realpath(__file__)
    dirname = os.path.dirname(path)
    config_file = os.path.join(dirname, 'config-neat.txt')
    run(config_file)
