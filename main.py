import pygame
import time

DISPLAY_SIZE = (1024, 512)
MAX_MAP_POS = (61, 27)
SG = True
isJump = False
isJumpCounter = 0
JumpTime = 0
lvl_board = list()

pygame.init()

screen = pygame.display.set_mode(DISPLAY_SIZE)
player_sprite = pygame.sprite.Group()
world_sprite = pygame.sprite.Group()
bullet_sprite = pygame.sprite.Group()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, map_pos, group):
        super().__init__(group)
        self.map_pos = [map_pos[0] + 1, map_pos[1] + 1]
        self.image = pygame.Surface((10, 5))
        self.image.fill(color=(255, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.x = self.map_pos[0] * 16
        self.rect.y = 432 - self.map_pos[1] * 16
        print(self.rect.y)
        self.speedx = 16

    def update(self):
        if lvl_board[bul.map_pos[1]][self.map_pos[0] + 1] == '/':
            self.rect.x += bul.speedx
            self.map_pos[0] += 1
        else:
            self.kill()


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
        self.map_pos = [1, 0]

        self.rect.x = 16
        self.rect.y = 390

    def next(self):
        self.rect.x = self.rect.x + self.velocity_walk
        return self.rect.x

    def back(self):
        self.rect.x = self.rect.x - self.velocity_walk
        return self.rect.x

    def gravit(self):
        self.rect.y = self.rect.y + 16
        self.map_pos[1] = self.map_pos[1] - 1

    def jump(self):
        self.rect.y = self.rect.y - 32

    def update(self):
        self.rect = self.rect


player = Player(player_sprite)


def canGo(pos):
    count = 0
    for i in range(2):
        for j in range(4):
            if lvl_board[pos[1] + j][pos[0] + i] == '/':
                count += 1
    if count == 8:
        return True
    return False


def canJump(pos):
    if MAX_MAP_POS[1] > pos[1] + 5:
        if lvl_board[pos[1] + 5][pos[0]] == '/':
            if lvl_board[pos[1] + 5][pos[0] + 1] == '/':
                return True
    return False


def checkGrav(pos):
    if pos[1] != 0:
        if lvl_board[pos[1] - 1][pos[0]] == '/':
            if lvl_board[pos[1] - 1][pos[0] + 1] == '/':
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


def lvl_loader(lvl):
    global isJump, isJumpCounter, JumpTime, lvl_board
    isJump = False
    isJumpCounter = 0
    JumpTime = 0

    lvl_board = list()
    map_generator(lvl)


lvl_loader('lvl1.txt')

bullet = []

clock = pygame.time.Clock()
while SG:
    dt = clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            SG = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not isJump:
                if JumpTime <= time.time():
                    isJumpCounter = 0
                    isJump = True
            if event.key == pygame.K_h:
                bullet.append(Bullet(player.map_pos, bullet_sprite))

    screen.fill((93, 148, 251))
    player_sprite.draw(screen)
    world_sprite.draw(screen)
    bullet_sprite.draw(screen)

    for bul in bullet:
        bul.update()

    keys = pygame.key.get_pressed()
    if isJump and isJumpCounter != 3:
        if canJump(player.map_pos):
            player.map_pos[1] += 2
            player.jump()
            isJumpCounter += 1
            if isJumpCounter == 3:
                isJump = False
                JumpTime = time.time() + 0.35
        else:
            isJump = False
            JumpTime = time.time() + 0.35

    if keys[pygame.K_d] and player.map_pos[0] + 1 <= MAX_MAP_POS[0]:
        if canGo([player.map_pos[0] + 1, player.map_pos[1]]):
            player.map_pos[0] += 1
            player.next()

    if keys[pygame.K_a] and player.map_pos[0] - 1 >= 1:
        if canGo([player.map_pos[0] - 1, player.map_pos[1]]):
            player.map_pos[0] -= 1
            player.back()

    if checkGrav(player.map_pos) and not isJump:
        player.gravit()

    pygame.display.flip()
pygame.quit()
