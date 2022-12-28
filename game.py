import pygame
import os
import random

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 700

IMAGE_PIPE = pygame.transform.scale2x(pygame.image.load(os.path.join('assets/img', 'pipe.png ')))
IMAGE_BASE = pygame.transform.scale2x(pygame.image.load(os.path.join('assets/img', 'base.png')))
IMAGE_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('assets/img', 'bg.png')))
IMAGE_PLAYER = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('assets/img', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('assets/img', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('assets/img', 'bird3.png'))),
]

pygame.font.init()
FONT_POINTS = pygame.font.SysFont('arial', 50)


class Player:
    IMG = IMAGE_PLAYER
    ROTATION_MAX = 25
    SPEED_ROTATION = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.count_image = 0
        self.image = self.IMG[0]

    def jump(self):
        self.speed = -10.5
        self.time = 0
        self.height = self.y

    def move(self):
        self.time += 1
        displacement = 1.5 * (self.time ** 2) + self.speed * self.time
        if displacement > 16:
            displacement = 16
        elif displacement < 0:
            displacement -= 2
        self.y += displacement
        if displacement < 0 or self.y < (self.height + 50):
            if self.angle < self.ROTATION_MAX:
                self.angle = self.ROTATION_MAX
        else:
            if self.angle > -90:
                self.angle -= self.SPEED_ROTATION

    def draw(self, screen):
        self.count_image += 1
        if self.count_image < self.ANIMATION_TIME:
            self.image = self.IMG[0]
        elif self.count_image < self.ANIMATION_TIME * 2:
            self.image = self.IMG[1]
        elif self.count_image < self.ANIMATION_TIME * 3:
            self.image = self.IMG[2]
        elif self.count_image < self.ANIMATION_TIME * 4:
            self.image = self.IMG[1]
        elif self.count_image < self.ANIMATION_TIME * 4 + 1:
            self.image = self.IMG[0]
            self.count_image = 0
        if self.angle <= -80:
            self.image = self.IMG[1]
            self.count_image = self.ANIMATION_TIME * 2

        rotation_image = pygame.transform.rotate(self.image, self.angle)
        position_center_image = self.image.get_rect(topleft=(self.x, self.y)).center
        rectangle = rotation_image.get_rect(center=position_center_image)
        screen.blit(rotation_image, rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Pipe:
    DISTANCE = 200
    SPEED = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.position_top = 0
        self.position_base = 0
        self.PIPE_TOP = pygame.transform.flip(IMAGE_PIPE, False, True)
        self.PIPE_BASE = IMAGE_PIPE
        self.pipe_pass = False
        self.height_define()

    def height_define(self):
        self.height = random.randrange(50, 350)
        self.position_top = self.height - self.PIPE_TOP.get_height()
        self.position_base = self.height + self.DISTANCE

    def move(self):
        self.x -= self.SPEED

    def draw(self, screen):
        screen.blit(self.PIPE_TOP, (self.x, self.position_top))
        screen.blit(self.PIPE_BASE, (self.x, self.position_base))

    def collision(self, player):
        player_mask = player.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        base_mask = pygame.mask.from_surface(self.PIPE_BASE)
        distance_top = (self.x - player.x, self.position_top - round(player.y))
        distance_base = (self.x - player.x, self.position_base - round(player.y))
        top_point = player_mask.overlap(top_mask, distance_top)
        base_point = player_mask.overlap(base_mask, distance_base)
        if base_point or top_point:
            return True
        else:
            return False


class Base:
    SPEED = 5
    WIDTH = IMAGE_BASE.get_width()
    IMAGE = IMAGE_BASE

    def __init__(self, y):
        self.y = y
        self.x0 = 0
        self.x1 = self.WIDTH

    def move(self):
        self.x0 -= self.SPEED
        self.x1 -= self.SPEED

        if self.x0 + self.WIDTH < 0:
            self.x0 = self.x1 + self.WIDTH
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x0 + self.WIDTH

    def draw(self, screen):
        screen.blit(self.IMAGE, (self.x0, self.y))
        screen.blit(self.IMAGE, (self.x1, self.y))


def draw_screen(screen, players, pipes, base, points):
    screen.blit(IMAGE_BACKGROUND, (0, 0))
    for player in players:
        player.draw(screen)
    for pipe in pipes:
        pipe.draw(screen)

    text = FONT_POINTS.render(f"Pontuação: {points}", True, (255, 255, 255))
    screen.blit(text, (SCREEN_WIDTH - 10 - text.get_width(), 10))
    base.draw(screen)
    pygame.display.update()


def main():
    players = [Player(230, 250)]
    base = Base(650)
    pipes = [Pipe(700)]
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    points = 0
    watch = pygame.time.Clock()

    running = True
    while running:
        watch.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for player in players:
                        player.jump()
        for player in players:
            player.move()
        base.move()

        add_pipe = False
        remove_pipes = []
        for pipe in pipes:
            for i, player in enumerate(players):
                if pipe.collision(player):
                    players.pop(i)
                if not pipe.pipe_pass and player.x > pipe.x:
                    pipe.pipe_pass = True
                    add_pipe = True
            pipe.move()
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove_pipes.append(pipe)
        if add_pipe:
            points += 1
            pipes.append(Pipe(600))
        for pipe in remove_pipes:
            pipes.remove(pipe)

        for i, player in enumerate(players):
            if (player.y + player.image.get_height()) > base.y or player.y < 0:
                players.pop(i)
        draw_screen(screen, players, pipes, base, points)


if __name__ == '__main__':
    main()
