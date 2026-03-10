"""
Breakout - Brick breaker with power-ups and levels.
"""
import pygame
import random

pygame.init()
W, H = 800, 600
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Breakout")
clock = pygame.time.Clock()
FPS = 60

BRICK_W, BRICK_H = 64, 24
PADDLE_W, PADDLE_H = 100, 16
BALL_R = 8
COLORS = [(220, 60, 60), (60, 180, 80), (60, 100, 220), (200, 180, 50), (180, 80, 200)]


def main():
    font = pygame.font.SysFont("segoeui", 28)
    level = 1
    score = 0
    lives = 3
    paddle_x = W // 2 - PADDLE_W // 2
    paddle_y = H - 50
    ball_x, ball_y = W // 2, H - 80
    ball_vx = 5 * (1 if random.random() > 0.5 else -1)
    ball_vy = -5
    paddle_wide = False
    power_timer = 0
    bricks = []
    running = True

    def build_level():
        nonlocal bricks
        bricks = []
        rows = min(2 + level, 6)
        for row in range(rows):
            for col in range(W // BRICK_W):
                x = col * BRICK_W
                y = 60 + row * (BRICK_H + 4)
                bricks.append({"rect": pygame.Rect(x, y, BRICK_W - 2, BRICK_H - 2), "color": random.choice(COLORS)})

    build_level()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        if power_timer > 0:
            power_timer -= 1
        pw = PADDLE_W * 2 if (paddle_wide and power_timer > 0) else PADDLE_W
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle_x -= 10
        if keys[pygame.K_RIGHT]:
            paddle_x += 10
        paddle_x = max(0, min(W - pw, paddle_x))

        ball_x += ball_vx
        ball_y += ball_vy
        if ball_x <= BALL_R or ball_x >= W - BALL_R:
            ball_vx *= -1
        if ball_y <= BALL_R:
            ball_vy *= -1
        if ball_y >= H:
            lives -= 1
            if lives <= 0:
                running = False
            ball_x, ball_y = W // 2, H - 80
            ball_vx = 5 * (1 if random.random() > 0.5 else -1)
            ball_vy = -5
        # Paddle
        if ball_vy > 0 and paddle_y <= ball_y + BALL_R <= paddle_y + PADDLE_H and paddle_x <= ball_x <= paddle_x + pw:
            ball_vy = -abs(ball_vy)
            ball_y = paddle_y - BALL_R
            dx = (ball_x - (paddle_x + pw / 2)) / (pw / 2)
            ball_vx = dx * 6
        # Bricks
        for b in bricks[:]:
            if b["rect"].collidepoint(ball_x, ball_y):
                bricks.remove(b)
                score += 10
                ball_vy *= -1
                if random.random() < 0.15:
                    power_timer = 600
                    paddle_wide = True
                break

        if not bricks:
            level += 1
            score += 100
            build_level()
            ball_x, ball_y = W // 2, H - 80
            ball_vx = 5 * (1 if random.random() > 0.5 else -1)
            ball_vy = -5

        screen.fill((20, 20, 35))
        for b in bricks:
            pygame.draw.rect(screen, b["color"], b["rect"])
        pygame.draw.rect(screen, (100, 200, 255), (paddle_x, paddle_y, pw, PADDLE_H))
        pygame.draw.circle(screen, (255, 255, 100), (int(ball_x), int(ball_y)), BALL_R)
        screen.blit(font.render(f"Level {level}  Score: {score}  Lives: {lives}", True, (255, 255, 255)), (10, 10))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()
