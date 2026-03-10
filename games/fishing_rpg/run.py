"""
Fishing RPG - Peaceful village, boat, fish, sell, upgrade. Immersive and relaxing.
"""
import random
import math
import pygame
import json
import os

pygame.init()
W, H = 1000, 680
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Fishing RPG")
clock = pygame.time.Clock()
FPS = 60

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(SCRIPT_DIR, "save.json")

# Colors
SKY = (135, 206, 250)
WATER = (30, 120, 180)
WATER_DEEP = (20, 80, 140)
SAND = (238, 214, 175)
GRASS = (60, 140, 60)
BOAT = (139, 90, 43)
PLAYER = (255, 220, 180)
FISH_COLORS = [(255, 180, 80), (80, 180, 255), (255, 100, 100), (100, 255, 150), (200, 100, 255)]
TEXT = (255, 255, 255)
MUTED = (180, 190, 200)
GOLD = (255, 215, 0)

FISH_TYPES = [
    {"name": "Minnow", "value": 5, "size": 8, "speed": 2},
    {"name": "Bass", "value": 25, "size": 14, "speed": 1.2},
    {"name": "Trout", "value": 40, "size": 16, "speed": 1.5},
    {"name": "Salmon", "value": 80, "size": 20, "speed": 1},
    {"name": "Tuna", "value": 150, "size": 28, "speed": 0.8},
]


def load_save():
    if os.path.isfile(SAVE_PATH):
        try:
            with open(SAVE_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"gold": 50, "rod_level": 1, "boat_level": 1, "best_catch": 0}


def save_save(data):
    with open(SAVE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def main():
    font = pygame.font.SysFont("segoeui", 24)
    font_small = pygame.font.SysFont("segoeui", 18)

    data = load_save()
    gold = data["gold"]
    rod_level = data["rod_level"]
    boat_level = data["boat_level"]
    best_catch = data.get("best_catch", 0)

    # World: 0=water, 1=deep water, 2=sand/shore, 3=dock, 4=shop
    LAKE_W, LAKE_H = 30, 22
    tile_w = min(W // LAKE_W, H // LAKE_H)
    lake = []
    for y in range(LAKE_H):
        row = []
        for x in range(LAKE_W):
            d = math.hypot(x - LAKE_W / 2, y - LAKE_H / 2)
            if d < 4:
                row.append(3)  # dock
            elif d < 6:
                row.append(2)  # sand
            elif d < 10:
                row.append(0)  # water
            else:
                row.append(1 if random.random() < 0.5 else 0)
        lake.append(row)
    lake[LAKE_H - 1][LAKE_W // 2] = 4  # shop

    px, py = LAKE_W // 2, LAKE_H - 2
    in_boat = True
    boat_speed = 0.08 * boat_level
    fishes = []
    for _ in range(25):
        fx = random.uniform(2, LAKE_W - 3)
        fy = random.uniform(2, LAKE_H - 3)
        ft = random.choice(FISH_TYPES)
        fishes.append({
            "x": fx, "y": fy, "vx": random.uniform(-0.02, 0.02), "vy": random.uniform(-0.02, 0.02),
            "type": ft, "caught": False
        })
    catch_bar = 0
    catch_target = 0
    catch_fish = None
    message = ""
    message_timer = 0
    menu = None  # "shop", "sell", None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if menu:
                        menu = None
                    else:
                        running = False
                if event.key == pygame.K_e and not menu:
                    tx, ty = int(px), int(py)
                    if 0 <= ty < LAKE_H and 0 <= tx < LAKE_W:
                        if lake[ty][tx] == 3:
                            in_boat = not in_boat
                            if in_boat:
                                message = "Got in the boat."
                            else:
                                message = "Got out at the dock."
                            message_timer = 60
                        elif lake[ty][tx] == 4:
                            caught_count = sum(1 for f in fishes if f["caught"])
                            menu = "sell" if caught_count > 0 else "shop"
                if menu == "shop":
                    if event.key == pygame.K_1 and gold >= 100:
                        gold -= 100
                        rod_level = min(5, rod_level + 1)
                        message = "Rod upgraded!"
                        message_timer = 60
                    if event.key == pygame.K_2 and gold >= 150:
                        gold -= 150
                        boat_level = min(5, boat_level + 1)
                        message = "Boat upgraded!"
                        message_timer = 60
                if menu == "sell" and event.key == pygame.K_1:
                    total = sum(f["type"]["value"] for f in fishes if f["caught"])
                    gold += total
                    for f in fishes:
                        f["caught"] = False
                    message = f"Sold fish for ${total}!"
                    message_timer = 90
                    menu = None

        if not running:
            break

        # Movement
        if not menu and not catch_fish:
            keys = pygame.key.get_pressed()
            dx = dy = 0
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
            if dx or dy:
                sp = boat_speed if in_boat else 0.08
                nx = px + dx * sp
                ny = py + dy * sp
                nx = max(0.5, min(LAKE_W - 0.5, nx))
                ny = max(0.5, min(LAKE_H - 0.5, ny))
                ti = lake[int(ny)][int(nx)]
                if ti in (0, 1, 3, 4) or not in_boat:
                    px, py = nx, ny

        # Fishing: space to cast / reel
        if not menu and in_boat and not catch_fish:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                for f in fishes:
                    if not f["caught"] and abs(f["x"] - px) < 1.5 and abs(f["y"] - py) < 1.5:
                        catch_fish = f
                        catch_target = 60 + rod_level * 15 - f["type"]["speed"] * 20
                        catch_bar = 0
                        break
        if catch_fish:
            catch_bar += 1
            if catch_bar >= catch_target:
                catch_fish["caught"] = True
                best_catch = max(best_catch, catch_fish["type"]["value"])
                message = f"Caught {catch_fish['type']['name']} (${catch_fish['type']['value']})!"
                message_timer = 90
                catch_fish = None
            elif random.random() < 0.02:
                catch_fish = None
                message = "Fish got away!"
                message_timer = 60

        # Fish move
        for f in fishes:
            if f["caught"]:
                continue
            f["x"] += f["vx"]
            f["y"] += f["vy"]
            if f["x"] < 1 or f["x"] > LAKE_W - 1:
                f["vx"] *= -1
            if f["y"] < 1 or f["y"] > LAKE_H - 1:
                f["vy"] *= -1

        if message_timer > 0:
            message_timer -= 1

        # Draw
        screen.fill(SKY)
        for y in range(LAKE_H):
            for x in range(LAKE_W):
                t = lake[y][x]
                rx = x * tile_w
                ry = y * tile_w
                if t == 0:
                    pygame.draw.rect(screen, WATER, (rx, ry, tile_w + 1, tile_w + 1))
                elif t == 1:
                    pygame.draw.rect(screen, WATER_DEEP, (rx, ry, tile_w + 1, tile_w + 1))
                elif t == 2:
                    pygame.draw.rect(screen, SAND, (rx, ry, tile_w + 1, tile_w + 1))
                elif t == 3:
                    pygame.draw.rect(screen, (100, 80, 60), (rx, ry, tile_w + 1, tile_w + 1))
                elif t == 4:
                    pygame.draw.rect(screen, (120, 80, 100), (rx, ry, tile_w + 1, tile_w + 1))

        for f in fishes:
            if f["caught"]:
                continue
            idx = FISH_TYPES.index(f["type"]) % len(FISH_COLORS)
            pygame.draw.ellipse(screen, FISH_COLORS[idx],
                               (f["x"] * tile_w - 8, f["y"] * tile_w - 4, 16, 8))

        # Player / boat
        px_draw = px * tile_w
        py_draw = py * tile_w
        if in_boat:
            pygame.draw.ellipse(screen, BOAT, (px_draw - 18, py_draw - 10, 36, 20))
            pygame.draw.circle(screen, PLAYER, (int(px_draw), int(py_draw - 4)), 8)
        else:
            pygame.draw.circle(screen, PLAYER, (int(px_draw), int(py_draw)), 10)

        # UI
        pygame.draw.rect(screen, (30, 35, 50), (0, LAKE_H * tile_w, W, H - LAKE_H * tile_w))
        screen.blit(font.render(f"Gold: ${gold}  Rod Lv.{rod_level}  Boat Lv.{boat_level}  Best: ${best_catch}", True, TEXT), (10, LAKE_H * tile_w + 10))
        caught_count = sum(1 for f in fishes if f["caught"])
        if caught_count > 0:
            screen.blit(font_small.render(f"Caught: {caught_count} fish - E at shop to sell", True, GOLD), (10, LAKE_H * tile_w + 40))
        screen.blit(font_small.render("WASD: move  SPACE: fish  E: dock/shop  ESC: menu", True, MUTED), (10, H - 28))
        if message_timer > 0:
            screen.blit(font_small.render(message, True, (200, 255, 200)), (W // 2 - 100, LAKE_H * tile_w + 38))
        if catch_fish:
            pygame.draw.rect(screen, (50, 50, 70), (W // 2 - 80, H // 2 - 25, 160, 50))
            pygame.draw.rect(screen, (80, 200, 100), (W // 2 - 75, H // 2 - 15, 150 * catch_bar / catch_target, 30))
            screen.blit(font_small.render("Reeling...", True, TEXT), (W // 2 - 40, H // 2 - 45))

        if menu == "shop":
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            screen.blit(font.render("SHOP", True, GOLD), (W // 2 - 30, 80))
            screen.blit(font_small.render("1: Upgrade Rod ($100) - Lv." + str(rod_level), True, TEXT), (W // 2 - 120, 140))
            screen.blit(font_small.render("2: Upgrade Boat ($150) - Lv." + str(boat_level), True, TEXT), (W // 2 - 120, 180))
            screen.blit(font_small.render("ESC: Close", True, MUTED), (W // 2 - 50, 250))

        if menu == "sell":
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            total = sum(f["type"]["value"] for f in fishes if f["caught"])
            screen.blit(font.render(f"Sell {caught_count} fish for ${total}?", True, TEXT), (W // 2 - 120, H // 2 - 40))
            screen.blit(font_small.render("1: Yes  ESC: No", True, MUTED), (W // 2 - 60, H // 2 + 10))

        pygame.display.flip()
        clock.tick(FPS)

    save_save({"gold": gold, "rod_level": rod_level, "boat_level": boat_level, "best_catch": best_catch})
    pygame.quit()


if __name__ == "__main__":
    main()
