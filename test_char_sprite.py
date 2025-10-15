import pygame

pygame.init()
screen = pygame.display.set_mode((768, 480))
sheet = pygame.image.load('game/assets/images/sprites/buddie0_sheet.png').convert()
sheet.set_colorkey((0, 0, 0))

# Draw sheet
screen.blit(sheet, (0, 0))

# Draw grid
cell_size = 32
for x in range(0, 768, cell_size):
    pygame.draw.line(screen, (255, 0, 0), (x, 0), (x, 480))
for y in range(0, 480, cell_size):
    pygame.draw.line(screen, (0, 255, 0), (0, y), (768, y))

pygame.display.flip()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
