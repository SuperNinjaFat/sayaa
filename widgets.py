import sys
import math
import pygame
import random

pygame.init()
# pygame.font.init()

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

        # pause
        self.paused = False

    def game(self):
        pygame.display.set_caption('Stand As You Are Able')

        # create particle pairs:
        pair_1 = self.Pair(p_width=20, pp_x=int(SCREEN_WIDTH / 2) - 60, pp_mass=100000)
        pair_2 = self.Pair(pp_x=int(SCREEN_WIDTH / 2) + 90, pp_mass=100000)

        # append particle pairs to particle pair list
        self.particles_pairs.append(pair_1)
        self.particles_pairs.append(pair_2)

        # append paired particles to master list
        for pair_increment in range(len(self.particles_pairs)):
            self.particles_master.append(self.particles_pairs[pair_increment].dump()[0])
            self.particles_master.append(self.particles_pairs[pair_increment].dump()[1])

        # random background circle test (creates more particles)
        # loop to create and append particles
        for i in range(10):
            size = random.randint(5, 10)  # (10, 20)
            density = random.randint(15, 20)  # (1, 20)
            x = random.randint(size, SCREEN_WIDTH - size)
            y = random.randint(size, int(SCREEN_HEIGHT / 2) - size)
            self.particles_master.append(Particle(x=x, y=y, p_size=size, p_color=COLOR_GRAY_41, p_mass=density * size ** 2))

        # links the keyboard input with the relevant function
        key_to_function = {
            pygame.K_LEFT:      (lambda thing: thing.thrust(1)),
            pygame.K_UP:        (lambda thing: thing.thrust(1)),
            pygame.K_RIGHT:     (lambda thing: thing.thrust(-1)),
            pygame.K_DOWN:      (lambda thing: thing.thrust(-1))
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
                    elif event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_F10:
                        self.reset()
                        self.game()
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

    def thrust(self, amount=None, engage=True):
        print("thrust:  ", amount)
        print("engaged: ", engage)

    # particle movement
    def update(self):
        for i, particle in enumerate(self.particles_master):
            if not self.paused:
                particle.move()
                particle.bounce()
                for particle2 in self.particles_master[i + 1:]:
                    collide(particle, particle2)
            else:
                screen.blit(FONT_PAUSE.render("PAUSED", False, COLOR_ORANGE), ((self.screen_width / 2) * 0.99 - 20, (self.screen_height / 2) * 0.97))
            particle.display()

    class Pair:
        # TODO: Create a bar between the orbs
        def __init__(self, p_width=WIDTH_PARTICLE_DEFAULT, pp_x=int(SCREEN_WIDTH / 2), pp_y=FLOOR_HEIGHT,
                     pp_width=WIDTH_PAIR_DEFAULT, pp_color=None, pp_mass=1):
            if pp_color is None:
                pp_color = rand_color()
            # adjust floor placement based on width
            self.orb_pair = []
            pp_y -= p_width
            self.orb1 = Particle(pp_x, pp_y, p_color=pp_color, p_size=p_width, p_mass=pp_mass)
            self.orb2 = Particle(pp_x + pp_width, pp_y, p_color=pp_color, p_size=p_width, p_mass=pp_mass)
            self.orb_pair.append(self.orb1)
            self.orb_pair.append(self.orb2)

        def dump(self):
            return self.orb_pair


class Particle:
    def __init__(self, x, y, p_size=WIDTH_PARTICLE_DEFAULT, p_color=COLOR_ORANGE, p_thickness=1, p_angle=(math.pi / 2),
                 p_speed=SPEED_DEFAULT, p_mass=1, p_text=None):
        self.x, self.y = x, y
        self.size = p_size
        self.speed = p_speed
        self.angle = p_angle
        self.mass = p_mass
        self.drag = (self.mass/(self.mass + MASS_AIR_DEFAULT)) ** self.size
        if p_text is None:
            self.text = str(self.mass)
        else:
            self.text = p_text
        self.color = p_color
        self.thickness = p_thickness

    def bounce(self):
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
        # text movement
        # display mass
        # text_to_screen(self.mass, self.x * 0.99, self.y * 0.97, size=20)
        screen.blit(FONT_ORB_DEFAULT.render(self.text, False, COLOR_ORANGE), (self.x * 0.99, self.y * 0.97))

    def move(self):
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
