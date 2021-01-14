import pygame
import threading
import time

DISPLAY_SIZE = (1024, 512)
pygame.init()
screen = pygame.display.set_mode(DISPLAY_SIZE)
start_game = True
player_sprite = pygame.sprite.Group()
world_sprite = pygame.sprite.Group()


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

    def __init__(self, group):
        super().__init__(group)
        self.image = Player.image
        self.rect = self.image.get_rect()
        self.velocity_walk = 16
        self.velocity_jump = 50
        self.map_pos = [1, 0]

        self.rect.x = 16
        self.rect.y = 390

    def next(self):
        self.rect.x = self.rect.x + self.velocity_walk
        return self.rect.x

    def back(self):
        self.rect.x = self.rect.x - self.velocity_walk
        return self.rect.x

    def update(self):
        self.rect = self.rect


player = Player(player_sprite)

max_map_pos = [61, 27]
lvl_board = None


def canGo(pos):
    count = 0
    for i in range(2):
        for j in range(4):
            if lvl_board[pos[1] + j][pos[0] + i] == '/':
                count += 1
    if count == 8:
        return True
    return False


def map_generator(lvl):
    global lvl_board
    with open(lvl, mode='r', encoding='utf8') as f:
        f = f.read()
        lvl_board = f.replace(' ', '/').split('\n')
        lvl_board.reverse()
        for line in enumerate(f.split('\n')):
            if len(line[1]) != 0:
                for i in range(len(line[1])):
                    if line[1][i] == '0':
                        block = pygame.sprite.Sprite(world_sprite)
                        block.image = load_image('block.png')
                        block.rect = block.image.get_rect()
                        block.rect.x = 16 * i
                        block.rect.y = int(line[0]) * 16

    grass = pygame.sprite.Sprite(world_sprite)
    grass.image = load_image('grass-ground.png')
    grass.rect = grass.image.get_rect()
    grass.rect.x = 0
    grass.rect.y = 448


map_generator('lvl1.txt')

clock = pygame.time.Clock()
while start_game:

    dt = clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            start_game = False

    screen.fill((93, 148, 251))

    player_sprite.draw(screen)
    world_sprite.draw(screen)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_d] and player.map_pos[0] + 1 <= max_map_pos[0]:
        if canGo([player.map_pos[0] + 1, player.map_pos[1]]):
            player.map_pos[0] += 1
            player.next()

    if keys[pygame.K_a] and player.map_pos[0] - 1 >= 1:
        if canGo([player.map_pos[0] - 1, player.map_pos[1]]):
            player.map_pos[0] -= 1
            player.back()

    pygame.display.flip()
pygame.quit()
