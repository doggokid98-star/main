"""
Flappy - Tap to fly through gaps. Addictive and polished.
"""
import pygame
import random

pygame.init()
W, H = 400, 600
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Flappy")
clock = pygame.time.Clock()
FPS = 60

GRAV = 0.35
FLAP = -7
GAP = 160
PIPE_W = 70
PIPE_SPEED = 3


def main():
    font = pygame.font.SysFont("segoeui", 36, bold=True)
    font_small = pygame.font.SysFont("segoeui", 24)
    bird_x = 80
    bird_y = H // 2
    bird_vy = 0
    pipes = []
    score = 0
    passed = set()
    game_over = False
    started = False
    pipe_timer = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if game_over:
                        bird_y = H // 2
                        bird_vy = 0
                        pipes.clear()
                        passed.clear()
                        score = 0
                        game_over = False
                        pipe_timer = 0
                    else:
                        bird_vy = FLAP
                        started = True

        if not game_over and started:
            bird_vy += GRAV
            bird_y += bird_vy
            pipe_timer += 1
            if pipe_timer >= 90:
                pipe_timer = 0
                gap_y = random.randint(120, H - 120 - GAP)
                pipes.append({
                    "x": W, "gap_y": gap_y,
                    "top": pygame.Rect(W, 0, PIPE_W, gap_y),
                    "bot": pygame.Rect(W, gap_y + GAP, PIPE_W, H - gap_y - GAP)
                })
            for p in pipes[:]:
                p["top"].x -= PIPE_SPEED
                p["bot"].x -= PIPE_SPEED
                p["x"] = p["top"].x
                if p["top"].right < 0:
                    pipes.remove(p)
                    continue
                if p["top"].right < bird_x and id(p) not in passed:
                    passed.add(id(p))
                    score += 1
                if p["top"].collidepoint(bird_x, bird_y) or p["bot"].collidepoint(bird_x, bird_y):
                    game_over = True
                if bird_x + 15 > p["top"].left and bird_x - 15 < p["top"].right:
                    if bird_y - 15 < p["top"].bottom or bird_y + 15 > p["bot"].top:
                        game_over = True
            if bird_y < 0 or bird_y > H:
                game_over = True

        screen.fill((135, 206, 235))
        pygame.draw.rect(screen, (34, 139, 34), (0, H - 60, W, 60))
        for p in pipes:
            pygame.draw.rect(screen, (50, 160, 60), p["top"])
            pygame.draw.rect(screen, (50, 160, 60), p["bot"])
            pygame.draw.rect(screen, (40, 120, 50), p["top"], 3)
            pygame.draw.rect(screen, (40, 120, 50), p["bot"], 3)
        pygame.draw.ellipse(screen, (255, 220, 50), (bird_x - 15, bird_y - 15, 30, 30))
        pygame.draw.circle(screen, (40, 30, 20), (bird_x + 8, bird_y - 5), 4)
        if not started:
            t = font_small.render("SPACE to start", True, (40, 40, 60))
            screen.blit(t, (W // 2 - t.get_width() // 2, H // 2 - 60))
        screen.blit(font.render(str(score), True, (255, 255, 255)), (W // 2 - 20, 50))
        if game_over:
            over = font.render("Game Over", True, (200, 60, 60))
            screen.blit(over, (W // 2 - over.get_width() // 2, H // 2 - 80))
            screen.blit(font_small.render("SPACE to restart", True, (255, 255, 255)), (W // 2 - 80, H // 2 - 20))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()
