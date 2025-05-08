import pygame
import sys
import random

pygame.init()

# Settings
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
WIDTH = CELL_SIZE * GRID_WIDTH
HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 10  # Will be set by difficulty menu

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED   = (255, 0, 0)
WHITE = (255, 255, 255)
GRAY  = (100, 100, 100)
BLUE  = (0, 0, 255)
BROWN = (139, 69, 19)  # Wall color

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

snake = [(5, 5), (4, 5), (3, 5)]
direction = (1, 0)
score = 0
game_started = False
walls = []
game_paused = False  # Removed the pause on game start

blink_timer = 0
blink_interval = 2000  # ms
blink_duration = 200   # ms

class Food:
    def __init__(self):
        self.respawn()

    def respawn(self):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in snake and pos not in walls:
                break
        self.position = pos
        roll = random.random()
        if roll < 0.6:
            self.points = 1
            self.size = 10
        elif roll < 0.9:
            self.points = 3
            self.size = 16
        else:
            self.points = 5
            self.size = 20

    def draw(self):
        x, y = self.position
        cx = x * CELL_SIZE + CELL_SIZE // 2
        cy = y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, RED, (cx, cy), self.size // 2)

food = Food()

def draw_cell(pos, color):
    x, y = pos
    pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_eyes(pos, direction, blinking=False):
    if blinking: return
    x, y = pos
    cx = x * CELL_SIZE
    cy = y * CELL_SIZE
    eye_radius = 3
    if direction == (1, 0):     offsets = [(12, 5), (12, 15)]
    elif direction == (-1, 0):  offsets = [(4, 5), (4, 15)]
    elif direction == (0, -1):  offsets = [(5, 4), (15, 4)]
    else:                       offsets = [(5, 12), (15, 12)]
    for ox, oy in offsets:
        pygame.draw.circle(screen, WHITE, (cx + ox, cy + oy), eye_radius)

def reset_game():
    global snake, direction, score, food, blink_timer, walls
    snake[:] = [(5, 5), (4, 5), (3, 5)]
    direction = (1, 0)
    score = 0
    food.respawn()
    blink_timer = 0
    walls = []
    

def draw_button(text, rect, active):
    pygame.draw.rect(screen, BLUE if active else GRAY, rect)
    label = font.render(text, True, WHITE)
    screen.blit(label, (rect.x + 15, rect.y + 5))

def main_menu():
    title_font = pygame.font.SysFont("Arial", 36)
    start_rect = pygame.Rect(WIDTH//2 - 60, HEIGHT//2 - 30, 120, 40)
    quit_rect = pygame.Rect(WIDTH//2 - 60, HEIGHT//2 + 30, 120, 40)

    while True:
        screen.fill(BLACK)
        title = title_font.render("Snake Game", True, GREEN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 100))

        mx, my = pygame.mouse.get_pos()
        draw_button("   START", start_rect, start_rect.collidepoint(mx, my))
        draw_button("    QUIT", quit_rect, quit_rect.collidepoint(mx, my))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_rect.collidepoint(event.pos):
                    return
                elif quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(60)

def difficulty_menu():
    global FPS, game_started, walls
    easy_rect = pygame.Rect(WIDTH//2 - 60, HEIGHT//2 - 90, 120, 40)
    normal_rect = pygame.Rect(WIDTH//2 - 60, HEIGHT//2 - 30, 120, 40)
    hard_rect = pygame.Rect(WIDTH//2 - 60, HEIGHT//2 + 30, 120, 40)

    while not game_started:
        screen.fill(BLACK)
        title = font.render("Choose Difficulty", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 140))

        mx, my = pygame.mouse.get_pos()
        draw_button("     Easy", easy_rect, easy_rect.collidepoint(mx, my))
        draw_button("   Normal", normal_rect, normal_rect.collidepoint(mx, my))
        draw_button("     Hard", hard_rect, hard_rect.collidepoint(mx, my))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if easy_rect.collidepoint(event.pos): FPS = 7; game_started = True; walls = generate_walls('easy')
                elif normal_rect.collidepoint(event.pos): FPS = 12; game_started = True; walls = generate_walls('normal')
                elif hard_rect.collidepoint(event.pos): FPS = 18; game_started = True; walls = generate_walls('hard')

        pygame.display.flip()
        clock.tick(60)

def game_over_screen():
    restart_rect = pygame.Rect(WIDTH//2 - 70, HEIGHT//2, 140, 40)
    font_large = pygame.font.SysFont("Arial", 36)
    while True:
        screen.fill(BLACK)
        over = font_large.render("Game Over!", True, RED)
        screen.blit(over, (WIDTH//2 - over.get_width()//2, HEIGHT//2 - 100))
        draw_button("  Main Menu", restart_rect, restart_rect.collidepoint(*pygame.mouse.get_pos()))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_rect.collidepoint(event.pos):
                    main_menu()  # main menu

        pygame.display.flip()
        clock.tick(60)

def generate_walls(difficulty):
    if difficulty == 'easy':
        return [(i, 7) for i in range(5, 10)]
    elif difficulty == 'normal':
        return [(i, 7) for i in range(7, 15)] + [(10, i) for i in range(10, 15)]
    else:
        return [(i, 7) for i in range(7, 20)] + [(10, i) for i in range(10, 20)] + [(i, 15) for i in range(10, 20)]

def draw_walls():
    for wall in walls:
        pygame.draw.rect(screen, BROWN, (wall[0]*CELL_SIZE, wall[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

# ---- Game Startup Sequence ----
main_menu()
difficulty_menu()
game_paused = False  # No pause at start

# ---- Main Game Loop ----
while True:
    dt = clock.tick(FPS)
    blink_timer += dt
    blinking = blink_timer % blink_interval < blink_duration

    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and direction != (0, 1): direction = (0, -1)
    if keys[pygame.K_DOWN] and direction != (0, -1): direction = (0, 1)
    if keys[pygame.K_LEFT] and direction != (1, 0): direction = (-1, 0)
    if keys[pygame.K_RIGHT] and direction != (-1, 0): direction = (1, 0)

    new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
    snake.insert(0, new_head)

    if (new_head in snake[1:] or new_head in walls or
        new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
        new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
        game_over_screen()

    if new_head == food.position:
        score += food.points
        food.respawn()
    else:
        snake.pop()

    screen.fill(BLACK)
    food.draw()
    draw_walls()

    for idx, segment in enumerate(snake):
        fade = 255 - int((idx / len(snake)) * 150)
        color = (0, fade, 0)
        x, y = segment
        cx, cy = x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2
        if idx == 0:
            pygame.draw.circle(screen, color, (cx, cy), CELL_SIZE // 2)
            draw_eyes(segment, direction, blinking)
        elif idx == len(snake) - 1:
            pygame.draw.rect(screen, (0, 100, 0), (x*CELL_SIZE+2, y*CELL_SIZE+2, CELL_SIZE-4, CELL_SIZE-4))
        else:
            pygame.draw.rect(screen, color, (x*CELL_SIZE+1, y*CELL_SIZE+1, CELL_SIZE-2, CELL_SIZE-2))

    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    pygame.display.flip()
