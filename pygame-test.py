import pygame
import yaml

# Инициализация Pygame
pygame.init()

# Загрузка данных из YAML-файла
with open('old_schedule.yaml', 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)

# Настройки окна
screen_width = 1024
screen_height = 768
screen = pygame.display.set_mode((screen_width, screen_height)) #pygame.Fullscreen
pygame.display.set_caption("YAML Data Display")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Шрифт
font = pygame.font.Font(None, 36)  # Используем стандартный шрифт


def draw_text(text, x, y):
    text_surface = font.render(text, True, WHITE)
    screen.blit(text_surface, (x, y))


# Основной цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Заливка фона
    screen.fill(BLACK)
    draw_text("ололо", 50, 50)

    pygame.display.flip()

pygame.quit()