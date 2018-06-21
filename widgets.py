import sys
import math
import pygame
import random

pygame.init()

# boundaries
SCREEN_WIDTH, SCREEN_HEIGHT = 750, 500
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT
FLOOR_HEIGHT = 470

# physics constants
SPEED_DEFAULT = 0.2  # 0.2
SPEED_SIZE_DEFAULT = 10000.0  # Makes speed vary depending upon the particle's size
MAGNITUDE_DEFAULT = 0.002  # 0.002
DRAG_DEFAULT = 0.9995  # 0.999
ELASTICITY_DEFAULT = 0.75  # 0.75
MASS_AIR_DEFAULT = 0.2  # 0.2

# forces
THRUST_SPEED_DEFAULT = 0.07  # 7.0

screen = pygame.display.set_mode(SCREEN_SIZE)

# colors
COLOR_BLACK = 0, 0, 0
COLOR_GRAY_19 = 31, 31, 31
COLOR_GRAY_21 = 54, 54, 54
COLOR_GRAY_41 = 105, 105, 105
COLOR_ORANGE = 251, 126, 20

# fonts
FONT_ORB_DEFAULT = pygame.font.Font('data/fonts/r_fallouty.ttf', 15)
FONT_PAUSE = pygame.font.Font('data/fonts/r_fallouty.ttf', 25)
FONT_PAIR_LEFT = pygame.font.Font('data/fonts/r_fallouty.ttf', 40)

# particle dimensions
WIDTH_PAIR_DEFAULT = 60
WIDTH_PARTICLE_DEFAULT = 15


class Environment:
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, floor_height=FLOOR_HEIGHT):
        self.reset(width, height, floor_height)

    def reset(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, floor_height=FLOOR_HEIGHT):
        self.screen_width = width
        self.screen_height = height
        self.screen_size = self.screen_width, self.screen_height

        self.floor_height = floor_height

        # list to contain all particles (including individual ones inside of particle pairs):
        self.particles_master = []
        # list to contain pairs
        self.particles_pairs = []

        # dictionary to contain preparations for adding pairs into the world
        self.particles_pairs_prep = {
            "color": [],
            "size": [],
            "mass": [],
            "strength": []}

        # amount of pairs desired to spawn
        self.pair_amount = 5

        # tracks what pair the player is in control of
        self.pair_player = 0


        # indicator of the remaining pairs you can spawn
        self.indicator_pair_remaining = self.pair_amount - 1

        # pause
        self.paused = False

        self.thrust_direction = 0

        # define where particles_pairs will spawn to
        self.spawner_x = int(SCREEN_WIDTH / 2) - 100
        self.spawner_y = FLOOR_HEIGHT - 70

    def game(self):
        pygame.display.set_caption('Stand As You Are Able')

        # create list of particle pairs with matching orb colors todo: add file loading feature
        self.particles_pairs_prep = self.pair_creation(p_amount=self.pair_amount)

        # create the starter orb
        orb_starter = self.orb_creation()

        # # create particle pairs:
        # pair_1 = self.Pair(p_width=20, pp_x=int(SCREEN_WIDTH / 2) - 60, pp_mass=1000, pp_strength=1)
        # pair_2 = self.Pair(pp_x=int(SCREEN_WIDTH / 2) + 90, pp_mass=100000, pp_strength=1)
        #
        # # append particle pairs to particle pair list
        # self.particles_pairs.append(pair_1)
        # self.particles_pairs.append(pair_2)
        #
        # # append paired particles to master list
        # for pair_increment in range(len(self.particles_pairs)):
        #     self.particles_master.append(self.particles_pairs[pair_increment].orb1)
        #     self.particles_master.append(self.particles_pairs[pair_increment].orb2)

        # random background circle test (creates more particles)
        # loop to create and append particles
        for i in range(3):
            size = random.randint(5, 10)  # (10, 20)
            density = random.randint(15, 20)  # (1, 20)
            x = random.randint(size, SCREEN_WIDTH - size)
            y = random.randint(size, int(SCREEN_HEIGHT / 2) - size)
            self.particles_master.append(Particle(x=x, y=y, p_size=size, p_color=COLOR_GRAY_41, p_mass=density * size ** 2))

        # append the starter orb to master list
        self.particles_master.append(orb_starter)

        # add the first pair
        self.pair_activation()

        # links the keyboard input with the relevant function
        key_to_function = {
            pygame.K_LEFT:      (lambda thing: thing.set_thrust_direction(-1)),
            pygame.K_UP:        (lambda thing: thing.set_thrust_direction(-1)),
            pygame.K_RIGHT:     (lambda thing: thing.set_thrust_direction(1)),
            pygame.K_DOWN:      (lambda thing: thing.set_thrust_direction(1))
        }

        # update the simulation until the user exits
        while 1:
            # loop over event list to detect quitting
            for event in pygame.event.get():
                # exit the program
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    # print("event.key (DOWN): ", event.key)
                    if event.key in key_to_function:
                        key_to_function[event.key](self)
                    # pause the game
                    elif event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                    # spawn new pair
                    elif event.key == pygame.K_SPACE:
                        if self.pair_player + 1 < self.pair_amount:
                            self.pair_activation()
                            # increase pair_player
                            self.pair_player += 1
                            # decrease indicator_pair_remaining
                            self.indicator_pair_remaining -= 1
                    elif event.key == pygame.K_F10:
                        self.reset()
                        self.game()
                elif event.type == pygame.KEYUP:
                    self.thrust_direction = 0
                # elif event.type == pygame.KEYUP:
                #     # print("event.key (UP):   ", event.key)
                #     if pygame.K_UP == event.key or pygame.K_LEFT == event.key:
                #         self.thrust(engage=False)
                #     elif pygame.K_DOWN == event.key or pygame.K_RIGHT == event.key:
                #         self.thrust(engage=False)
            # screen fill (removes blur)
            screen.fill(COLOR_BLACK)
            self.update()
            pygame.display.update()

    # return a list specifying starter orb and particle pair color, size, mass, and strength based upon the parameters.
    def pair_creation(self, p_amount=3, p_list_color=[], p_list_size=[], p_list_density=[], p_list_mass=[],
                      p_list_strength=[]):
        """

        :param p_amount: amount of colors to share amongst all orbs. (the number of pairs is 1 less than this)
        :param p_list_color: list of colors for the starting orb and each orb among pairs. Default randomizes colors.
        :param p_list_size: list of sizes for the starting orb and each pair. Default randomizes sizes.
        :param p_list_density: list of densities to calculate the starting orb's and each pair's masses.
        :param p_list_mass: list of masses for the starting orb and each pair. Default randomizes masses.
        :param p_list_strength: list of strengths for each pair. Default gives default strengths.
        :return: return a list of particle pairs based upon the parameters.
        """

        # fill lists with ranged random values until their sizes meet the specified amount.
        # list of colors must meet the specified amount.
        while len(p_list_color) < p_amount:
            p_list_color.append(rand_color())
        # list of sizes must meet the specified amount.
        while len(p_list_size) < p_amount:
            p_list_size.append(random.randint(10, 15))
        # list of densities must meet the specified amount.
        while len(p_list_density) < p_amount:
            p_list_density.append(random.randint(15, 20))
        # list of masses must meet the specified amount.
        while len(p_list_mass) < p_amount:
            p_list_mass.append(p_list_density[len(p_list_mass)] * p_list_size[len(p_list_mass)] ** 2)
        # list of strengths must be 1 less than the specified amount (as it only affects pairs)
        while len(p_list_strength) + 1 < p_amount:
            p_list_strength.append(0.5)

        # create a particle pair dictionary
        # Note that density is absent, as it is dropped after calculating mass.
        pair_dict = {
            "color": p_list_color,
            "size": p_list_size,
            "mass": p_list_mass,
            "strength": p_list_strength}

        # return the list of pairs
        return pair_dict

    def orb_creation(self, p_x=int(SCREEN_WIDTH / 2), p_y=FLOOR_HEIGHT):
        """

        :param p_x: x placement for starter orb. Defaults to the center of the screen.
        :param p_y: y placement for the starter orb. Defaults to merge with the floor.
        :return returns the starter orb.
        """
        # create starter orb
        orb_starter = Particle(x=p_x, y=p_y, static=True, p_color=self.particles_pairs_prep["color"][0],
                               p_size=self.particles_pairs_prep["size"][0], p_mass=self.particles_pairs_prep["mass"][0])
        return orb_starter

    # places the next pair in particles_pairs into the world and iterates pair_player to reflect this
    def pair_activation(self):
        # iterates pair_player. Once it is larger than the size of the list, return false.

        # append pairs to particles_pairs list
        self.particles_pairs.append(self.Pair(pp_x=self.spawner_x, pp_y=self.spawner_y,
                                               pp_color_1=self.particles_pairs_prep["color"][self.pair_player],
                                               pp_color_2=self.particles_pairs_prep["color"][self.pair_player+1],
                                               p_width=self.particles_pairs_prep["size"][self.pair_player],
                                               pp_mass=self.particles_pairs_prep["mass"][self.pair_player],
                                               pp_strength=self.particles_pairs_prep["strength"][self.pair_player]))
        # append paired particles to master list
        self.particles_master.append(self.particles_pairs[len(self.particles_pairs)-1].orb1)
        self.particles_master.append(self.particles_pairs[len(self.particles_pairs)-1].orb2)

    def set_thrust_direction(self, direction):
        self.thrust_direction = direction

    def thrust(self):
        if self.thrust_direction is not 0 and self.particles_pairs:
            print("thrust:  ", self.thrust_direction)
            self.particles_pairs[self.pair_player].thrust(self.thrust_direction)

    # particle movement
    def update(self):
        for j, spring in enumerate(self.particles_pairs):
            spring.display()
            spring.update()
        for i, particle in enumerate(self.particles_master):
            if not self.paused:
                particle.move()
                particle.bounce()
                for particle2 in self.particles_master[i + 1:]:
                    collide(particle, particle2)
                self.thrust()
            else:
                # pause screen text
                screen.blit(FONT_PAUSE.render("PAUSED", False, COLOR_ORANGE),
                            ((self.screen_width / 2) * 0.99 - 20, (self.screen_height / 2) * 0.97))
            # counter text (displays how many pairs you have left)
            screen.blit(FONT_PAIR_LEFT.render(str(self.indicator_pair_remaining), False, COLOR_ORANGE),
                        ((self.screen_width * 0.9) * 0.99 - 20, (self.screen_height / 8) * 0.97))
            particle.display()

    class Pair:
        def __init__(self, p_width=WIDTH_PARTICLE_DEFAULT, pp_x=int(SCREEN_WIDTH / 2), pp_y=FLOOR_HEIGHT,
                     pp_length=WIDTH_PAIR_DEFAULT, pp_color_1=None, pp_color_2=None, pp_mass=1, pp_strength=0.5):
            # apply colors to orbs
            if pp_color_1 is None and pp_color_2 is None:
                pp_color_1 = rand_color()
                pp_color_2 = pp_color_1
            if pp_color_1 is None:
                pp_color_1 = rand_color()
            if pp_color_2 is None:
                pp_color_2 = rand_color()
            # adjust floor placement based on width
            self.orb_pair = []
            pp_y -= p_width
            self.orb1 = Particle(pp_x, pp_y, p_color=pp_color_1, p_size=p_width, p_mass=pp_mass)
            self.orb2 = Particle(pp_x + pp_length, pp_y, p_color=pp_color_2, p_size=p_width, p_mass=pp_mass)
            self.orb_pair.append(self.orb1)
            self.orb_pair.append(self.orb2)
            # spring variables
            self.length = pp_length
            self.strength = pp_strength

        def display(self):
            pygame.draw.aaline(screen, COLOR_GRAY_21, (int(self.orb1.x), int(self.orb1.y)),
                                   (int(self.orb2.x), int(self.orb2.y)))

        def thrust(self, amount):
            # set what orb is to the left and which one is on the right
            if self.orb1.x <= self.orb2.x:
                orb_left = 0
                orb_right = 1
            else:
                orb_left = 1
                orb_right = 0
            dx = self.orb1.x - self.orb2.x
            dy = self.orb1.y - self.orb2.y
            theta = math.atan2(dy, dx)  # - 0.5 * math.pi
            # if amount is negative, move left
            if amount is -1:
                # todo: calculate the angle at which the thrust should be applied
                theta = theta + 0.5 * math.pi
                # apply thrust to orb_left
                print("left orb theta:  ", theta)
                self.orb_pair[orb_left].accelerate(theta, THRUST_SPEED_DEFAULT)
            # if amount is positive, move right
            else:
                # todo: calculate the angle at which the thrust should be applied
                theta = -theta - 0.5 * math.pi
                # apply thrust to orb_right
                print("right orb theta:  ", theta)
                self.orb_pair[orb_right].accelerate(theta, THRUST_SPEED_DEFAULT)

        # update the spring constraints
        def update(self):
            dx = self.orb1.x - self.orb2.x
            dy = self.orb1.y - self.orb2.y
            dist = math.hypot(dx, dy)
            theta = math.atan2(dy, dx)
            force = (self.length - dist) * self.strength

            self.orb1.accelerate(theta + 0.5 * math.pi, force/self.orb1.mass)
            self.orb2.accelerate(theta - 0.5 * math.pi, force/self.orb2.mass)


class Particle:
    def __init__(self, x, y, static=False, p_size=WIDTH_PARTICLE_DEFAULT, p_color=COLOR_ORANGE, p_thickness=1, p_angle=(math.pi / 2),
                 p_speed=SPEED_DEFAULT, p_mass=1, p_text=None):
        self.x, self.y = x, y
        self.static = static
        self.size = p_size
        self.speed = p_speed
        self.angle = p_angle
        self.mass = p_mass
        self.drag = (self.mass/(self.mass + MASS_AIR_DEFAULT)) ** self.size
        if p_text is None:
            self.text = str(self.mass)  # self.angle)
        else:
            self.text = p_text
        self.color = p_color
        self.thickness = p_thickness

    def accelerate(self, a_angle, a_length):
        (self.angle, self.speed) = add_vectors(self.angle, self.speed, a_angle, a_length)

    def bounce(self):
        if not self.static:
            if self.x > SCREEN_WIDTH - self.size:
                self.x = 2 * (SCREEN_WIDTH - self.size) - self.x
                self.angle = - self.angle
                self.speed *= ELASTICITY_DEFAULT

            elif self.x < self.size:
                self.x = 2 * self.size - self.x
                self.angle = - self.angle
                self.speed *= ELASTICITY_DEFAULT

            if self.y > FLOOR_HEIGHT - self.size:
                self.y = 2 * (FLOOR_HEIGHT - self.size) - self.y
                self.angle = math.pi - self.angle
                self.speed *= ELASTICITY_DEFAULT

            elif self.y < self.size:
                self.y = 2 * self.size - self.y
                self.angle = math.pi - self.angle
                self.speed *= ELASTICITY_DEFAULT

    def display(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size, self.thickness)
        # display angle
        # self.text = str(round(self.angle))
        # display mass
        screen.blit(FONT_ORB_DEFAULT.render(self.text, False, COLOR_ORANGE), (self.x * 0.99, self.y * 0.97))

    def move(self):
        if not self.static:
            self.x += math.sin(self.angle) * self.speed
            self.y -= math.cos(self.angle) * self.speed
            (self.angle, self.speed) = add_vectors(self.angle, self.speed, math.pi, MAGNITUDE_DEFAULT)
            self.speed *= self.drag
            self.speed *= (1 - self.size / SPEED_SIZE_DEFAULT)


def add_vectors(angle1, length1, angle2, length2):
    x = math.sin(angle1) * length1 + math.sin(angle2) * length2
    y = math.cos(angle1) * length1 + math.cos(angle2) * length2
    length = math.hypot(x, y)
    angle = 0.5 * math.pi - math.atan2(y, x)
    return [angle, length]


def collide(p1, p2):
    dx = p1.x - p2.x
    dy = p1.y - p2.y

    distance = math.hypot(dx, dy)
    if distance < p1.size + p2.size:
        total_mass = p1.mass + p2.mass
        # angle = 0.5 * math.pi + tangent
        # tangent = math.atan2(dx, dy)
        # p1.angle = 2 * tangent - p1.angle
        # p2.angle = 2 * tangent - p2.angle
        angle = math.atan2(dy, dx) + 0.5 * math.pi
        # (p1.speed, p2.speed) = (p2.speed, p1.speed)
        (p1.angle, p1.speed) = add_vectors(p1.angle, p1.speed * (p1.mass - p2.mass) / total_mass,
                                           angle, 2 * p2.speed * p2.mass / total_mass)
        (p2.angle, p2.speed) = add_vectors(p2.angle, p2.speed * (p2.mass - p1.mass) / total_mass,
                                           angle + math.pi, 2 * p1.speed * p1.mass / total_mass)
        p1.speed *= ELASTICITY_DEFAULT
        p2.speed *= ELASTICITY_DEFAULT
        overlap = 0.5 * (p1.size + p2.size - distance + 1)
        # p1.x += math.sin(angle)
        p1.x += math.sin(angle) * overlap
        # p1.y -= math.cos(angle)
        p1.y -= math.cos(angle) * overlap
        # p2.x -= math.sin(angle)
        p2.x -= math.sin(angle) * overlap
        # p2.y += math.cos(angle)
        p2.y += math.cos(angle) * overlap


def rand_color():
    color = []
    for x in range(3):
        color.append(random.randint(0, 255))
    return color


# adapted from https://stackoverflow.com/questions/20842801/how-to-display-text-in-pygame
def text_to_screen(text, x, y, size=50,
                   color=COLOR_ORANGE, font_type='data/fonts/r_fallouty.ttf'):
    try:

        text = str(text)
        font = pygame.font.Font(font_type, size)
        text = font.render(text, True, color)
        screen.blit(text, (x, y))

    except Exception as e:
        print('Font Error')
        raise e
