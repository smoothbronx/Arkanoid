import pygame, time, copy, ast, random, math
import status, music
import numpy
from pygame.math import Vector2

pygame.init()

# Colors
White = (255, 255, 255)
Red = (169, 19, 38)
Black = (0, 0, 0)
Green = (8, 101, 55)
Silver = (192, 192, 192)
Gold = (255, 188, 0)
Grey = (100, 100, 100)
Yellow = (255, 255, 0)

# States
STATE_INTRO = -1
STATE_MENU_MAIN = 0
STATE_MENU_CHOOSE_LEVEL = 1
STATE_MENU_INSTRUCTIONS = 2
STATE_MENU_ABOUT = 3
STATE_MENU_OPTIONS = 4
STATE_MENU_PREMIUM = 5
STATE_BALL_IN_PADDLE = 6
STATE_PLAY = 7
STATE_NEXT_LVL = 8
STATE_BALL_OUT = 9
STATE_GAME_OVER = 10
STATE_WON = 11
STATE_SURE_TO_MENU = 12
STATE_SURE_TO_QUIT = 13
STATE_OUTRO = 14


class Options():
    def __init__(self, text, pos, hovered):
        self.text = text
        self.pos = pos
        self.hov = hovered
        self.font = pygame.font.SysFont("monospace", 40)

    def draw(self, menu, indeks):
        if self.hov == True:
            sp = self.font.render(self.text, True, White)
        else:
            sp = self.font.render(self.text, True, Grey)
        spRect = sp.get_rect()
        spRect.x, spRect.y = self.pos
        game.screen.blit(sp, spRect)
        if spRect.collidepoint(game.mouse_pos):
            game.menu_bool[menu][indeks] = True
        else:
            game.menu_bool[menu][indeks] = False

        # handleclicks menu
        if pygame.mouse.get_pressed()[0]:
            if game.menu_bool[0][0] == True:  # click play
                game.state = STATE_BALL_IN_PADDLE
                game.whichBrickSet()
                game.createBrick()
                game.resetAll()
                if game.music.music_on:
                    game.music.playGame()

            if game.menu_bool[0][1] == True:  # click choose level
                game.state = STATE_MENU_CHOOSE_LEVEL
                game.menu_bool[0][1] = False
                game.time_start = time.time()

            if game.menu_bool[0][2] == True:  # click insructions
                game.state = STATE_MENU_INSTRUCTIONS

            if game.menu_bool[0][3] == True:  # click about
                game.state = STATE_MENU_ABOUT

            if game.menu_bool[0][4] == True:  # click optons
                game.state = STATE_MENU_OPTIONS

            if game.menu_bool[0][5] == True:  # click quit
                game.wannaQuit()

            if game.menu_bool[1][0] == True:  # back from levels
                game.state = STATE_MENU_MAIN
                game.menu_bool[1][0] = False

            if game.menu_bool[2][0] == True:  # back from instructions
                game.state = STATE_MENU_MAIN
                game.menu_bool[2][0] = False

            if game.menu_bool[3][0] == True:  # back from about
                game.state = STATE_MENU_MAIN
                game.menu_bool[3][0] = False

            if game.menu_bool[4][0] == True:  # on/off music
                if game.music.music_on == True:
                    game.music.music_on = False
                    pygame.mixer.music.pause()
                else:
                    game.music.music_on = True
                    pygame.mixer.music.unpause()
                time.sleep(0.05)

            if game.menu_bool[4][1] == True:  # on/off effects
                if game.music.music_effects == True:
                    game.music.music_effects = False
                else:
                    game.music.music_effects = True
                time.sleep(0.05)

            if game.menu_bool[4][2] == True:  # back from options
                game.state = STATE_MENU_MAIN
                game.menu_bool[4][2] = False


class Ball():
    def __init__(self):
        self.circle_radius = 15
        self.circle_x = 250
        self.circle_y = 250
        self.circle_color = White

        self.circle_speed = 4
        self.circle_V_value = Vector2(0.1, 4)
        self.circle_V = self.circle_V_value
        self.circle_V.scale_to_length(self.circle_speed)

    def invertY(self):
        self.circle_V = (self.circle_V[0], -self.circle_V[1])

    def invertX(self):
        self.circle_V = (-self.circle_V[0], self.circle_V[1])

    def invertBoth(self):
        self.circle_V = (-self.circle_V[0], -self.circle_V[1])

    def update(self):
        self.circle_x += self.circle_V[0]
        self.circle_y += self.circle_V[1]

        # top
        if self.circle_y - self.circle_radius <= 0 and self.circle_V[1] < 0:
            self.invertY()
            self.circle_y = 1 + self.circle_radius
        # left
        if self.circle_x - self.circle_radius <= 0 and self.circle_V[0] < 0:
            self.invertX()
        # right
        if self.circle_x > game.field_x - self.circle_radius and self.circle_V[0] > 0:
            self.invertX()
        # paddle
        if self.circle_y + self.circle_radius >= game.paddle_y and self.circle_x >= game.paddle_x and \
                self.circle_x <= game.paddle_x + game.paddle_width and self.circle_V[1] > 0:
            self.invertY()
            if game.music.music_effects:
                game.music.playBounce()
            self.circle_V += game.paddleV / 3
            self.circle_V.scale_to_length(self.circle_speed)

        # bonus
        if game.bonus.active[0]:
            if self.circle_y + self.circle_radius >= game.bonus.bonus0_pos and self.circle_V[1] > 0:
                self.invertY()

    def intersected(self, rect):
        deltaX = self.circle_x - max(rect.x, min(self.circle_x, rect.x + rect.width))
        deltaY = self.circle_y - max(rect.y, min(self.circle_y, rect.y + rect.height))
        d = deltaX ** 2 + deltaY ** 2
        if d <= self.circle_radius ** 2:
            if deltaX == 0:
                return 2
            elif deltaY == 0:
                return 1
            elif (math.fabs(deltaX - deltaY) < 10) and ((self.circle_V[0] > 0 and self.circle_x < rect.x) or (
                    self.circle_V[0] < 0 and self.circle_x > rect.x)):
                return 3
            elif math.fabs(deltaX) >= math.fabs(deltaY):
                return 1
            else:
                return 2
        else:
            return 0

    def detectCollision(self):
        self.circle = pygame.Rect(self.circle_x - self.circle_radius, self.circle_y - self.circle_radius,
                                  2 * self.circle_radius, 2 * self.circle_radius)
        for i in range(game.brick_rows):
            for j in range(game.brick_columns):
                if game.actual_brick_set[i][j] > 0:
                    if time.time() - game.brick_time[j + i * game.brick_columns] > 0.1:
                        if self.intersected(game.bricks[j + i * game.brick_columns]) > 0:
                            if game.actual_brick_set[i][j] != 3:
                                if self.circle_color == White or game.actual_brick_set[i][j] == 4:
                                    if self.intersected(
                                            game.bricks[j + i * game.brick_columns]) == 1:  # hit form left or right
                                        self.invertX()
                                    elif self.intersected(
                                            game.bricks[j + i * game.brick_columns]) == 2:  # hit from up or down
                                        self.invertY()
                                    else:
                                        self.invertBoth()
                            if game.actual_brick_set[i][j] != 4:
                                if game.actual_brick_set[i][j] == 3:
                                    game.actual_brick_set[i][j] -= 2
                                game.actual_brick_set[i][j] -= 1

                            stats.factor += 1
                            stats.points += 1 + stats.factor
                            if game.music.music_effects:
                                game.music.playPunch()
                            game.brick_time[j + i * game.brick_columns] = time.time()
                            stats.last_hit = time.time()
                            break

    def draw(self):
        pygame.draw.circle(game.screen, self.circle_color, [int(self.circle_x), int(self.circle_y)], self.circle_radius,
                           0)


class BulletFly():
    def __init__(self, x):
        self.pos_x = x
        self.pos_y = game.paddle_y

    def update(self):
        self.pos_y -= 10
        game.screen.blit(game.img_bullet, (self.pos_x, self.pos_y))
        rect = game.img_bullet.get_rect()
        rect.x = self.pos_x
        rect.y = self.pos_y

        for i in range(game.brick_rows):
            for j in range(game.brick_columns):
                if game.actual_brick_set[i][j] > 0:
                    if rect.colliderect(game.bricks[j + i * game.brick_columns]):
                        self.removeFirst()
                        if game.actual_brick_set[i][j] != 4:
                            if game.actual_brick_set[i][j] == 3:
                                game.actual_brick_set[i][j] -= 2
                            game.actual_brick_set[i][j] -= 1
                        stats.factor += 1
                        stats.points += 1 + stats.factor
                        stats.last_hit = time.time()

        if self.pos_y < -20:  # fly over the sreen
            self.removeFirst()

    def removeFirst(self):
        game.bonus.bullets_fly.reverse()
        game.bonus.bullets_fly.pop()
        game.bonus.bullets_fly.reverse()


class BulletReady():
    def __init__(self):
        self.pos_x = game.paddle_x + 10
        self.pos_y = game.paddle_y

    def update(self, x):
        self.pos_x = x
        self.pos_y = game.paddle_y
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LALT]:
            if time.time() - game.bonus.bullet_time > 0.5:
                game.bonus.bullets_ready.pop()
                game.bonus.bullets_fly.append(BulletFly(self.pos_x))
                game.bonus.bullet_time = time.time()
        game.screen.blit(game.img_bullet, (self.pos_x, self.pos_y))


class Bonus():
    def __init__(self):
        #        0 - floor
        #        1 - massive
        #        2 - laser
        #        3 - slow
        #        4 - life
        self.active = [False, False, False, False, False]
        self.time_active = [0, 0, 0, 0, 0]
        self.visible = [False, False, False, False, False]
        self.img = [pygame.image.load("img/F.png"), pygame.image.load("img/M.png"), \
                    pygame.image.load("img/L.png"), pygame.image.load("img/T.png"), pygame.image.load("img/H.png")]
        self.time = time.time()
        self.pos = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
        self.bonus0_pos = 400
        self.slow = False
        self.bullet_time = time.time()

    def reset(self):
        self.active = [False, False, False, False, False]
        self.time_active = [0, 0, 0, 0, 0]
        self.visible = [False, False, False, False, False]
        self.time = time.time()
        self.bullets_ready = []
        self.bullets_fly = []
        if self.slow == True:
            game.ball.circle_speed *= 2
            vect = Vector2(game.ball.circle_V)
            vect.scale_to_length(game.ball.circle_speed)
            game.ball.circle_V = vect
            self.slow = False

    def randPlace(self):
        self.x = random.randint(10, game.field_x - 50)
        self.y = random.randint(10, game.paddle_y - 60)
        return [self.x, self.y]

    def update(self):
        if time.time() - self.time > 7:  # create bonus
            index = random.randrange(5)
            self.pos[index] = self.randPlace()
            self.visible[index] = True
            self.time = time.time()

        self.display()
        x = game.paddle_x + game.paddle_width / 2 - 16
        for bull in self.bullets_ready:
            pygame.draw.rect(game.screen, White, [game.paddle_x + game.paddle_width / 2 - 17, game.paddle_y + 19, 5, 1])
            bull.update(x)
            x += 15
        for bull in self.bullets_fly:
            bull.update()

        if self.active[0]:
            pygame.draw.rect(game.screen, Green, [0, self.bonus0_pos, game.field_x, 10], 0)
        if self.active[1]:
            game.ball.circle_color = Gold
        else:
            game.ball.circle_color = White

        if self.active[2]:
            for i in range(3):
                if len(self.bullets_ready) < 3:
                    self.bullets_ready.append(BulletReady())
            self.active[2] = False

        if self.active[3]:
            if self.slow != True:
                game.ball.circle_speed /= 2
                vect = Vector2(game.ball.circle_V)
                vect.scale_to_length(game.ball.circle_speed)
                game.ball.circle_V = vect
                self.slow = True

        if self.active[4] and stats.lives < 3:
            stats.lives += 1
            self.active[4] = False

        for i in range(4):
            if self.active[i] and time.time() - self.time_active[i] > 5:
                self.active[i] = False
                if i == 3:
                    self.slow = False
                    game.ball.circle_speed *= 2
                    vect = Vector2(game.ball.circle_V)
                    vect.scale_to_length(game.ball.circle_speed)
                    game.ball.circle_V = vect

    def display(self):
        for i in range(5):
            if self.visible[i]:
                game.screen.blit(self.img[i], self.pos[i])
                rect = self.img[i].get_rect()
                rect.x = self.pos[i][0]
                rect.y = self.pos[i][1]
                if self.intersected(rect):
                    self.active[i] = True
                    self.visible[i] = False
                    self.time_active[i] = time.time()

    def intersected(self, rect):
        deltaX = game.ball.circle_x - max(rect.x, min(game.ball.circle_x, rect.x + rect.width))
        deltaY = game.ball.circle_y - max(rect.y, min(game.ball.circle_y, rect.y + rect.height))
        d = deltaX ** 2 + deltaY ** 2
        if d <= game.ball.circle_radius ** 2:
            return True
        else:
            return False


class Game():
    def __init__(self):
        # init
        self.game_ver = "0.1.2"
        self.activeBot = False
        self.time_start = time.time()
        self.music = music.Music()
        self.initImages()
        self.ball = Ball()
        self.bonus = Bonus()

        self.screen_width = 1000
        self.screen_height = 480
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Arkanoid from Bronx inc.")
        self.screen_color = Black

        self.fps = 100
        self.clock = pygame.time.Clock()

        self.paddle_x = 400
        self.paddle_y = 440
        self.paddle_height = 20
        self.paddle_color = Green
        self.paddle_width_tab = [50, 100, 150, 200]
        self.paddle_index = 2
        self.paddle_width = self.paddle_width_tab[self.paddle_index]
        self.x_speed = 600  # pos in options menu
        self.click_on_speed = False

        # paddle physics
        self.paddleV = Vector2(float(0), float(0))
        self.acc = 0
        self.force = 0.85
        self.resistance = 0.87
        # separator between game field and stats
        self.field_width = 10
        self.field_height = self.screen_height
        self.field_x = 800
        self.field_y = 0
        self.field_color = Green
        self.menu_bool = [[False, False, False, False, False, False, False], [False], [False], [False],
                          [False, False, False], [False]]
        # blocks
        self.brick_width = 58
        self.brick_height = 20
        self.brick_color_normal = Red
        self.brick_color_strong = Silver
        self.brick_color_ghost = White
        self.brick_color_boss = Gold

        self.levels = open('levels.txt', 'r')
        self.brick_set = []
        for i in range(10):
            self.brick_set.append(ast.literal_eval(self.levels.readline()))

        self.activeBosses = True
        self.bricks = []
        self.brick_time = []

        self.state = STATE_INTRO
        self.running = True
        self.playFromChoose = False

    def initImages(self):
        self.img_right = pygame.image.load('img/right.png')
        self.img_left = pygame.image.load('img/left.png')
        self.img_up = pygame.image.load('img/up.png')
        self.img_up2 = pygame.image.load("img/upp.png")
        self.img_lives_3 = pygame.image.load("img/heart_3.png")
        self.img_lives_2 = pygame.image.load("img/heart_2.png")
        self.img_lives_1 = pygame.image.load("img/heart_1.png")
        self.img_lives_inf = pygame.image.load("img/heart_inf.png")
        self.img_bullet = pygame.image.load("img/bullet.png")
        self.img_levels = []
        for i in range(1, 11):
            self.img_levels.append(pygame.image.load("img/level_" + str(i) + ".png"))
        self.img_intro = []
        for i in range(34):
            if i < 10:
                self.img_intro.append(pygame.image.load("img/intro/intro_00" + str(i) + ".png"))
            else:
                self.img_intro.append(pygame.image.load("img/intro/intro_0" + str(i) + ".png"))

    def resetAll(self):
        stats.points = 0
        stats.lives = 3
        stats.f = open('highscore.txt', 'r+')
        stats.highscore = int(stats.f.readline())
        stats.level = 1
        self.whichBrickSet()
        self.paddle_x = 400
        self.paddle_y = 440
        self.paddleV = (0, 0)
        self.acc = 0
        self.bonus.reset()

    def whichBrickSet(self):
        self.actual_brick_set = []
        self.brick_time.clear()
        self.actual_brick_set = copy.deepcopy(self.brick_set[stats.level - 1])
        self.brick_rows = len(self.actual_brick_set)
        self.brick_columns = len(self.actual_brick_set[0])
        for i in range(self.brick_rows):
            for j in range(self.brick_columns):
                self.brick_time.append(0)

    def createBrick(self):
        self.bricks.clear()
        pos_y = 20
        for i in range(self.brick_rows):
            pos_x = 5
            for j in range(self.brick_columns):
                self.bricks.append(pygame.Rect(pos_x, pos_y, self.brick_width, self.brick_height))
                pos_x += 3 + self.brick_width
            pos_y += 3 + self.brick_height

    def loadTempLevel(self, lvl):
        self.resetAll()
        self.actual_brick_set = []
        self.brick_time.clear()
        self.actual_brick_set = copy.deepcopy(self.brick_set[lvl])
        self.brick_rows = len(self.actual_brick_set)
        self.brick_columns = len(self.actual_brick_set[0])
        self.createBrick()
        for i in range(self.brick_rows):
            for j in range(self.brick_columns):
                self.brick_time.append(0)
        game.state = STATE_BALL_IN_PADDLE
        if game.music.music_on:
            game.music.playGame()

    def drawBricks(self):
        for i in range(self.brick_rows):
            for j in range(self.brick_columns):
                if self.actual_brick_set[i][j] == 1:
                    pygame.draw.rect(self.screen, self.brick_color_normal, self.bricks[self.brick_columns * i + j])
                elif self.actual_brick_set[i][j] == 2:
                    pygame.draw.rect(self.screen, self.brick_color_strong, self.bricks[self.brick_columns * i + j])
                elif self.actual_brick_set[i][j] == 3:
                    pygame.draw.rect(self.screen, self.brick_color_ghost, self.bricks[self.brick_columns * i + j], 1)
                elif self.actual_brick_set[i][j] == 4:
                    pygame.draw.rect(self.screen, self.brick_color_boss, self.bricks[self.brick_columns * i + j])

    def addForce(self, direction):
        if direction == "left" and self.paddle_x > 10:
            self.acc -= self.force
        elif direction == "right" and self.paddle_x < self.field_x - self.paddle_width - 10:
            self.acc += self.force

    def handlePaddlePhysics(self):
        self.paddleV = numpy.asarray(self.paddleV) * self.resistance
        self.paddleV = Vector2(self.paddleV[0], self.paddleV[1])
        self.paddleV[0] += self.acc
        if self.state == STATE_PLAY or self.state == STATE_BALL_IN_PADDLE:
            if self.acc < 0 and self.paddle_x > 10:
                self.paddle_x += self.paddleV[0]
            elif self.acc > 0 and self.paddle_x < self.field_x - self.paddle_width - 10:
                self.paddle_x += self.paddleV[0]
        self.acc *= 0

    def loose(self):
        if self.ball.circle_y + self.ball.circle_radius > self.paddle_y + self.paddle_height:
            stats.lives -= 1
            if stats.lives > 0:
                self.state = STATE_BALL_OUT
                self.time_start = time.time()
            else:
                if self.music.music_effects:
                    self.music.playFail()
                self.state = STATE_GAME_OVER
                self.time_start = time.time()

    def allGone(self):
        for i in range(self.brick_rows):
            for j in range(self.brick_columns):
                if self.actual_brick_set[i][j] > 0:
                    return False
        return True

    def allGoneButBosses(self):
        for i in range(self.brick_rows):
            for j in range(self.brick_columns):
                if self.actual_brick_set[i][j] > 0 and self.actual_brick_set[i][j] < 4:
                    return False
        return True

    def weakBosses(self):
        for i in range(self.brick_rows):
            for j in range(self.brick_columns):
                if self.actual_brick_set[i][j] == 4:
                    self.actual_brick_set[i][j] = 2
        self.activeBosses = False

    def onThePaddle(self):
        self.ball.circle_x = self.paddle_x + self.paddle_width / 2
        self.ball.circle_y = self.paddle_y - self.ball.circle_radius - 1
        self.ball.circle_V = self.ball.circle_V_value

    def printSmall(self, napis, x, y):
        myfont = pygame.font.SysFont("monospace", 30)
        label = myfont.render(napis, 1, White)
        self.screen.blit(label, (x, y))

    def printSmall2(self, napis, x, y):
        myfont = pygame.font.SysFont("monospace", 20)
        label = myfont.render(napis, 1, White)
        self.screen.blit(label, (x, y))

    def printSmaller(self, napis, x, y):
        myfont = pygame.font.SysFont("monospace", 10)
        label = myfont.render(napis, 1, White)
        self.screen.blit(label, (x, y))

    def printBig(self, napis, x, y):
        myfont = pygame.font.SysFont("monospace", 35)
        label = myfont.render(napis, 1, White)
        self.screen.blit(label, (x, y))

    def printBigger(self, napis, x, y):
        myfont = pygame.font.SysFont("monospace", 60)
        label = myfont.render(napis, 1, White)
        self.screen.blit(label, (x, y))

    def printScore(self):
        if stats.factor < 2:
            color = White
        elif stats.factor < 5:
            color = Gold
        else:
            color = Red
        myfont = pygame.font.SysFont("monospace", 35)
        label1 = myfont.render("Score", 1, color)
        label2 = myfont.render(str(stats.points), 1, color)
        label3 = myfont.render("COMBO ", 1, color)
        label4 = myfont.render(str(stats.factor) + 'x', 1, color)

        self.screen.blit(label1, (850, 200))
        if stats.points < 10:
            self.screen.blit(label2, (890, 235))
        elif stats.points < 100:
            self.screen.blit(label2, (880, 235))
        else:
            self.screen.blit(label2, (870, 235))
        self.screen.blit(label3, (850, 290))
        self.screen.blit(label4, (880, 325))

    def printFPS(self, fps):
        myfont = pygame.font.SysFont("monospace", 20)
        label = myfont.render(fps, 1, Yellow)
        self.screen.blit(label, (961, 10))

    def displayLives(self):
        if stats.lives > 3:
            self.printBig("+", 975, 70)
        if stats.lives >= 3:
            self.screen.blit(self.img_lives_3, (810, 15))
        if stats.lives == 2:
            self.screen.blit(self.img_lives_2, (810, 15))
        if stats.lives == 1:
            self.screen.blit(self.img_lives_1, (810, 15))

    def saveScore(self):
        if stats.points > stats.highscore:
            stats.f.seek(0)
            stats.f.write(str(stats.points))

    def intro(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.state = STATE_MENU_MAIN
        frame = int((time.time() - self.time_start) * 10)
        if frame <= 33:
            self.screen.blit(self.img_intro[frame], (140, 0))
        if frame > 40:
            self.state = STATE_MENU_MAIN

    def wannaMenu(self):
        self.state_previous = self.state
        self.state = STATE_SURE_TO_MENU

    def wannaQuit(self):
        self.state_previous = self.state
        self.state = STATE_SURE_TO_QUIT

    def endGame(self):
        self.time_start = time.time()
        self.state = STATE_OUTRO

    def outro(self):
        self.printBigger("Goodbye", 370, 200)
        if time.time() - self.time_start > 1:
            self.running = False

    def loop(self):
        while self.running:
            self.clock.tick(self.fps)
            self.screen.fill(self.screen_color)
            keys = pygame.key.get_pressed()
            self.printFPS(str((int(self.clock.get_fps()))))
            self.mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if self.state != STATE_SURE_TO_QUIT:
                    if event.type == pygame.QUIT:
                        self.wannaQuit()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        if self.state == STATE_MENU_MAIN:
                            self.wannaQuit()
                        elif self.state >= STATE_BALL_IN_PADDLE and self.state <= STATE_NEXT_LVL:
                            self.wannaMenu()
                        elif self.state != STATE_SURE_TO_MENU:
                            self.state = STATE_MENU_MAIN

            if self.state == STATE_INTRO:
                self.intro()

            elif self.state == STATE_MENU_MAIN:
                menu_main_options = [Options("Play", (100, 20), self.menu_bool[0][0]),
                                     Options("Choose level", (100, 90), self.menu_bool[0][1]), \
                                     Options("Instructions", (100, 180), self.menu_bool[0][2]),
                                     Options("About", (100, 250), self.menu_bool[0][3]), \
                                     Options("Options", (100, 320), self.menu_bool[0][4]),
                                     Options("End game", (100, 410), self.menu_bool[0][5])]
                for i in range(len(menu_main_options)):
                    menu_main_options[i].draw(0, i)
                self.state_previous = STATE_MENU_MAIN

            elif self.state == STATE_MENU_CHOOSE_LEVEL:
                option = Options("Back", (850, 410), self.menu_bool[1][0])
                option.draw(1, 0)
                x = 20
                y = 60
                self.rect = []

                for i in range(10):
                    self.screen.blit(self.img_levels[i], (x, y))
                    self.rect.append(self.img_levels[i].get_rect())
                    self.rect[i].x = x
                    self.rect[i].y = y
                    if self.rect[i].collidepoint((self.mouse_pos)):
                        self.screen.blit(self.img_up2, (x + 60, y + 100))
                        self.printSmall(str(i + 1), x + 90, y + 110)
                    x += 200
                    if i == 4:
                        y += 180
                        x = 20
                if pygame.mouse.get_pressed()[0] and time.time() - self.time_start > 0.5:
                    for i in range(10):
                        if self.rect[i].collidepoint((self.mouse_pos)):
                            self.playFromChoose = True
                            self.loadTempLevel(i)

            elif self.state == STATE_MENU_INSTRUCTIONS:
                option = Options("Back", (850, 430), self.menu_bool[2][0])
                option.draw(2, 0)
                # steering 
                self.printSmall2("[left]", 300, 80)
                self.printSmall2("[right]", 630, 80)
                self.printSmall2("[space]", 555, 5)
                self.printSmall2("[L_alt]", 425, 110)
                pygame.draw.circle(self.screen, self.ball.circle_color, [500, 63], self.ball.circle_radius, 0)
                pygame.draw.rect(self.screen, self.paddle_color,
                                 [425, 80, self.paddle_width_tab[2], self.paddle_height], 0)
                self.screen.blit(self.img_bullet, (425 + self.paddle_width_tab[2] / 2 - 16, 80))
                self.screen.blit(self.img_bullet, (425 + self.paddle_width_tab[2] / 2 - 1, 80))
                self.screen.blit(self.img_right, (585, 79))
                self.screen.blit(self.img_left, (375, 79))
                self.screen.blit(self.img_up, (510, 10))
                # bricks
                self.printSmall("Bricks:", 510, 150)
                pygame.draw.rect(self.screen, self.brick_color_normal, [510, 200, self.brick_width, self.brick_height],
                                 0)
                pygame.draw.rect(self.screen, self.brick_color_strong, [510, 260, self.brick_width, self.brick_height],
                                 0)
                pygame.draw.rect(self.screen, self.brick_color_ghost, [510, 320, self.brick_width, self.brick_height],
                                 1)
                pygame.draw.rect(self.screen, self.brick_color_boss, [510, 380, self.brick_width, self.brick_height], 0)
                self.printSmall2("normal bricks", 580, 192)
                self.printSmall2("strengthened bricks,", 580, 252)
                self.printSmall2(" hit them twice", 580, 272)
                self.printSmall2("ghost bricks, ", 580, 312)
                self.printSmall2(" doesn't change your direction", 580, 332)
                self.printSmall2("BOSS bricks, destroy  ", 580, 372)
                self.printSmall2(" other bricks before them", 580, 392)
                # Bonuses
                self.printSmall("Bonuses:", 20, 140)
                y = 180
                for img in self.bonus.img:
                    self.screen.blit(img, (20, y))
                    y += 60
                self.printSmall2("extra, really BIG paddle", 70, 190)
                self.printSmall2("Gold ball, bricks don't", 70, 240)
                self.printSmall2(" change its direction", 70, 260)
                self.printSmall2("You have 3 bullets, ", 70, 300)
                self.printSmall2("press left alt to shoot a brick", 70, 320)
                self.printSmall2("Ball is 2 times slower", 70, 370)
                self.printSmall2("If you really need extra life", 70, 420)
                self.printSmall2("you will receive it", 70, 440)

            elif self.state == STATE_MENU_ABOUT:
                option = Options("Back", (850, 400), self.menu_bool[3][0])
                option.draw(3, 0)
                self.printSmall("Uhwatov 'Bronx' Vladislav", 40, 130)
                self.printSmall("Game version: " + self.game_ver, 40, 50)
                self.printSmall("Python version: 3.6.6", 40, 210)
                self.printSmall("PyGame version: 1.9.6", 40, 290)
                self.printSmall("Contact: vlad.uhwatov@yandex.ru", 40, 370)

            elif self.state == STATE_MENU_OPTIONS:
                # Music and effects
                menu_options_options = [Options("Music: " + str(self.music.music_on), (100, 30), self.menu_bool[4][0]), \
                                        Options("Effects: " + str(self.music.music_effects), (100, 130),
                                                self.menu_bool[4][1]), \
                                        Options("Back", (850, 400), self.menu_bool[4][2])]
                for i in range(len(menu_options_options)):
                    menu_options_options[i].draw(4, i)
                # Paddle size
                myfont = pygame.font.SysFont("monospace", 40)
                label = myfont.render("Paddle size:", 1, Grey)
                self.screen.blit(label, (100, 230))
                pygame.draw.rect(self.screen, self.paddle_color, [400, 245, self.paddle_width, self.paddle_height], 0)
                if pygame.mouse.get_pressed()[0] and time.time() - self.time_start > 0.2:
                    rect_paddle = pygame.draw.rect(self.screen, self.paddle_color,
                                                   [400, 245, self.paddle_width, self.paddle_height], 0)
                    if rect_paddle.collidepoint(self.mouse_pos):
                        if self.paddle_index == 3:
                            self.paddle_index = 0
                        else:
                            self.paddle_index += 1
                        self.paddle_width = self.paddle_width_tab[self.paddle_index]
                        self.time_start = time.time()
                # Ball speed - slide
                label = myfont.render("Ball speed:", 1, Grey)
                self.screen.blit(label, (100, 330))
                pygame.draw.rect(self.screen, Grey, [400, 355, 400, 2])
                rect_speed = pygame.draw.rect(self.screen, White, [self.x_speed, 346, 20, 20], 0)
                if pygame.mouse.get_pressed()[0] and rect_speed.collidepoint(self.mouse_pos):
                    self.click_on_speed = True
                if self.click_on_speed == True and pygame.mouse.get_pressed()[0] == 0:
                    self.click_on_speed = False
                if self.click_on_speed and self.mouse_pos[0] >= 400 and self.mouse_pos[0] <= 800:
                    self.x_speed = self.mouse_pos[0] - 10
                    self.ball.circle_speed = (self.mouse_pos[0] - 200) / 100
                self.printBig(str(self.ball.circle_speed), 850, 335)

            elif self.state >= STATE_BALL_IN_PADDLE and self.state <= STATE_WON:
                if keys[pygame.K_RIGHT]:
                    self.addForce("right")
                if keys[pygame.K_LEFT]:
                    self.addForce("left")
                if (keys[pygame.K_SPACE]) and self.state == STATE_BALL_IN_PADDLE:
                    self.state = STATE_PLAY

                if self.activeBot:
                    if self.ball.circle_x > self.paddle_x + self.paddle_width / 2 and self.ball.circle_y + self.ball.circle_radius < self.paddle_y - 25:
                        self.addForce("right")
                    else:
                        self.addForce("left")

                self.ball.draw()
                pygame.draw.rect(self.screen, self.paddle_color,
                                 [self.paddle_x, self.paddle_y, self.paddle_width, self.paddle_height], 0)
                pygame.draw.rect(self.screen, self.field_color,
                                 [self.field_x, self.field_y, self.field_width, self.field_height], 0)
                self.handlePaddlePhysics()
                self.bonus.update()
                if self.state != STATE_NEXT_LVL:
                    self.drawBricks()
                self.displayLives()
                self.printBig("Level", 850, 120)
                self.printBig(str(stats.level), 890, 150)
                self.printScore()
                self.printBig("Highscore", 810, 385)
                self.printBig(str(stats.highscore), 870, 420)

                # Reset combo
                if time.time() - stats.last_hit > 1.6:
                    stats.factor = 0

                if self.state == STATE_PLAY:
                    self.ball.update()
                    self.loose()
                    self.ball.detectCollision()
                    if self.activeBosses and self.allGoneButBosses():
                        self.weakBosses()

                if self.state == STATE_BALL_IN_PADDLE:
                    self.onThePaddle()
                    if self.activeBot:
                        self.state = STATE_PLAY

                if self.state == STATE_BALL_OUT:
                    if time.time() - self.time_start > 1:
                        self.state = STATE_BALL_IN_PADDLE

                if self.state == STATE_GAME_OVER:
                    if time.time() - self.time_start < 3:
                        self.printBigger("Game Over", 250, 200)
                        self.saveScore()

                    else:
                        self.resetAll()
                        if self.music.music_on:
                            self.music.playMenu()
                        self.state = STATE_MENU_MAIN

                if self.allGone() and self.state == STATE_PLAY:  # Total win
                    if stats.level == 10 or self.playFromChoose:
                        self.state = STATE_WON
                        self.playFromChoose = False
                    else:
                        stats.level += 1
                        if self.music.music_effects:
                            self.music.playNext()
                        self.activeBosses = True
                        self.time_start = time.time()
                        self.whichBrickSet()
                        self.state = STATE_NEXT_LVL

                if self.state == STATE_NEXT_LVL:
                    self.printBigger("Next Level!", 250, 200)
                    self.whichBrickSet()
                    self.createBrick()
                    if time.time() - self.time_start > 2:
                        self.bonus.reset()
                        self.state = STATE_BALL_IN_PADDLE

                if self.state == STATE_WON:
                    self.printBigger("You Win!", 250, 200)
                    self.printSmall("press [r] to return to main menu", 140, 320)
                    self.saveScore()
                    if keys[pygame.K_r]:
                        self.state = STATE_MENU_MAIN

            elif self.state == STATE_SURE_TO_MENU:
                self.printBig("Sure you wanna go to main menu? (Y/N)", 120, 200)
                if keys[pygame.K_y]:
                    self.state = STATE_MENU_MAIN
                elif keys[pygame.K_n]:
                    self.state = self.state_previous

            elif self.state == STATE_SURE_TO_QUIT:
                self.printBig("Sure you wanna quit? (Y/N)", 210, 200)
                if keys[pygame.K_y]:
                    self.endGame()
                elif keys[pygame.K_n]:
                    self.state = self.state_previous

            elif self.state == STATE_OUTRO:
                self.outro()

            pygame.display.flip()


# Main
stats = status.Status()
game = Game()
game.loop()
pygame.quit()
