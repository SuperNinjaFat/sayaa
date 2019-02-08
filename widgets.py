import sys
import math
import pygame
import random

pygame.init()

# boundaries
SCREEN_WIDTH, SCREEN_HEIGHT = 750, 500  # 750, 500
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT
FLOOR_HEIGHT = SCREEN_HEIGHT - 45

# physics constants
SPEED_DEFAULT = 0.2  # 0.2
SPEED_SIZE_DEFAULT = 10000.0  # 10000.0 Makes speed vary depending upon the particle's size
MAGNITUDE_DEFAULT = 0.002  # 0.002
DRAG_DEFAULT = 0.9995  # 0.999
ELASTICITY_DEFAULT = 0.75  # 0.75
MASS_AIR_DEFAULT = 0.2  # 0.2

# forces
THRUST_SPEED_DEFAULT = 0.001  # 0.001

screen = pygame.display.set_mode(SCREEN_SIZE)

# colors
COLOR_BLACK = 0, 0, 0
COLOR_GRAY_19 = 31, 31, 31
COLOR_GRAY_21 = 54, 54, 54
COLOR_GRAY_41 = 105, 105, 105
COLOR_ORANGE = 251, 126, 20
COLOR_LAVENDER = 230, 230, 250

# animated colors
COLOR_LAVENDER_ANIM = [
    [230, 230, 250],
    [213, 213, 241],
    [195, 195, 222],
    [165, 165, 189],
    [128, 128, 148],
    [89, 89, 103],
    [53, 53, 60],
    [30, 30, 37],
    [10, 10, 12]]

# fonts
FONT_ORB_DEFAULT = pygame.font.Font('data/fonts/r_fallouty.ttf', 15)
FONT_PAUSE = pygame.font.Font('data/fonts/r_fallouty.ttf', 25)
FONT_TITLE = pygame.font.Font('data/fonts/r_fallouty.ttf', 50)
FONT_PAIR_LEFT = pygame.font.Font('data/fonts/r_fallouty.ttf', 40)

# sound effects
SOUND_STICK = [pygame.mixer.Sound('data/sound/airboat_gun_lastshot1.wav'),
               pygame.mixer.Sound('data/sound/airboat_gun_lastshot2.wav')]
SOUND_UNSTICK = pygame.mixer.Sound('data/sound/rmine_chirp_answer1.wav')
SOUND_PAUSE = pygame.mixer.Sound('data/sound/MenuBack.wav')
SOUND_RELOAD = pygame.mixer.Sound('data/sound/LegoDebris2.wav')
SOUND_THRUST = pygame.mixer.Sound('data/sound/suit_sprint.wav')

# particle dimensions
WIDTH_PAIR_DEFAULT = 60  # 60
WIDTH_PARTICLE_DEFAULT = 15  # 15

# effect dimensions
WIDTH_EFFECT_DEFAULT = 1  # 1
EFFECT_RATE_DEFAULT = 2  # 2

# sticky constants
RESTICK_TIME_DEFAULT = 80  # 80


# adapted from https://pythonprogramming.net/pygame-button-function/?completed=/placing-text-pygame-buttons/
def button(msg,x,y,w,h,ic,ac,action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    print(click)
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(screen, ac,(x,y,w,h))

        if click[0] == 1 and action != None:
            action()
    else:
        pygame.draw.rect(screen, ic,(x,y,w,h))

    textSurf, textRect = text_objects(msg, FONT_ORB_DEFAULT)
    textRect.center = ( (x+(w/2)), (y+(h/2)) )
    screen.blit(textSurf, textRect)


# adapted from https://pythonprogramming.net/pygame-start-menu-tutorial/
def text_objects(text, font):
    textSurface = font.render(text, True, COLOR_BLACK)
    return textSurface, textSurface.get_rect()


# adapted from https://pythonprogramming.net/pygame-start-menu-tutorial/
def message_display(text):
    TextSurf, TextRect = text.text_objects(text, FONT_PAUSE)
    TextRect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 2))
    screen.blit(TextSurf, TextRect)

    pygame.display.update()

    # time.sleep(2)


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
        # list to contain all effects
        self.effects_master = []
        # list to contain all boundaries
        self.boundaries_master = []

        # amount of pairs desired to spawn
        self.pair_amount = 7

        # dictionary to contain preparations for adding pairs into the world
        self.particles_pairs_prep = {}

        # tracks what pair the player is in control of
        self.pair_player = 0


        # indicator of the remaining pairs you can spawn
        self.indicator_pair_remaining = self.pair_amount - 1

        # pause
        self.paused = False

        self.thrust_direction = 0

        self.lift_direction = 0

        # define where particles_pairs will spawn to
        self.spawner_x = int(SCREEN_WIDTH / 2) - 300
        self.spawner_y = FLOOR_HEIGHT - 70

    def game(self):
        pygame.display.set_caption('Stand As You Are Able')

        # create list of particle pairs with matching orb colors todo: add file loading feature
        list_color = []
        list_size = []
        list_density = []
        list_mass = []
        list_strength = []
        self.particles_pairs_prep = self.pair_creation(p_amount=self.pair_amount,
                                                       p_list_color=list_color,
                                                       p_list_size=list_size,
                                                       p_list_density=list_density,
                                                       p_list_mass=list_mass,
                                                       p_list_strength=list_strength)

        # create the starter orb
        orb_starter = self.orb_creation(sticky=True)

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
        for i in range(0):
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
            pygame.K_LEFT:      (lambda thing: thing.set_thrust_direction(1)),
            pygame.K_DOWN:      (lambda thing: thing.set_lift_direction(1)),
            pygame.K_RIGHT:     (lambda thing: thing.set_thrust_direction(-1)),
            pygame.K_UP:        (lambda thing: thing.set_lift_direction(-1))
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
                        play_sfx(SOUND_THRUST)
                    # pause the game
                    elif event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                        play_sfx(SOUND_PAUSE)
                    # spawn new pair
                    elif event.key == pygame.K_SPACE and (self.pair_player + 1 < self.pair_amount)\
                        and self.particles_pairs[self.pair_player].orb1.static and not self.paused:
                        self.particles_pairs[self.pair_player].orb2.static = True
                        self.particles_pairs[self.pair_player].orb2.sticky = True
                        # increase pair_player
                        self.pair_player += 1
                        self.pair_activation()
                        # decrease indicator_pair_remaining
                        self.indicator_pair_remaining -= 1
                        # create effects
                        self.effects_master.append(Effect((self.screen_width * 0.9) * 0.99 - 10,
                                                          (self.screen_height / 8) * 0.97 + 28,
                                                          e_color_anim=COLOR_LAVENDER_ANIM))
                        self.effects_master.append(Effect(self.particles_pairs[self.pair_player].orb2.x,
                                                          self.particles_pairs[self.pair_player].orb2.y,
                                                          e_color_anim=COLOR_LAVENDER_ANIM))
                        # play sound effect
                        play_sfx(SOUND_STICK)
                    elif event.key == pygame.K_F10:
                        play_sfx(SOUND_RELOAD)
                        self.reset()
                        self.game()
                    elif event.key == pygame.K_BACKSPACE:
                        if self.particles_pairs[self.pair_player].orb1.static:
                            self.particles_pairs[self.pair_player].orb1.static = False
                            self.particles_pairs[self.pair_player].orb1.sticky = True
                            self.particles_pairs[self.pair_player].orb1.stuck_to.restick = True
                            self.particles_pairs[self.pair_player].orb1.stuck_to.stuck_to = Particle
                            self.particles_pairs[self.pair_player].orb1.stuck_to = Particle
                            # play sound effect
                            play_sfx(SOUND_UNSTICK)
                elif event.type == pygame.KEYUP:
                    self.thrust_direction, self.lift_direction = 0, 0
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

    def effect_timeout(self):
        for h, effect in enumerate(self.effects_master):
            if effect.timeout():
                self.effects_master.remove(effect)

    # return a list specifying starter orb and particle pair color, size, mass, and strength based upon the parameters.
    def pair_creation(self, p_amount=2, p_list_color=[], p_list_size=[], p_list_density=[], p_list_mass=[],
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
        while len(p_list_color) - 1 < p_amount:
            p_list_color.append(rand_color())
        # list of sizes must meet the specified amount.
        while len(p_list_size) - 1 < p_amount:
            p_list_size.append(random.randint(10, 15))
        # list of densities must meet the specified amount.
        while len(p_list_density) - 1 < p_amount:
            p_list_density.append(random.randint(15, 20))
        # list of masses must meet the specified amount.
        while len(p_list_mass) - 1 < p_amount:
            p_list_mass.append(p_list_density[len(p_list_mass)] * p_list_size[len(p_list_mass)] ** 2)
        # list of strengths must be 1 less than the specified amount (as it only affects pairs)
        while len(p_list_strength) < p_amount:
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

    def orb_creation(self, p_x=int(SCREEN_WIDTH / 2), p_y=FLOOR_HEIGHT, sticky=False):
        """

        :param sticky: Determines whether it can stick to another orb.
        :param p_x: x placement for starter orb. Defaults to the center of the screen.
        :param p_y: y placement for the starter orb. Defaults to merge with the floor.
        :return returns the starter orb.
        """
        # create starter orb
        orb_starter = Particle(x=p_x, y=p_y, static=True, sticky=sticky, p_color=self.particles_pairs_prep["color"][0],
                               p_size=self.particles_pairs_prep["size"][0], p_mass=self.particles_pairs_prep["mass"][0])
        return orb_starter

    # creates ingame boundaries and obstacles
    def boundary_creation(self, b_list_wall):
        boundary_dict = {
            "wall": b_list_wall
        }

        return boundary_dict

    def boundary_activation(self):
        for i, boundary in enumerate(self.boundaries_master):
            boundary
        for w in range(len(self.boundaries_master["wall"])):
            # contains list of coordinates for walls
            for b in range(len(self.boundaries_master["wall"][w])):
                self.boundaries_master["wall"][w][b]

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

    def set_lift_direction(self, direction):
        self.lift_direction = direction

    def set_thrust_direction(self, direction):
        self.thrust_direction = direction

    def lift(self):
        if self.lift_direction is not 0 and self.particles_pairs:
            print("lift:  ", self.lift_direction)
            self.particles_pairs[self.pair_player].lift(self.lift_direction)

    def thrust(self):
        if self.thrust_direction is not 0 and self.particles_pairs:
            print("thrust:  ", self.thrust_direction)
            self.particles_pairs[self.pair_player].thrust(self.thrust_direction)

    # particle movement
    def update(self):
        for j, spring in enumerate(self.particles_pairs):
            spring.display()
            if not self.paused:
                spring.update()
        for i, particle in enumerate(self.particles_master):
            if not self.paused:
                particle.move()
                particle.bounce()
                for particle2 in self.particles_master[i + 1:]:
                    collide(particle, particle2)
                particle.restick_timeout()
                self.thrust()
                self.lift()
            else:
                # pause screen text
                screen.blit(FONT_PAUSE.render("PAUSED", False, COLOR_ORANGE),
                            ((self.screen_width / 2) * 0.99 - 20, (self.screen_height / 2) * 0.97))
            # counter text (displays how many pairs you have left)
            screen.blit(FONT_PAIR_LEFT.render(str(self.indicator_pair_remaining), False, COLOR_ORANGE),
                        ((self.screen_width * 0.9) * 0.99 - 20, (self.screen_height / 8) * 0.97))
            particle.display()
            # draw floor
            pygame.draw.aaline(screen, COLOR_GRAY_21, (0, self.floor_height), (self.screen_width, self.floor_height))
        for h, effect in enumerate(self.effects_master):
            self.effect_timeout()
            effect.display()

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
            self.orb1 = Particle(pp_x, pp_y, sticky=True, p_color=pp_color_1, p_size=p_width, p_mass=pp_mass)
            self.orb2 = Particle(pp_x + pp_length, pp_y, p_color=pp_color_2, p_size=p_width, p_mass=pp_mass)
            self.orb_pair.append(self.orb1)
            self.orb_pair.append(self.orb2)
            # spring variables
            self.length = pp_length
            self.strength = pp_strength

        def display(self):
            pygame.draw.aaline(screen, COLOR_GRAY_21, (int(self.orb1.x), int(self.orb1.y)),
                                   (int(self.orb2.x), int(self.orb2.y)))

        def lift(self, amount):
            # set what orb is to the left and which one is on the right
            if self.orb1.y == self.orb2.y:
                orb_left = 0
                orb_right = 1
            else:
                orb_left = 1
                orb_right = 0
            dx = self.orb1.x - self.orb2.x
            dy = self.orb1.y - self.orb2.y
            theta = 2 * math.atan2(dy, dx)
            # if amount is negative, lift up
            if amount is -1:
                # apply thrust to orb_left
                print("left orb theta:  ", theta)
                self.orb_pair[orb_left].accelerate(theta, THRUST_SPEED_DEFAULT)
            # if amount is positive, lift up
            else:
                # apply thrust to orb_right
                print("right orb theta:  ", theta)
                self.orb_pair[orb_right].accelerate(theta, THRUST_SPEED_DEFAULT)


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
            theta = 2 * math.atan2(dy, dx)
            # if amount is negative, move left
            if amount is -1:
                # apply thrust to orb_left
                print("left orb theta:  ", theta)
                self.orb_pair[orb_left].accelerate(theta, THRUST_SPEED_DEFAULT)
            # if amount is positive, move right
            else:
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

    # used this for reference: https://pythonprogramming.net/pygame-start-menu-tutorial/
    def main_menu(self):
        while 1:
            for event in pygame.event.get():
                print(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            screen.fill(COLOR_LAVENDER)
            TextSurf, TextRect = text_objects("Stand As You Are Able", FONT_TITLE)
            TextRect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 2))
            screen.blit(TextSurf, TextRect)

            button("New Game", 150, 450, 100, 50, COLOR_GRAY_21, COLOR_GRAY_41, self.game)
            button("Quit", 550, 450, 100, 50, COLOR_GRAY_19, COLOR_GRAY_21, quit)

            mouse = pygame.mouse.get_pos()



            pygame.display.update()




class Particle:
    def __init__(self, x, y, static=False, sticky=False, p_size=WIDTH_PARTICLE_DEFAULT, p_color=COLOR_ORANGE, p_thickness=1, p_angle=(math.pi / 2),
                 p_speed=SPEED_DEFAULT, p_mass=1, p_text=None):
        self.x, self.y = x, y
        self.static = static
        # whether the orb color sticks to its matching color
        self.sticky = sticky
        self.restick = False
        self.stuck_to = Particle
        self.restick_time = 0

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

    def restick_timeout(self):
        if self.restick:
            if self.restick_time == RESTICK_TIME_DEFAULT:
                self.sticky, self.restick = True, False
            else:
                self.restick_time += 1

class Effect:
    def __init__(self, x, y, static=True, e_size=WIDTH_EFFECT_DEFAULT, e_color=COLOR_LAVENDER,
                 e_color_anim=[], thickness=1):
        self.x, self.y = x, y
        self.static = static
        self.size = e_size
        self.color = e_color
        self.color_anim = e_color_anim
        self.thickness = thickness

        self.anim_frame = 0
        self.anim_endframe = len(self.color_anim)-1

        self.extend_frame = 0

    def display(self):
        pygame.draw.circle(screen, self.color_anim[int(self.anim_frame)], (int(self.x), int(self.y)), self.size,
                           self.thickness)
        self.size += int(self.extend_frame * 0.02)
        self.extend_frame += 1
        self.anim_frame = int(self.extend_frame * 0.05)

    def timeout(self):
        if self.anim_frame is self.anim_endframe:
            return True
        else:
            return False

class Wall:
    def __init__(self, x1, y1, x2, y2, x3, y3, x4, y4, w_color=COLOR_GRAY_21):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.x3, self.y3 = x3, y3
        self.x4, self.y4 = x4, y4
        self.color = w_color

    def display(self):
        pygame.draw.polygon(screen, self.color, [[int(self.x1), int(self.y1)],
                                                 [int(self.x2), int(self.y2)],
                                                 [int(self.x3), int(self.y3)],
                                                 [int(self.x4), int(self.y4)]])

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
        if p2.sticky and p1.sticky:
            p1.static, p2.static, p1.sticky, p2.sticky = True, True, False, False
            p1.stuck_to, p2.stuck_to = p2, p1
            play_sfx(SOUND_STICK)
        else:
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
            if not p1.static:
                p1.speed *= ELASTICITY_DEFAULT
            if not p2.static:
                p2.speed *= ELASTICITY_DEFAULT
            overlap = 0.5 * (p1.size + p2.size - distance + 1)
            if not p1.static:
                # p1.x += math.sin(angle)
                p1.x += math.sin(angle) * overlap
                # p1.y -= math.cos(angle)
                p1.y -= math.cos(angle) * overlap
            if not p2.static:
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

def play_sfx(sound):
    # play a random sound effect if it is in a list
    if isinstance(sound, list):
        pygame.mixer.Sound(sound[random.randint(0, len(sound)-1)]).play()
    else:
        pygame.mixer.Sound(sound).play()