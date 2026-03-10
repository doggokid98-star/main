"""
Tower Defense - Place towers, stop the creeps. Waves get harder.
"""
import pygame
import random
import math

pygame.init()
W, H = 800, 500
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Tower Defense")
clock = pygame.time.Clock()
FPS = 60

# Path: list of (x, y)
path = []
for x in range(0, W + 1, 40):
    path.append((x, 80))
for y in range(80, 350, 30):
    path.append((W - 20, y))
for x in range(W - 20, 100, -30):
    path.append((x, 340))
for y in range(340, 80, -30):
    path.append((100, y))
path.append((100, 50))
path.append((-30, 50))

towers = []
creeps = []
bullets = []
wave = 1
cash = 150
lives = 20
spawn_timer = 0
wave_timer = 0
font = pygame.font.SysFont("segoeui", 20)


def main():
    global towers, creeps, bullets, wave, cash, lives, spawn_timer, wave_timer
    running = True
    placing = None
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                placing = None
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if placing and 50 <= my <= H - 50:
                    tx = (mx // 50) * 50 + 25
                    ty = (my // 50) * 50 + 25
                    if not any(abs(t["x"] - tx) < 30 and abs(t["y"] - ty) < 30 for t in towers):
                        if cash >= 50:
                            towers.append({"x": tx, "y": ty, "range": 120, "dmg": 15, "cooldown": 0})
                            cash -= 50
                    placing = None
                elif 10 <= mx <= 120 and H - 45 <= my <= H - 15:
                    placing = "tower"
                for t in towers[:]:
                    if (t["x"] - mx)**2 + (t["y"] - my)**2 < 400 and event.button == 3:
                        towers.remove(t)
                        cash += 25
                        break

        if not game_over:
            wave_timer += 1
            if wave_timer > 300 and len(creeps) == 0:
                wave += 1
                wave_timer = 0
            spawn_timer += 1
            if spawn_timer >= max(25 - wave, 8):
                spawn_timer = 0
                if path:
                    creeps.append({"path_idx": 0, "hp": 30 + wave * 10, "max_hp": 30 + wave * 10, "speed": 1.2})
            for c in creeps[:]:
                c["path_idx"] += c["speed"] * 0.5
                idx = int(c["path_idx"])
                if idx >= len(path) - 1:
                    creeps.remove(c)
                    lives -= 1
                    if lives <= 0:
                        game_over = True
                    continue
                for t in towers:
                    t["cooldown"] = max(0, t["cooldown"] - 1)
                    cx = path[idx][0]
                    cy = path[idx][1]
                    if (t["x"] - cx)**2 + (t["y"] - cy)**2 <= t["range"]**2 and t["cooldown"] == 0:
                        t["cooldown"] = 30
                        bullets.append({"x": t["x"], "y": t["y"], "tx": cx, "ty": cy, "dmg": t["dmg"], "target": c})
                        break
            for b in bullets[:]:
                b["x"] += (b["tx"] - b["x"]) * 0.2
                b["y"] += (b["ty"] - b["y"]) * 0.2
                if abs(b["x"] - b["tx"]) < 10 and abs(b["y"] - b["ty"]) < 10:
                    b["target"]["hp"] -= b["dmg"]
                    bullets.remove(b)
                    if b["target"]["hp"] <= 0:
                        creeps.remove(b["target"])
                        cash += 5
            for c in creeps[:]:
                if c["hp"] <= 0:
                    creeps.remove(c)

        screen.fill((25, 30, 40))
        for i in range(len(path) - 1):
            pygame.draw.line(screen, (80, 90, 110), path[i], path[i + 1], 25)
        for t in towers:
            pygame.draw.circle(screen, (80, 150, 255), (int(t["x"]), int(t["y"])), 22)
            pygame.draw.circle(screen, (60, 120, 200), (int(t["x"]), int(t["y"])), 22, 2)
        for c in creeps:
            idx = min(int(c["path_idx"]), len(path) - 1)
            cx, cy = path[idx]
            pygame.draw.circle(screen, (220, 100, 100), (int(cx), int(cy)), 12)
            pygame.draw.rect(screen, (80, 40, 40), (cx - 15, cy - 20, 30, 5))
            pygame.draw.rect(screen, (200, 60, 60), (cx - 15, cy - 20, 30 * c["hp"] / c["max_hp"], 5))
        for b in bullets:
            pygame.draw.circle(screen, (255, 220, 100), (int(b["x"]), int(b["y"])), 5)
        pygame.draw.rect(screen, (60, 70, 100), (10, H - 50, 120, 35))
        screen.blit(font.render("Tower $50 (click)", True, (255, 255, 255)), (15, H - 42))
        screen.blit(font.render(f"Wave {wave}  Cash ${cash}  Lives {lives}", True, (255, 255, 255)), (150, 10))
        if game_over:
            screen.blit(font.render("Game Over", True, (255, 100, 100)), (W // 2 - 50, H // 2 - 20))
        if placing:
            mx, my = pygame.mouse.get_pos()
            pygame.draw.circle(screen, (100, 180, 255), (mx, my), 22)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()
