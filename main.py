import pygame

print(1)
print(2)
DISPLAY_SIZE = (1280, 720)
col = 32
row = 30
margin = 40
height = (DISPLAY_SIZE[0] - margin * 2) / 16
weight = (DISPLAY_SIZE[1] - margin * 2) / 30
running = True
x_pos = 0
v = 20


pygame.init()
pygame.display.set_caption('Mario and Doom')
screen = pygame.display.set_mode(DISPLAY_SIZE)
board = [['0'] * row] * col

clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print(2)
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                margin += 10
            elif event.key == pygame.K_a:
                margin -= 10
    screen.fill((0, 0, 0))

    for x in range(col + 1):
        pygame.draw.line(screen, (255, 255, 255), (margin + height * x, margin),
                         (margin + height * x, DISPLAY_SIZE[1] - margin), width=1)

    for y in range(row + 1):
        pygame.draw.line(screen, (255, 255, 255), (margin, margin + weight * y),
                         (DISPLAY_SIZE[0] - margin, margin + weight * y), width=1)
    pygame.draw.rect(screen, pygame)
    clock.tick(10)
    pygame.display.flip()
pygame.quit()
