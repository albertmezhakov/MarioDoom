import pygame
import time

DISPLAY_SIZE = (1024, 512)
MAX_MAP_POS = (61, 27)
SG = True

lvl_board = list()
bullet = list()
mob_list = dict()
mob_counter = 0
last_lvl = 'lvl1.txt'

pygame.init()

screen = pygame.display.set_mode(DISPLAY_SIZE)
player_sprite = pygame.sprite.Group()
world_sprite = pygame.sprite.Group()
bullet_sprite = pygame.sprite.Group()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, map_pos, group):
        super().__init__(group)
        self.map_pos = [map_pos[0] + 1, map_pos[1] + 2]
        self.image = pygame.Surface((10, 5))
        self.image.fill(color=(255, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.x = self.map_pos[0] * 16
        self.rect.y = 432 - self.map_pos[1] * 16
        self.speedx = 16
        self.right = player.right

    def update(self):
        global mob_counter
        if self.right:
            if lvl_board[self.map_pos[1] - 2][self.map_pos[0] + 1] != '1':
                if lvl_board[bul.map_pos[1]][self.map_pos[0] + 1] == '/':
                    self.rect.x += bul.speedx
                    self.map_pos[0] += 1
                else:
                    self.kill()
            else:
                try:
                    mob_list[f'{str(self.map_pos[0] + 1)}x{str(self.map_pos[1] - 2)}'].kill()
                    del mob_list[f'{str(self.map_pos[0] + 1)}x{str(self.map_pos[1] - 2)}']
                    mob_counter -= 1
                    bullet.pop(bullet.index(self))
                    self.kill()

                except KeyError:
                    self.rect.x += bul.speedx
                    self.map_pos[0] += 1
        else:
            if lvl_board[self.map_pos[1] - 2][self.map_pos[0] - 1] != '1':
                if lvl_board[self.map_pos[1] - 2][self.map_pos[0] - 1] == '/':
                    self.rect.x -= bul.speedx
                    self.map_pos[0] -= 1
                else:
                    self.kill()
            else:
                try:
                    mob_list[f'{str(self.map_pos[0] - 1)}x{str(self.map_pos[1] - 2)}'].kill()
                    del mob_list[f'{str(self.map_pos[0] - 1)}x{str(self.map_pos[1] - 2)}']
                    mob_counter -= 1
                    bullet.pop(bullet.index(self))
                    self.kill()

                except KeyError:
                    self.rect.x -= bul.speedx
                    self.map_pos[0] -= 1


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
    image_right = load_image("player_right.png", -1)
    image_left = load_image("player_left.png", -1)

    def __init__(self, group):
        super().__init__(group)
        self.image = Player.image_right
        self.rect = self.image.get_rect()
        self.velocity_walk = 16
        self.map_pos = [1, 0]
        self.isJump = False
        self.isJumpCounter = 0
        self.jumpTime = 0
        self.rect.x = 16
        self.rect.y = 390
        self.right = True

    def next(self):
        self.right = True
        self.rect.x = self.rect.x + self.velocity_walk
        return self.rect.x

    def back(self):
        self.right = False
        self.rect.x = self.rect.x - self.velocity_walk
        return self.rect.x

    def gravit(self):
        self.rect.y = self.rect.y + 16
        self.map_pos[1] = self.map_pos[1] - 1

    def jump(self):
        self.rect.y = self.rect.y - 32

    def update(self):
        self.image = Player.image_right if self.right else Player.image_left


player = Player(player_sprite)


def canGo(pos):
    count = 0
    for i in range(2):
        for j in range(4):
            if lvl_board[pos[1] + j][pos[0] + i] == '/':
                count += 1
            elif lvl_board[pos[1] + j][pos[0] + i] == '1':
                try:
                    mob_list[f'{str(pos[0] + i)}x{str(pos[1] + j)}'].kill()
                    lvl_loader(last_lvl)
                except KeyError:
                    count += 1
            elif lvl_board[pos[1] + j][pos[0] + i] == '-':
                count += 1
            elif lvl_board[pos[1] + j][pos[0] + i] == '+':
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
    global lvl_board, mob_counter
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
                    elif line[1][i] == '1':
                        mob = pygame.sprite.Sprite(world_sprite)
                        mob.image = load_image('3x1_mob.png', -1)
                        mob.rect = mob.image.get_rect()
                        mob.rect.x = 16 * i
                        mob.rect.y = (int(line[0]) - 2) * 16
                        mob_counter += 1
                        mob_list[f'{str(i)}x{str(27 - line[0])}'] = mob
                    elif line[1][i] == '-':
                        grass_dec_min = pygame.sprite.Sprite(world_sprite)
                        grass_dec_min.image = load_image('grass_min.png', -1)
                        grass_dec_min.rect = grass_dec_min.image.get_rect()
                        grass_dec_min.rect.x = 16 * i
                        grass_dec_min.rect.y = (int(line[0])) * 16
                    elif line[1][i] == '+':
                        grass_dec_max = pygame.sprite.Sprite(world_sprite)
                        grass_dec_max.image = load_image('grass_max.png', -1)
                        grass_dec_max.rect = mob.image.get_rect()
                        grass_dec_max.rect.x = 16 * i
                        grass_dec_max.rect.y = (int(line[0])) * 16

    grass = pygame.sprite.Sprite(world_sprite)
    grass.image = load_image('grass-ground.png')
    grass.rect = grass.image.get_rect()
    grass.rect.x = 0
    grass.rect.y = 448


def lvl_loader(lvl):
    global lvl_board, player, last_lvl, mob_counter
    global world_sprite, bullet_sprite, player_sprite
    last_lvl = lvl
    player.isJump = False
    player.isJumpCounter = 0
    player.jumpTime = 0
    mob_counter = 0
    lvl_board = list()

    player_sprite = pygame.sprite.Group()
    world_sprite = pygame.sprite.Group()
    bullet_sprite = pygame.sprite.Group()
    player.kill()

    map_generator(lvl)
    player = Player(player_sprite)


lvl_loader('lvl1.txt')

clock = pygame.time.Clock()
while SG:
    print(mob_counter)
    dt = clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            SG = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not player.isJump:
                if player.jumpTime <= time.time():
                    player.isJumpCounter = 0
                    player.isJump = True
            if event.key == pygame.K_j and not player.isJump:
                bullet.append(Bullet(player.map_pos, bullet_sprite))

    screen.fill((93, 148, 251))
    player_sprite.draw(screen)
    world_sprite.draw(screen)
    bullet_sprite.draw(screen)
    player.update()
    for bul in bullet:
        bul.update()

    # if mob_counter == 0:
    #     SG = False

    keys = pygame.key.get_pressed()
    if player.isJump and player.isJumpCounter != 3:
        if canJump(player.map_pos):
            player.map_pos[1] += 2
            player.jump()
            player.isJumpCounter += 1
            if player.isJumpCounter == 3:
                player.isJump = False
                player.umpTime = time.time() + 0.35
        else:
            player.isJump = False
            player.jumpTime = time.time() + 0.35

    if keys[pygame.K_d] and player.map_pos[0] + 1 <= MAX_MAP_POS[0]:
        if canGo([player.map_pos[0] + 1, player.map_pos[1]]):
            player.map_pos[0] += 1
            player.next()

    if keys[pygame.K_a] and player.map_pos[0] - 1 >= 1:
        if canGo([player.map_pos[0] - 1, player.map_pos[1]]):
            player.map_pos[0] -= 1
            player.back()

    if checkGrav(player.map_pos) and not player.isJump:
        player.gravit()

    pygame.display.flip()
pygame.quit()
