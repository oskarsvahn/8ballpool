#!/usr/bin/env python
# covenvding=utf-8
# -*- coding: utf-8 -*
# coding=utf-8-
import logging
import pygame
import sys
import math

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Konstanter
FPS = 60
SCREEN_SIZE = (800, 600)
CAPTION = "Pygame 8 ball pool"

COLOR = {'ship': pygame.Color('#FF0000'),
         'ship_fill': pygame.Color('#660000'),
         'bg': pygame.Color('#333333'),
         'thruster': pygame.Color('#7799FF'),
}

CW = 1
CCW = 2


# Game states
STATE_PREGAME = 1
STATE_RUNNING = 2
STATE_GAMEOVER = 3

class Controller():
    """Game controller."""

    def __init__(self):
        """Initialize game controller."""
        self.fps = FPS

        pygame.init()
        pygame.mixer.quit()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption(CAPTION)
        self.clock = pygame.time.Clock()
        self.crash_font = pygame.font.Font('freesansbold.ttf',20)

        self.rotation = None


        self.world = World(self)
        self.cue = Cue(self)
        self.balls = [Ball(self, (200, 310), (255,255,255)),

                      Ball(self, (600, 300), (255,0,0)),
                      Ball(self, (600, 280), (0,0,255)),
                      Ball(self, (600, 320), (0,0,255)),
                      Ball(self, (600, 340), (255, 0, 0)),

                      Ball(self, (585, 290), (255, 0, 0)),
                      Ball(self, (585, 310), (255,0,0)),
                      Ball(self, (585, 330), (0, 0, 255)),

                      Ball(self, (570, 300), (0,0,255)),
                      Ball(self, (570, 320), (255, 0, 0)),

                      Ball(self, (555, 310), (0,0,255))]

        self.holes = [  Hole(self, (25,60)),
                        Hole(self, (25,575)),
                        Hole(self, (775,60)),
                        Hole(self, (775,575)),
                        Hole(self, (400,60)),
                        Hole(self, (400,575))]



        # Initialize game state
        self.game_state = STATE_PREGAME


    def run(self):
        """Main game loop."""
        while True:
            # -- Handle events -----------------------------------------------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # ALT + F4 or icon in upper right corner.
                    self.quit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # Escape key pressed.
                    self.quit()

                if self.game_state == STATE_PREGAME:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.game_state = STATE_RUNNING

                if self.game_state == STATE_RUNNING:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                        pass
#                        for ball in self.balls:
#                            self.balls.append(ball)
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.cue.draw()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                        self.cue.d +=0.5
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                        self.cue.d -=0.5
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                        self.rotation = CW
#                        self.cue.r +=0.005

                    if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                        self.rotation = CCW
#                        self.cue.r -=0.005


                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.cue.smach()

                    if event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
                        self.rotation = None
#                        self.cue.r +=0.005

                    if event.type == pygame.KEYUP and event.key == pygame.K_LEFT:
                        self.rotation = None
#                        self.cue.r -=0.005




            # -- Update game state -------------------------------------------

            if self.game_state == STATE_PREGAME:
                pass

            if self.game_state == STATE_RUNNING:
                if self.rotation == CW:
                    self.cue.r += 0.01
                if self.rotation == CCW:
                    self.cue.r -= 0.01


                for ball in self.balls:
                    ball.tick()


                # Generate the sequence of indexes below.
                #
                #     b1 b2 b3 b4
                # b1   x  x  x  x
                # b2   o  x  x  x
                # b3   o  o  x  x
                # b4   o  o  o  x
                #

                if self.balls >= 2:
                    for i in range(1, len(self.balls)):
                        for j in range(i):
                            # Genomfor kontroll
                            ball.check_collision(self.balls[i],
                                                 self.balls[j])
                for i in range(0, len(self.balls)):
                    Ball.check_collision_wall(self.balls[i])
                for i in range(0, len(self.balls)-1):
                    Ball.check_collision_hole(self.balls[i], self)

            if self.game_state == STATE_GAMEOVER:
                pass

            # -- Draw game ---------------------------------------------------

            if self.game_state == STATE_PREGAME:
                pass

            if self.game_state == STATE_RUNNING:
                self.world.draw()

                self.cue.draw()
                for hole in self.holes:
                    hole.draw()
                for ball in self.balls:
                    ball.draw()
            if self.game_state == STATE_GAMEOVER:
                logging.info('Points: {} m/s'.format(self.points))


            # Display drawn graphic
            pygame.display.flip()

            # Wait for next tick ...
            self.clock.tick(self.fps)

    def quit(self):
        logger.info('Quitting... good bye!')
        pygame.quit()
        sys.exit()

class Cue():
    def __init__(self, controller):
        self.controller = controller
        self.screen = controller.screen
        self.d = 3

        self.r = 0

    def draw(self):
        self.x = self.controller.balls[0].x
        self.y = self.controller.balls[0].y

        start = (self.x, self.y)
        end = (self.x + 100 * self.d * math.cos(self.r), self.y + 100 * self.d * math.sin(self.r))
        pygame.draw.aaline(self.screen, (255, 105, 0), start, end)


    def smach(self):
        self.controller.balls[0].v_x = self.d * math.cos(self.r)
        self.controller.balls[0].v_y = self.d * math.sin(self.r)
        logging.info('{}' .format(self.r*180/math.pi))

class World():
    def __init__(self, controller):
        self.controller = controller
        self.screen = controller.screen

    def draw(self):
        surface = pygame.Surface((800, 600), flags=pygame.SRCALPHA) #background
        pygame.draw.rect(surface, (0,204,51), (0, 0, 750, 520))
        self.screen.blit(surface, (25, 60))


class Hole():
    def __init__(self, controller, pos):
        self.controller = controller
        self.screen = controller.screen
        self.x, self.y = pos

    def draw(self):
        surface = pygame.Surface((31, 31), flags=pygame.SRCALPHA)
        pygame.draw.circle(surface, (100, 100, 100), (15, 15), 15)
        self.screen.blit(surface, ( self.x - 15, self.y - 15))

class Ball():
    def __init__(self, controller, pos, colour):
        self.controller = controller
        self.screen = controller.screen
        self.x, self.y = pos
        self.colour = colour
        #  Vilka varden behovs?
        self.direction = 0
        self.contact = 0
        self.v_x = 0
        self.v_y = 0
        self.v_x1 = 0
        self.v_y1 = 0

    def draw(self):
        surface = pygame.Surface((21, 21), flags=pygame.SRCALPHA)
        pygame.draw.circle(surface, self.colour, (10, 10), 10)
        self.screen.blit(surface, ( self.x - 10, self.y - 10))


    def tick(self):
        # Uppdatera bollens position

        self.x += self.v_x
        self.y += self.v_y
        self.v_x *= 0.99
        self.v_y *= 0.99
    @staticmethod
    def check_collision_wall(bi): #Baunce off wall
        if bi.x > 765:
            bi.v_x = -abs(bi.v_x)
        if bi.x < 35:
            bi.v_x = abs(bi.v_x)
        if bi.y > 570:
            bi.v_y = -abs(bi.v_y)
        if bi.y < 75:
            bi.v_y = abs(bi.v_y)
    def check_collision_hole(bi, self):
        if bi.x > 760:
            if bi.y < 80 or bi.y > 570:
                 self.balls.pop(self.balls.index(bi))
        elif 390 < bi.x < 410:
            if bi.y < 80 or bi.y > 570:
                self.balls.pop(self.balls.index(bi))
        elif bi.x < 40:
            if bi.y < 80 or bi.y > 570:
                self.balls.pop(self.balls.index(bi))
    def check_collision(self, bi, bj):
        # Kolliderar bollarna bi och bj?
        # Om kollision: Uppdatera bollarnas riktning och hastighet
        Angle = 0
        d = math.sqrt((bi.y-bj.y) * (bi.y-bj.y) + (bi.x-bj.x) * (bi.x-bj.x))
        if (d < 18):
            bi.v = math.sqrt(bi.v_x * bi.v_x + bi.v_y * bi.v_y)
            bj.v = math.sqrt(bj.v_x * bj.v_x + bj.v_y * bj.v_y)

            XDiff = (bj.x-bi.x) 
            YDiff = (bj.y-bi.y)

            logger.info('speed{}'.format(bi.v_x))
            if XDiff > 0:
                if YDiff > 0:
                    Angle = math.degrees(math.atan(YDiff/XDiff))

                elif YDiff < 0:
                    Angle = math.degrees(math.atan(YDiff/XDiff))

            elif XDiff < 0:
                if YDiff > 0:
                    Angle = 180 + math.degrees(math.atan(YDiff/XDiff))

                elif YDiff < 0:
                    Angle = -180 + math.degrees(math.atan(YDiff/XDiff))

            elif XDiff == 0:
                if YDiff > 0:
                    Angle = -90
                else:
                    Angle = 90

            elif YDiff == 0:
                if XDiff < 0:
                    Angle = 0
                else:
                    Angle = 180

            contact = math.radians(Angle)

            bi.v_x = bj.v*math.cos(bj.direction-contact)*math.cos(contact) + bi.v*math.sin(bi.direction-contact)*math.sin(contact) #imported from wikipedia "https://en.wikipedia.org/wiki/Elastic_collision#Two-dimensional_collision_with_two_moving_objects"
            bi.v_y = bj.v*math.cos(bj.direction-contact)*math.sin(contact) + bi.v*math.sin(bi.direction-contact)*math.cos(contact)

            bj.v_x = bj.v_x + bi.v_x1 - bi.v_x
            bj.v_y = bj.v_y + bi.v_y1 - bi.v_y


if __name__ == "__main__":
    logger.info('Starting...')
    c = Controller()
    c.run()
