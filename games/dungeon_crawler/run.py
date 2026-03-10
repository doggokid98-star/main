"""
Dungeon Crawler - Rogue-like with procedural floors, combat, items, permadeath.
Immersive atmosphere with exploration and risk.
"""
import random
import pygame
import json
import os

pygame.init()
W, H = 960, 640
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Dungeon Crawler")
clock = pygame.time.Clock()
FPS = 60

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(SCRIPT_DIR, "highscores.json")

TILE = 32
GRID_W, GRID_H = 24, 18

# Colors
FLOOR = (45, 42, 55)
WALL = (25, 22, 35)
WALL_EDGE = (60, 55, 75)
PLAYER = (255, 220, 100)
ENEMY = (200, 80, 80)
HP_BAR = (200, 60, 60)
HP_BG = (80, 40, 40)
GOLD = (255, 215, 0)
STAIRS = (120, 100, 180)
TEXT = (240, 235, 255)
MUTED = (140, 130, 160)
POTION = (100, 200, 255)
SWORD = (180, 180, 190)


def load_highscores():
    if os.path.isfile(SAVE_PATH):
        try:
            with open(SAVE_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_highscore(floor_reached, gold, kills):
    scores = load_highscores()
    scores.append({"floor": floor_reached, "gold": gold, "kills": kills})
    scores.sort(key=lambda x: (-x["floor"], -x["gold"]))
    with open(SAVE_PATH, "w") as f:
        json.dump(scores[:15], f, indent=2)


def generate_level(floor_num):
    grid = [[1] * GRID_W for _ in range(GRID_H)]
    rooms = []
    for _ in range(6):
        rw = random.randint(4, 8)
        rh = random.randint(3, 6)
        rx = random.randint(1, GRID_W - rw - 1)
        ry = random.randint(1, GRID_H - rh - 1)
        rooms.append((rx, ry, rw, rh))
    for rx, ry, rw, rh in rooms:
        for y in range(ry, ry + rh):
            for x in range(rx, rx + rw):
                if 0 < x < GRID_W - 1 and 0 < y < GRID_H - 1:
                    grid[y][x] = 0
    for i in range(len(rooms) - 1):
        x1 = rooms[i][0] + rooms[i][2] // 2
        y1 = rooms[i][1] + rooms[i][3] // 2
        x2 = rooms[i + 1][0] + rooms[i + 1][2] // 2
        y2 = rooms[i + 1][1] + rooms[i + 1][3] // 2
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 < x < GRID_W - 1:
                grid[y1][x] = 0
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 < y < GRID_H - 1:
                grid[y][x2] = 0
    # Stairs
    sx, sy = random.randint(1, GRID_W - 2), random.randint(1, GRID_H - 2)
    while grid[sy][sx] != 0:
        sx, sy = random.randint(1, GRID_W - 2), random.randint(1, GRID_H - 2)
    # Enemies
    enemies = []
    for _ in range(2 + floor_num):
        ex, ey = random.randint(1, GRID_W - 2), random.randint(1, GRID_H - 2)
        if grid[ey][ex] == 0:
            enemies.append({"x": ex, "y": ey, "hp": 20 + floor_num * 8, "max_hp": 20 + floor_num * 8, "dmg": 3 + floor_num})
    # Items
    items = []
    for _ in range(3):
        ix, iy = random.randint(1, GRID_W - 2), random.randint(1, GRID_H - 2)
        if grid[iy][ix] == 0:
            items.append({"x": ix, "y": iy, "type": random.choice(["gold", "potion", "sword"])})
    return grid, (sx, sy), enemies, items


def main():
    font = pygame.font.SysFont("segoeui", 24)
    font_small = pygame.font.SysFont("segoeui", 18)

    floor = 1
    grid, stairs, enemies, items = generate_level(floor)
    px, py = 2, GRID_H // 2
    while grid[py][px] != 0:
        px += 1
    player_hp = 50
    player_max_hp = 50
    player_dmg = 8
    gold = 0
    kills = 0
    message = "Enter the dungeon..."
    message_timer = 0
    game_over = False
    victory = False
    show_scores = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if show_scores or game_over or victory:
                        running = False
                    else:
                        show_scores = not show_scores
                if game_over or victory:
                    continue
                if show_scores:
                    continue
                dx, dy = 0, 0
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    dy = -1
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    dy = 1
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    dx = -1
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    dx = 1
                if dx or dy:
                    nx, ny = px + dx, py + dy
                    if 0 <= nx < GRID_W and 0 <= ny < GRID_H and grid[ny][nx] == 0:
                        # Check enemy
                        enemy_here = next((e for e in enemies if e["x"] == nx and e["y"] == ny), None)
                        if enemy_here:
                            enemy_here["hp"] -= player_dmg
                            if enemy_here["hp"] <= 0:
                                enemies.remove(enemy_here)
                                kills += 1
                                gold += random.randint(5, 15)
                                message = "Enemy defeated!"
                            else:
                                # Enemy hits back
                                player_hp -= enemy_here.get("dmg", 5)
                                message = f"You take {enemy_here.get('dmg', 5)} damage!"
                            message_timer = 90
                        else:
                            px, py = nx, ny
                            # Pick up items
                            for it in items[:]:
                                if it["x"] == px and it["y"] == py:
                                    if it["type"] == "gold":
                                        gold += random.randint(10, 25)
                                        message = "Picked up gold!"
                                    elif it["type"] == "potion":
                                        player_hp = min(player_max_hp, player_hp + 25)
                                        message = "Health restored!"
                                    elif it["type"] == "sword":
                                        player_dmg += 4
                                        message = "Attack increased!"
                                    items.remove(it)
                                    message_timer = 60
                                    break
                            # Stairs
                            if (px, py) == stairs:
                                floor += 1
                                if floor > 10:
                                    victory = True
                                    save_highscore(floor - 1, gold, kills)
                                else:
                                    grid, stairs, enemies, items = generate_level(floor)
                                    message = f"Floor {floor}..."
                                    message_timer = 60
                        if player_hp <= 0:
                            game_over = True
                            save_highscore(floor, gold, kills)

        if not running:
            break

        if message_timer > 0:
            message_timer -= 1

        screen.fill((15, 12, 22))
        for y in range(GRID_H):
            for x in range(GRID_W):
                rx = x * TILE
                ry = y * TILE
                if grid[y][x] == 1:
                    pygame.draw.rect(screen, WALL, (rx, ry, TILE, TILE))
                    pygame.draw.rect(screen, WALL_EDGE, (rx, ry, TILE, TILE), 1)
                else:
                    pygame.draw.rect(screen, FLOOR, (rx, ry, TILE, TILE))
                if (x, y) == stairs:
                    pygame.draw.rect(screen, STAIRS, (rx + 4, ry + 4, TILE - 8, TILE - 8))
                for e in enemies:
                    if e["x"] == x and e["y"] == y:
                        pygame.draw.rect(screen, ENEMY, (rx + 4, ry + 4, TILE - 8, TILE - 8))
                        # HP bar
                        pygame.draw.rect(screen, HP_BG, (rx, ry - 4, TILE, 4))
                        pygame.draw.rect(screen, HP_BAR, (rx, ry - 4, TILE * e["hp"] // max(1, e["max_hp"]), 4))
                for it in items:
                    if it["x"] == x and it["y"] == y:
                        col = GOLD if it["type"] == "gold" else POTION if it["type"] == "potion" else SWORD
                        pygame.draw.circle(screen, col, (rx + TILE // 2, ry + TILE // 2), 6)
                if px == x and py == y:
                    pygame.draw.rect(screen, PLAYER, (rx + 4, ry + 4, TILE - 8, TILE - 8))

        # UI
        pygame.draw.rect(screen, (30, 28, 40), (0, GRID_H * TILE, W, H - GRID_H * TILE))
        screen.blit(font.render(f"Floor {floor}  HP: {player_hp}/{player_max_hp}  Gold: {gold}  Kills: {kills}", True, TEXT), (10, GRID_H * TILE + 10))
        if message_timer > 0:
            screen.blit(font_small.render(message, True, MUTED), (10, GRID_H * TILE + 42))
        screen.blit(font_small.render("WASD: move  ESC: quit / high scores", True, MUTED), (10, H - 28))

        if show_scores:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            screen.blit(font.render("High Scores (Floor, Gold, Kills)", True, TEXT), (W // 2 - 180, 40))
            for i, s in enumerate(load_highscores()[:10]):
                t = font_small.render(f"{i + 1}. Floor {s['floor']}  ${s['gold']}  {s['kills']} kills", True, TEXT)
                screen.blit(t, (W // 2 - 120, 80 + i * 32))
            screen.blit(font_small.render("ESC to close", True, MUTED), (W // 2 - 50, H - 50))

        if game_over:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            screen.blit(font.render("You Died", True, (220, 80, 80)), (W // 2 - 60, H // 2 - 50))
            screen.blit(font_small.render(f"Floor {floor}  Gold: {gold}  Kills: {kills}", True, TEXT), (W // 2 - 100, H // 2 - 10))
            screen.blit(font_small.render("ESC to quit", True, MUTED), (W // 2 - 50, H // 2 + 30))

        if victory:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            screen.blit(font.render("Victory! Dungeon Cleared!", True, GOLD), (W // 2 - 140, H // 2 - 50))
            screen.blit(font_small.render("ESC to quit", True, MUTED), (W // 2 - 50, H // 2 + 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
