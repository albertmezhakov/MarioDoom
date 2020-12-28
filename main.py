import pygame
import os
import sys
import time

DISPLAY_SIZE = (1280, 720)
pygame.init()
pygame.display.set_caption('Mario and Doom')
screen = pygame.display.set_mode(DISPLAY_SIZE)
start_game = True
player_sprite = pygame.sprite.Group()
world_sprite = pygame.sprite.Group()


# def map_generator()

def load_image(image_path, colorkey=None):
    result = pygame.image.load(image_path)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = result.get_at((0, 0))
        result.set_colorkey(colorkey)
    else:
        result.convert_alpha()
    return result


class Player(pygame.sprite.Sprite):
    image = load_image("player.png", -1)

    def __init__(self, group, minX, maxX):
        super().__init__(group)
        self.image = Player.image
        self.rect = self.image.get_rect()
        self.velocity_walk = 20
        self.velocity_jump = 50
        # self.minX = minX
        # self.maxX = maxX
        self.rect.x = 50
        self.rect.y = 300
        self.ammo_1 = 12  # Дробь
        self.ammo_2 = 60  # Пуля
        self.ammo_3 = 150  # Энергия
        self.ammo_4 = 3  # Топливо
        self.ammo_5 = 3  # Снаряды для BFG
        self.ammo_6 = 3  # Заряды для горнила
        self.gun = None
        self.isJumpXY = None
        self.isJump = True
        self.isJumpUp_old = True
        self.jump_time = None

    def next(self, dt):
        self.rect.x = self.rect.x + self.velocity_walk * dt / 60
        return self.rect.x

    def back(self, dt):
        self.rect.x = self.rect.x - self.velocity_walk * dt / 60
        return self.rect.x

    def jump(self, dt):
        if self.jump_time is None or self.jump_time + 3 <= time.time():
            if self.isJump:
                self.isJumpXY = (self.rect.x, self.rect.y)
                self.isJump = False
                self.isJumpUp_old = True

            if self.isJumpXY[1] - self.velocity_jump < self.rect.y and self.isJumpUp_old:
                self.rect.y = self.rect.y - self.velocity_jump * dt / 60

            elif self.isJumpXY[1] + self.velocity_jump > self.rect.y:
                self.rect.y = self.rect.y + self.velocity_jump * dt / 60
                self.isJumpUp_old = False
            else:
                self.isJump = True
                self.jump_time = time.time()

    def shoot(self):
        if self.gun.isShoot:
            pass

    def update(self):
        self.rect = self.rect


player = Player(player_sprite, 0, 3000)
clock = pygame.time.Clock()

while start_game:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            start_game = False

    screen.fill((93, 148, 251))

    keys = pygame.key.get_pressed()

    player_sprite.draw(screen)
    if keys[pygame.K_d]:
        player.next(dt)
    if keys[pygame.K_a]:
        player.back(dt)
    if keys[pygame.K_SPACE]:
        player.jump(dt)
    #
    # for x in range(col + 1):
    #     pygame.draw.line(screen, (255, 255, 255), (margin + height * x, margin),
    #                      (margin + height * x, DISPLAY_SIZE[1] - margin), width=1)
    #
    # for y in range(row + 1):
    #     pygame.draw.line(screen, (255, 255, 255), (margin, margin + weight * y),
    #                      (DISPLAY_SIZE[0] - margin, margin + weight * y), width=1)
    # pygame.draw.rect(screen, pygame)
    pygame.display.flip()
pygame.quit()
