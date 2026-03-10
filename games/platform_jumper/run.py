"""
Platform Jumper - Collect gems, reach the door. Tight controls.
"""
import pygame
import random

pygame.init()
W, H = 640, 480
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Platform Jumper")
clock = pygame.time.Clock()
FPS = 60

GRAV = 0.6
JUMP = -12
MOVE = 5
platforms = []
gems = []
door_rect = None
px, py = 100, 300
vx, vy = 0, 0
score = 0
won = False


def main():
    global platforms, gems, door_rect, px, py, vx, vy, score, won
    font = pygame.font.SysFont("segoeui", 24)
    platforms = [
        pygame.Rect(0, H - 40, W, 40),
        pygame.Rect(100, 350, 120, 20),
        pygame.Rect(280, 280, 100, 20),
        pygame.Rect(450, 320, 120, 20),
        pygame.Rect(150, 220, 80, 20),
        pygame.Rect(350, 180, 100, 20),
        pygame.Rect(500, 250, 80, 20),
        pygame.Rect(200, 120, 140, 20),
        pygame.Rect(420, 100, 120, 20),
    ]
    gems = [pygame.Rect(p.x + p.w // 2 - 12, p.y - 30, 24, 24) for p in platforms[1:6]]
    door_rect = pygame.Rect(W - 80, 60, 50, 80)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        if not won:
            keys = pygame.key.get_pressed()
            vx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) * MOVE - (keys[pygame.K_LEFT] or keys[pygame.K_a]) * MOVE
            if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and vy >= 0:
                for p in platforms:
                    if p.collidepoint(px + 15, py + 32) or p.collidepoint(px + 18, py + 32):
                        vy = JUMP
                        break
            vy += GRAV
            px += vx
            py += vy
            px = max(0, min(W - 30, px))
            for p in platforms:
                if p.collidepoint(px + 15, py + 31) and vy > 0:
                    py = p.top - 31
                    vy = 0
                if p.collidepoint(px + 15, py) and vy < 0:
                    vy = 0
            for g in gems[:]:
                if g.collidepoint(px + 15, py + 15):
                    gems.remove(g)
                    score += 10
            if door_rect.collidepoint(px + 15, py + 15) and len(gems) == 0:
                won = True

        screen.fill((40, 45, 70))
        for p in platforms:
            pygame.draw.rect(screen, (90, 100, 140), p)
            pygame.draw.rect(screen, (120, 130, 180), p, 2)
        for g in gems:
            pygame.draw.ellipse(screen, (255, 215, 0), g)
        pygame.draw.rect(screen, (80, 200, 120), door_rect)
        pygame.draw.rect(screen, (60, 160, 90), door_rect, 3)
        pygame.draw.rect(screen, (255, 220, 180), (px, py, 30, 32))
        screen.blit(font.render(f"Score: {score}  Gems: {len(gems)} left", True, (255, 255, 255)), (10, 10))
        if won:
            screen.blit(font.render("You win! Reach the green door.", True, (100, 255, 150)), (W // 2 - 150, H // 2 - 20))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()
