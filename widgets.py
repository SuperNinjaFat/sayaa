import math
import pygame
import random
from tkinter import *

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 750, 500
FLOOR_HEIGHT = 470
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT
SPEED_DEFAULT = 0.2  # 0.2
SPEED_SIZE_DEFAULT = 10000.0  # Makes speed vary depending upon the particle's size
MAGNITUDE_DEFAULT = 0.002  # 0.002
DRAG_DEFAULT = 0.9995  # 0.999
ELASTICITY_DEFAULT = 0.75  # 0.75
screen = pygame.display.set_mode(SCREEN_SIZE)

COLOR_BLACK = 0, 0, 0
COLOR_GRAY_19 = 31, 31, 31
COLOR_GRAY_21 = 54, 54, 54
COLOR_GRAY_41 = 105, 105, 105
COLOR_ORANGE = 251, 126, 20

WIDTH_PAIR_DEFAULT = 60
WIDTH_PARTICLE_DEFAULT = 15


def rand_color():
    color = []
    for x in range(3):
        color.append(random.randint(0, 255))
    return color


class Application(Frame):
    def __init__(self, master=None):
        self.master = master
        Frame.__init__(self, self.master)

        pi_title_pre = PhotoImage(file="sayaa_title.gif")
        self.pi_title = Label(self, image=pi_title_pre)
        self.pi_title.image = pi_title_pre
        self.b_start = Button(self.master, text="START", command=self.game, font=('Fallouty', 12))
        self.b_exit = Button(self.master, text="EXIT", command=self.escape, font=('Fallouty', 12))
        self.widgets_bind()

    def escape(self, event=None):
        self.quit()

    def game(self, event=None):
        pygame.display.set_caption('Stand As You Are Able')

        # list to contain all particles (including individual ones inside of particle pairs):
        particles_master = []

        # list to contain
        particles_pairs = []

        # create particle pairs:
        # pair_1 = self.Pair(p_width=20, pp_x=int(SCREEN_WIDTH / 2) - 60)
        pair_2 = self.Pair(pp_x=int(SCREEN_WIDTH / 2) + 90)

        # append particle pairs to particle pair list
        # particles_pairs.append(pair_1)
        particles_pairs.append(pair_2)

        # append paired particles to master list
        for pair_increment in range(len(particles_pairs)):
            particles_master.append(particles_pairs[pair_increment].dump()[0])
            particles_master.append(particles_pairs[pair_increment].dump()[1])

        # random background circle test (creates more particles)
        # loop to create and append particles
        for i in range(20):
            size = random.randint(10, 20)
            density = random.randint(1, 20)
            x = random.randint(size, SCREEN_WIDTH - size)
            y = random.randint(size, int(SCREEN_HEIGHT / 2) - size)
            particles_master.append(Particle(x=x, y=y, p_size=size, p_color=COLOR_GRAY_41, p_mass=density * size ** 2))

        # update the simulation until the user exits
        while 1:
            # loop over event list to detect quitting
            for event in pygame.event.get():
                # exit the program
                if event.type == pygame.QUIT:
                    sys.exit()
            # screen fill (removes blur)
            screen.fill(COLOR_BLACK)
            # particle movement
            for i, particle in enumerate(particles_master):
                particle.move()
                particle.bounce()
                for particle2 in particles_master[i + 1:]:
                    collide(particle, particle2)
                particle.display()
            pygame.display.update()

    class Pair:
        # TODO: Create a bar between the orbs
        def __init__(self, p_width=WIDTH_PARTICLE_DEFAULT, pp_x=int(SCREEN_WIDTH / 2), pp_y=FLOOR_HEIGHT,
                     pp_width=WIDTH_PAIR_DEFAULT, pp_color=None):
            if pp_color is None:
                pp_color = rand_color()
            # adjust floor placement based on width
            self.orb_pair = []
            pp_y -= p_width
            self.orb1 = Particle(pp_x, pp_y, p_color=pp_color, p_size=p_width)
            self.orb2 = Particle(pp_x + pp_width, pp_y, p_color=pp_color, p_size=p_width)
            self.orb_pair.append(self.orb1)
            self.orb_pair.append(self.orb2)

        def dump(self):
            return self.orb_pair

    def widgets_bind(self):
        self.pi_title.grid(row=0, column=0, columnspan=2, sticky=NW)
        self.b_start.grid(row=1, column=0, sticky=W)
        self.b_start.bind_all('<Return>', self.game)
        self.b_exit.grid(row=1, column=1, sticky=E)
        self.b_exit.bind_all('<BackSpace>', self.escape)


class Particle:
    def __init__(self, x, y, p_size=WIDTH_PARTICLE_DEFAULT, p_color=COLOR_ORANGE, p_thickness=1, p_angle=(math.pi / 2),
                 p_speed=SPEED_DEFAULT, p_mass=1):
        self.x, self.y = x, y
        self.size = p_size
        self.color = p_color
        self.thickness = p_thickness
        self.speed = p_speed
        self.angle = p_angle
        self.mass = p_mass

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

    def move(self):
        self.x += math.sin(self.angle) * self.speed
        self.y -= math.cos(self.angle) * self.speed
        (self.angle, self.speed) = addVectors(self.angle, self.speed, math.pi, MAGNITUDE_DEFAULT)
        self.speed *= DRAG_DEFAULT
        self.speed *= (1 - self.size / SPEED_SIZE_DEFAULT)


def addVectors(angle1, length1, angle2, length2):
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
        (p1.angle, p1.speed) = addVectors(p1.angle, p1.speed*(p1.mass-p2.mass)/total_mass,
                                          angle, 2*p2.speed*p2.mass/total_mass)
        (p2.angle, p2.speed) = addVectors(p2.angle, p2.speed*(p2.mass-p1.mass)/total_mass,
                                          angle+math.pi, 2*p1.speed*p1.mass/total_mass)
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


