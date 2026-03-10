"""
Space Shooter - Waves of enemies, power-ups, score.
"""
import pygame
import random
import math

pygame.init()
W, H = 900, 650
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()
FPS = 60

player_x = W // 2
player_y = H - 80
bullets = []
enemies = []
explosions = []
particles = []
wave = 1
score = 0
player_hp = 100
invuln = 0


def main():
    global player_x, player_y, bullets, enemies, explosions, wave, score, player_hp, invuln
    font = pygame.font.SysFont("segoeui", 24)
    spawn_timer = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bullets.append({"x": player_x, "y": player_y - 20, "vy": -12})

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= 8
        if keys[pygame.K_RIGHT]:
            player_x += 8
        player_x = max(30, min(W - 30, player_x))

        spawn_timer += 1
        if spawn_timer >= max(20 - wave * 2, 8):
            spawn_timer = 0
            enemies.append({
                "x": random.randint(40, W - 40), "y": -20,
                "vy": 1.5 + wave * 0.2, "hp": 1, "w": 36, "h": 28
            })

        for b in bullets[:]:
            b["y"] += b["vy"]
            if b["y"] < -10:
                bullets.remove(b)
                continue
            for e in enemies[:]:
                if (e["x"] - e["w"]//2 <= b["x"] <= e["x"] + e["w"]//2 and
                    e["y"] <= b["y"] <= e["y"] + e["h"]):
                    score += 10
                    explosions.append({"x": e["x"], "y": e["y"], "t": 0})
                    enemies.remove(e)
                    if b in bullets:
                        bullets.remove(b)
                    break

        for e in enemies[:]:
            e["y"] += e["vy"]
            if e["y"] > H:
                enemies.remove(e)
            if invuln <= 0 and (e["x"] - e["w"]//2 <= player_x <= e["x"] + e["w"]//2 and
                                e["y"] + e["h"] >= player_y - 25):
                player_hp -= 15
                invuln = 90
                explosions.append({"x": player_x, "y": player_y, "t": 0})
                if player_hp <= 0:
                    running = False

        if invuln > 0:
            invuln -= 1
        for ex in explosions[:]:
            ex["t"] += 1
            if ex["t"] > 30:
                explosions.remove(ex)

        if len(enemies) == 0 and spawn_timer > 60:
            wave += 1
            score += 50

        screen.fill((8, 8, 20))
        for star in range(80):
            sx = (star * 31) % W
            sy = (star * 17 + wave) % H
            pygame.draw.circle(screen, (180, 180, 220), (sx, sy), 1)
        for e in enemies:
            pygame.draw.rect(screen, (220, 80, 80), (e["x"] - e["w"]//2, e["y"], e["w"], e["h"]))
        for b in bullets:
            pygame.draw.rect(screen, (100, 255, 200), (b["x"] - 2, b["y"], 4, 12))
        for ex in explosions:
            r = ex["t"] * 2
            pygame.draw.circle(screen, (255, 200, 80), (int(ex["x"]), int(ex["y"])), r)
        if invuln % 4 < 2:
            pygame.draw.polygon(screen, (80, 200, 255),
                               [(player_x, player_y - 25), (player_x - 20, player_y + 15), (player_x, player_y + 5), (player_x + 20, player_y + 15)])
        screen.blit(font.render(f"Wave {wave}  Score: {score}  HP: {player_hp}", True, (255, 255, 255)), (10, 10))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()
