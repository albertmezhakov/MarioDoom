import pygame
import time
import sqlite3

DISPLAY_SIZE = (1024, 512)
MAX_MAP_POS = (61, 27)

pygame.init()
pygame.mixer.init()
last_lvl = 1
max_lvl = 2
difficult = 1
menu = True

screen = pygame.display.set_mode(DISPLAY_SIZE)


def load_image(image_path, colorkey=None):
    result = pygame.image.load(image_path)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = result.get_at((0, 0))
        result.set_colorkey(colorkey)
    else:
        result.convert_alpha()
    return result


class World:

    def __init__(self, difficult):
        self.map = list()
        self.bullet_list = list()
        self.mob_list = dict()
        self.mob_counter = len(self.mob_list)
        self.name_lvl = ''
        self.allow_block = ['/', '-', '+']
        self.difficult = difficult

        self.player_sprite = pygame.sprite.Group()
        self.world_sprite = pygame.sprite.Group()
        self.bullet_sprite = pygame.sprite.Group()
        self.mob_sprite = pygame.sprite.Group()
        self.blur_sprite = pygame.sprite.Group()

    def checkGravity(self):
        if self.player.map_pos[1] != 0:
            if self.map[self.player.map_pos[1] - 1][
                self.player.map_pos[0]] in self.allow_block:
                if self.map[self.player.map_pos[1] - 1][
                    self.player.map_pos[0] + 1] in self.allow_block:
                    return True
        return False

    def checkAll(self):
        global world, player, last_lvl, menu
        if self.checkGravity() and not self.player.isJump:
            player.gravity()
        if self.mob_counter == 0:
            last_lvl += 1
            if last_lvl <= max_lvl:
                world = World(difficult)
                player = Player(world.player_sprite)
                world.setPlayer(player)
                world.mapGenerator(f'data/lvl{last_lvl}.txt')
                with sqlite3.connect('data/mariodom.db') as con:
                    con.cursor().execute(f'UPDATE data SET lvl = {last_lvl} WHERE id = 1')
            else:
                last_lvl = 1
                with sqlite3.connect('data/mariodom.db') as con:
                    con.cursor().execute(f'UPDATE data SET lvl = {last_lvl} WHERE id = 1')
                menu = True
                pause = True
                pygame.mixer.music.stop()
        for bullet in self.bullet_list:
            bullet.update()
        for mob_key in self.mob_list:
            self.mob_list[mob_key].update()
        self.player.update()

    def mapGenerator(self, lvl):
        with open(lvl, mode='r', encoding='utf8') as f:
            f = f.read()
            lvl_board_temp = f.replace(' ', '/').split('\n')
            lvl_board_temp.reverse()
            self.map = list(map(lambda x: list(x), lvl_board_temp))

            for line in enumerate(f.split('\n')):
                if len(line[1]) != 0:
                    for i in range(len(line[1])):
                        if line[1][i] == '0':
                            block = pygame.sprite.Sprite(self.world_sprite)
                            block.image = load_image('assets/sprite/block.png')
                            block.rect = block.image.get_rect()
                            block.rect.x = 16 * i
                            block.rect.y = int(line[0]) * 16
                        elif line[1][i] == '1':

                            self.mob_counter += 1
                            self.mob_list[f'{str(i)}x{str(27 - line[0])}'] = MobPython(i, (
                                    int(line[0]) - 2), self.difficult)
                        elif line[1][i] == '-':
                            grass_dec_min = pygame.sprite.Sprite(self.world_sprite)
                            grass_dec_min.image = load_image('assets/sprite/grass_min.png', -1)
                            grass_dec_min.rect = grass_dec_min.image.get_rect()
                            grass_dec_min.rect.x = 16 * i
                            grass_dec_min.rect.y = (int(line[0])) * 16
                        elif line[1][i] == '+':
                            grass_dec_max = pygame.sprite.Sprite(self.world_sprite)
                            grass_dec_max.image = load_image('assets/sprite/grass_max.png', -1)
                            grass_dec_max.rect = grass_dec_max.image.get_rect()
                            grass_dec_max.rect.x = 16 * i
                            grass_dec_max.rect.y = (int(line[0])) * 16
        self.mob_counter = len(self.mob_list)

        grass = pygame.sprite.Sprite(self.world_sprite)
        grass.image = load_image('assets/sprite/grass-ground.png')
        grass.rect = grass.image.get_rect()
        grass.rect.x = 0
        grass.rect.y = 448

    def setPlayer(self, player):
        self.player = player


class Bullet(pygame.sprite.Sprite):
    def __init__(self, map_pos, group):
        super().__init__(group)
        self.map_pos = [map_pos[0] + 1, map_pos[1] + 2]
        self.right = player.right
        self.ban_block = ['0']
        self.image = pygame.Surface((10, 5))
        self.image.fill(color=(255, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.x = self.map_pos[0] * 16
        self.rect.y = 432 - self.map_pos[1] * 16
        self.speedx = 16

    def update(self):
        if self.right:
            for i in range(4):
                if i == 3:
                    self.rect.x += self.speedx
                    self.map_pos[0] += 1
                    break
                elif world.map[self.map_pos[1] - i][self.map_pos[0] + 1] == '1':
                    world.mob_list[
                        f'{str(self.map_pos[0] + 1)}x{str(self.map_pos[1] - i)}'].damage(
                        [self.map_pos[1] - i, self.map_pos[0] + 1])

                    world.bullet_list.pop(world.bullet_list.index(self)).kill()
                    break
                elif world.map[self.map_pos[1]][self.map_pos[0] + 1] in self.ban_block:
                    world.bullet_list.pop(world.bullet_list.index(self)).kill()
                    break
                # # -----------
                # elif [self.map_pos[0] + 1, self.map_pos[1] - i] == world.player.map_pos:
                #     world.player.damage()
                #     world.bullet_list.pop(world.bullet_list.index(self)).kill()
                #     break
                # -----------
        else:
            for i in range(4):
                if i == 3:
                    self.rect.x -= self.speedx
                    self.map_pos[0] -= 1
                    break
                elif world.map[self.map_pos[1] - i][self.map_pos[0] - 1] == '1':
                    world.mob_list[
                        f'{str(self.map_pos[0] - 1)}x{str(self.map_pos[1] - i)}'].damage(
                        [self.map_pos[1] - i, self.map_pos[0] - 1])

                    world.bullet_list.pop(world.bullet_list.index(self)).kill()
                    break
                elif world.map[self.map_pos[1]][self.map_pos[0] - 1] in self.ban_block:
                    world.bullet_list.pop(world.bullet_list.index(self)).kill()
                    break
                # # -----------
                # elif [self.map_pos[0] - 1, self.map_pos[1] - i] == world.player.map_pos:
                #     world.player.damage()
                #     world.bullet_list.pop(world.bullet_list.index(self)).kill()
                #     break
                # # -----------


class MobPython(pygame.sprite.Sprite):
    image = load_image("assets/sprite/3x1_mob.png", -1)
    image_dead = load_image("assets/sprite/3x1_mob_dead.png", -1)

    def __init__(self, x, y, difficult):
        super().__init__(world.mob_sprite)
        self.image = load_image('assets/sprite/3x1_mob.png', -1)
        self.rect = self.image.get_rect()
        self.pos = [x, 27 - y - 2]
        self.rect.x = 16 * x
        self.rect.y = y * 16
        self.base_hp = 1 * difficult
        self.hp = 1 * difficult
        self.dead = False
        self.time = time.time()

    def damage(self, map_pos):
        if self.hp - 1 != 0:
            self.hp -= 1
        else:
            self.image = self.image_dead
            world.map[map_pos[0]][map_pos[1]] = '/'
            world.mob_counter -= 1
            self.dead = True

    def update(self):
        if not self.dead:
            pygame.draw.rect(screen, (0, 230, 0),
                             pygame.Rect(self.rect.x, self.rect.y - 10,
                                         (16 / self.base_hp) * self.hp, 6))
        # if self.pos[0] - 5 <= world.player.map_pos[0] <= self.pos[0] + 5 and not self.dead:
        #     if self.time < time.time():
        #         if world.player.map_pos[0] < self.pos[0] and world.player.map_pos[1] == self.pos[1]:
        #             bul = Bullet([self.pos[0] - 1, self.pos[1]], world.bullet_sprite)
        #             bul.right = False
        #             world.bullet_list.append(bul)
        #             self.time = time.time() + 1 / difficult
        #         elif world.player.map_pos[0] > self.pos[0] and world.player.map_pos[1] == self.pos[1]:
        #             bul = Bullet(self.pos, world.bullet_sprite)
        #             bul.right = True
        #             world.bullet_list.append(bul)
        #             self.time = time.time() + 1 / difficult


class Player(pygame.sprite.Sprite):
    image_right = [load_image("assets/sprite/animated_player/player_anim1_right.png", -1),
                   load_image("assets/sprite/animated_player/player_anim2_right.png", -1)]
    image_left = [load_image("assets/sprite/animated_player/player_anim1_left.png", -1),
                  load_image("assets/sprite/animated_player/player_anim2_left.png", -1)]

    def __init__(self, group):
        super().__init__(group)
        self.player = None
        self.image = Player.image_right[0]
        self.rect = self.image.get_rect()
        self.velocity_walk = 16
        self.map_pos = [1, 0]
        self.isJump = False
        self.isJumpCounter = 0
        self.jumpTime = 0
        self.rect.x = 16
        self.rect.y = 390
        self.right = True
        self.allow_block = ['/', '-', '+']
        self.cur_frame = 0
        # self.hp = 6 - difficult
        # self.base_hp = 6 - difficult
        # self.dead = False

    def _canGo(self, pos):
        global world, player
        count = 0
        for i in range(2):
            for j in range(4):
                if world.map[pos[1] + j][pos[0] + i] in self.allow_block:
                    count += 1
                elif world.map[pos[1] + j][pos[0] + i] == '1':
                    world = World(difficult)
                    player = Player(world.player_sprite)
                    world.setPlayer(player)
                    world.mapGenerator(f'data/lvl{last_lvl}.txt')
        if count == 8:
            return True
        return False

    def _canJump(self, pos):
        count = 0
        for i in range(2):
            for j in range(4, 6):
                if world.map[pos[1] + j][pos[0] + i] in self.allow_block:
                    count += 1
        if count == 4:
            return True
        return False

    def next(self):
        pos = [self.map_pos[0] + 1, self.map_pos[1]]

        if self._canGo(pos):
            self.right = True
            self.cur_frame = (self.cur_frame + 1) % 2
            self.image = self.image_right[self.cur_frame]
            self.map_pos[0] += 1
            self.rect.x = self.rect.x + self.velocity_walk

    def back(self):
        pos = [self.map_pos[0] - 1, self.map_pos[1]]

        if self._canGo(pos):
            self.right = False
            self.image = self.image_left[self.cur_frame]
            self.map_pos[0] -= 1
            self.rect.x = self.rect.x - self.velocity_walk

    def gravity(self):
        self.rect.y = self.rect.y + 16
        self.map_pos[1] = self.map_pos[1] - 1

    def jump(self):
        self._canJump(self.map_pos)
        if self._canJump(self.map_pos):
            self.map_pos[1] += 2
            self.rect.y = self.rect.y - 32
            self.isJumpCounter += 1
            if self.isJumpCounter == 3:
                self.isJump = False
                self.isJumpCounter = 0
                self.jumpTime = time.time() + 0.35
        else:
            self.isJump = False

    # def damage(self):
    #     global world, player
    #     if self.hp - 1 != 0:
    #         self.hp -= 1
    #     else:
    #         print(1)
    #         world = World(difficult)
    #         player = Player(world.player_sprite)
    #         world.setPlayer(player)
    #         world.mapGenerator(f'data/lvl{last_lvl}.txt')
    #
    # def update(self):
    #     if not self.dead:
    #         pygame.draw.rect(screen, (0, 230, 0),
    #                          pygame.Rect(self.rect.x, self.rect.y - 16,
    #                                      (32 / self.base_hp) * self.hp, 6))


world = World
player = Player


def db():
    with sqlite3.connect('data/mariodom.db') as con:
        return con.cursor().execute('SELECT lvl, max_lvl FROM data').fetchall()


def start_game():
    pygame.init()
    global world, player, menu, difficult
    pause = False
    SG = True
    menu = True

    world = World(difficult)
    player = Player(world.player_sprite)
    world.setPlayer(player)
    world.mapGenerator(f'data/lvl{last_lvl}.txt')

    clock = pygame.time.Clock()
    blur = pygame.sprite.Sprite(world.blur_sprite)
    blur.image = load_image('assets/sprite/blur.png')
    blur.rect = blur.image.get_rect()
    blur.rect.x = 0
    blur.rect.y = 0

    dif = ['Легкий', 'Средний', 'Ад', 'Хуже К/Р']

    while SG:
        clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                SG = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not player.isJump and not pause and \
                        not menu:
                    if player.jumpTime <= time.time():
                        player.isJump = True
                elif event.key == pygame.K_SPACE and pause:
                    menu = True

                elif event.key == pygame.K_j and not player.isJump and not menu:
                    world.bullet_list.append(Bullet(world.player.map_pos, world.bullet_sprite))
                elif event.key == pygame.K_ESCAPE and not menu:
                    pause = not pause
                    pygame.mixer.music.pause() if pause else pygame.mixer.music.unpause()
                elif event.key == pygame.K_RIGHT and difficult < len(dif):
                    difficult += 1
                elif event.key == pygame.K_LEFT and difficult > 1:
                    difficult -= 1

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    pos = event.pos
                    if 445 <= pos[0] <= 445 + 134:
                        if 159 <= pos[1] <= 159 + 55:
                            pause = False
                            menu = False

                            world = World(difficult)
                            player = Player(world.player_sprite)
                            world.setPlayer(player)
                            world.mapGenerator(f'data/lvl{last_lvl}.txt')
                            blur = pygame.sprite.Sprite(world.blur_sprite)
                            blur.image = load_image('assets/sprite/blur.png')
                            blur.rect = blur.image.get_rect()
                            blur.rect.x = 0
                            blur.rect.y = 0
                            pygame.mixer.music.load('assets/music/background_music.mp3')
                            pygame.mixer.music.set_volume(0.3)
                            pygame.mixer.music.play(loops=-1)
                    if 447 <= pos[0] <= 447 + 130:
                        if 240 <= pos[1] <= 240 + 54:
                            SG = False

        if menu:
            screen.fill((93, 148, 251))
            font = pygame.font.Font(None, 50)

            text = font.render(f"Уровень : {last_lvl}", True, (100, 255, 100))
            screen.blit(text, (420, 110))

            text = font.render("Играть", True, (100, 255, 100))
            screen.blit(text, (455, 169))
            pygame.draw.rect(screen, (0, 255, 0), (445, 159, 134, 55), 1)

            text1 = font.render("Выйти", True, (100, 255, 100))
            screen.blit(text1, (457, 250))
            pygame.draw.rect(screen, (0, 255, 0), (447, 240, 130, 54), 1)

            text = font.render(f"< {dif[difficult - 1]} >", True, (100, 255, 100))
            if difficult == len(dif):
                text = font.render(f"< {dif[difficult - 1]}  ", True, (100, 255, 100))
            elif len(dif) > difficult > 1:
                text = font.render(f"< {dif[difficult - 1]} >", True, (100, 255, 100))
            else:
                text = font.render(f"  {dif[difficult - 1]} >", True, (100, 255, 100))
            text_x = DISPLAY_SIZE[0] // 2 - text.get_width() // 2
            text_y = DISPLAY_SIZE[1] // 2 - text.get_height() // 2 + 70
            screen.blit(text, (text_x, text_y))

            pygame.display.flip()
            continue

        if pause:
            screen.fill((93, 148, 251))
            world.mob_sprite.draw(screen)
            world.player_sprite.draw(screen)
            world.world_sprite.draw(screen)
            world.bullet_sprite.draw(screen)
            world.blur_sprite.draw(screen)
            font1 = pygame.font.Font(None, 50)
            font2 = pygame.font.Font(None, 30)
            text1 = font1.render("Игра приостановлена", True, (26, 26, 26))
            text2 = font2.render("Нажмите ESCAPE чтобы выйти", True, (26, 26, 26))
            text3 = font2.render("Нажмите SPACE чтобы перейти в меню", True, (26, 26, 26))
            screen.blit(text1, (328, 239))
            screen.blit(text2, (359, 276))
            screen.blit(text3, (318, 305))
            pygame.display.flip()
            continue

        screen.fill((93, 148, 251))
        world.player_sprite.draw(screen)
        world.world_sprite.draw(screen)
        world.bullet_sprite.draw(screen)
        world.mob_sprite.draw(screen)
        world.checkAll()

        keys = pygame.key.get_pressed()
        if world.player.isJump and world.player.isJumpCounter != 3:
            world.player.jump()

        if keys[pygame.K_d] and world.player.map_pos[0] + 1 <= MAX_MAP_POS[0]:
            world.player.next()

        if keys[pygame.K_a] and world.player.map_pos[0] - 1 >= 1:
            world.player.back()

        pygame.display.flip()


info = db()
last_lvl = info[0][0]
max_lvl = info[0][1]

start_game()
pygame.quit()
