"""
Snake Classic - Grow by eating, don't hit walls or yourself.
"""
import pygame
import random

pygame.init()
CELL = 24
COLS, ROWS = 24, 18
W, H = COLS * CELL, ROWS * CELL
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Snake Classic")
clock = pygame.time.Clock()
FPS = 12

snake = [(COLS // 2, ROWS // 2)]
dx, dy = 1, 0
food = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
score = 0
game_over = False


def main():
    global snake, dx, dy, food, score, game_over
    font = pygame.font.SysFont("segoeui", 22)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over and event.key == pygame.K_SPACE:
                    snake = [(COLS // 2, ROWS // 2)]
                    dx, dy = 1, 0
                    food = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
                    score = 0
                    game_over = False
                elif not game_over:
                    if event.key == pygame.K_UP and dy != 1:
                        dx, dy = 0, -1
                    if event.key == pygame.K_DOWN and dy != -1:
                        dx, dy = 0, 1
                    if event.key == pygame.K_LEFT and dx != 1:
                        dx, dy = -1, 0
                    if event.key == pygame.K_RIGHT and dx != -1:
                        dx, dy = 1, 0

        if not game_over:
            head = (snake[0][0] + dx, snake[0][1] + dy)
            if head[0] < 0 or head[0] >= COLS or head[1] < 0 or head[1] >= ROWS:
                game_over = True
            elif head in snake:
                game_over = True
            else:
                snake.insert(0, head)
                if head == food:
                    score += 10
                    while food in snake:
                        food = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
                else:
                    snake.pop()

        screen.fill((15, 25, 20))
        for i, (sx, sy) in enumerate(snake):
            c = (80, 200, 120) if i == 0 else (60, 160, 90)
            pygame.draw.rect(screen, c, (sx * CELL + 1, sy * CELL + 1, CELL - 2, CELL - 2))
        pygame.draw.rect(screen, (255, 80, 80), (food[0] * CELL + 4, food[1] * CELL + 4, CELL - 8, CELL - 8))
        screen.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (10, 5))
        if game_over:
            screen.blit(font.render("Game Over - SPACE to restart", True, (255, 150, 150)), (W // 2 - 140, H // 2 - 15))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()
