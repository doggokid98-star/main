"""
Endless Runner - Dodge obstacles, speed increases. One more run!
"""
import pygame
import random

pygame.init()
W, H = 500, 400
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Endless Runner")
clock = pygame.time.Clock()
FPS = 60

player_y = H - 100
player_vy = 0
on_ground = True
obstacles = []
scroll = 0
score = 0
speed = 6
game_over = False
font = pygame.font.SysFont("segoeui", 28)


def main():
    global player_y, player_vy, on_ground, obstacles, scroll, score, speed, game_over
    running = True
    obst_timer = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over and event.key == pygame.K_SPACE:
                    game_over = False
                    obstacles.clear()
                    scroll = 0
                    score = 0
                    speed = 6
                    player_y = H - 100
                    player_vy = 0
                elif not game_over and (event.key == pygame.K_SPACE or event.key == pygame.K_UP) and on_ground:
                    player_vy = -14
                    on_ground = False

        if not game_over:
            player_vy += 0.6
            player_y += player_vy
            ground_y = H - 80
            if player_y >= ground_y - 30:
                player_y = ground_y - 30
                player_vy = 0
                on_ground = True
            scroll += speed
            score = scroll // 20
            speed = 6 + score // 50
            obst_timer += 1
            if obst_timer > 60 - speed:
                obst_timer = 0
                h = random.randint(40, 80)
                obstacles.append({"x": W + 20, "y": H - 80 - h, "w": 25, "h": h})
            for o in obstacles[:]:
                o["x"] -= speed
                if o["x"] + o["w"] < 0:
                    obstacles.remove(o)
                if (o["x"] < 60 and o["x"] + o["w"] > 30 and
                    player_y + 25 > o["y"] and player_y < o["y"] + o["h"]):
                    game_over = True

        screen.fill((50, 55, 80))
        pygame.draw.rect(screen, (60, 130, 70), (0, H - 80, W, 80))
        for o in obstacles:
            pygame.draw.rect(screen, (180, 70, 70), (o["x"], o["y"], o["w"], o["h"]))
        pygame.draw.rect(screen, (100, 200, 255), (30, player_y, 30, 30))
        screen.blit(font.render(f"Score: {score}  Speed: {speed}", True, (255, 255, 255)), (10, 10))
        if game_over:
            screen.blit(font.render("SPACE to restart", True, (255, 200, 100)), (W // 2 - 100, H // 2 - 20))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()
