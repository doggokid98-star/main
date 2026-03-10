"""
City Driver - Top-down city with car, on-foot, jobs, bank, stocks, highway, NPCs.
Drive or get out and walk. Crashes and simple physics.
"""
import json
import math
import os
import random
import pygame

pygame.init()
W, H = 1024, 720
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("City Driver")
clock = pygame.time.Clock()
FPS = 60

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(SCRIPT_DIR, "save.json")

TILE = 48
MAP_W, MAP_H = 40, 30  # tiles
HIGHWAY_Y = 12  # horizontal highway row

# Colors
SKY = (135, 206, 235)
ROAD = (60, 60, 65)
ROAD_LINE = (200, 200, 200)
GRASS = (34, 139, 34)
BUILDING = (80, 70, 90)
BUILDING2 = (100, 85, 110)
BANK_COL = (50, 180, 80)
JOB_COL = (200, 150, 50)
STOCK_COL = (50, 100, 200)
STORE_COL = (180, 80, 120)
PLAYER_CAR = (220, 60, 60)
NPC_CAR = (90, 90, 100)
PLAYER_FOOT = (255, 200, 100)
TEXT = (255, 255, 255)
MUTED = (180, 180, 190)

# Fake companies for stocks
COMPANIES = ["MegaTech", "GreenEnergy", "FoodCorp", "BuildCo", "MediaNet"]
STOCK_PRICES = {c: 100.0 for c in COMPANIES}
STOCK_HOLDINGS = {c: 0 for c in COMPANIES}


def load_save():
    global STOCK_PRICES, STOCK_HOLDINGS
    if os.path.isfile(SAVE_PATH):
        try:
            with open(SAVE_PATH, "r") as f:
                d = json.load(f)
                return d.get("cash", 500), d.get("bank", 0), d.get("stocks", STOCK_HOLDINGS), d.get("prices", STOCK_PRICES)
        except Exception:
            pass
    return 500, 0, dict(STOCK_HOLDINGS), dict(STOCK_PRICES)


def save_save(cash, bank, stocks, prices):
    with open(SAVE_PATH, "w") as f:
        json.dump({"cash": cash, "bank": bank, "stocks": stocks, "prices": prices}, f, indent=2)


def main():
    font = pygame.font.SysFont("segoeui", 22)
    font_small = pygame.font.SysFont("segoeui", 18)

    cash, bank, stocks, prices = load_save()
    STOCK_PRICES.update(prices)
    STOCK_HOLDINGS.update(stocks)

    # World: 0=grass, 1=road, 2=highway, 3=bank, 4=job, 5=stock, 6=store
    world = [[0] * MAP_W for _ in range(MAP_H)]
    for x in range(MAP_W):
        world[HIGHWAY_Y][x] = 2
        world[HIGHWAY_Y + 1][x] = 2
    for x in range(4, 10):
        for y in range(4, 8):
            world[y][x] = 3  # bank
    for x in range(12, 18):
        for y in range(4, 8):
            world[y][x] = 4  # job
    for x in range(20, 26):
        for y in range(4, 8):
            world[y][x] = 5  # stock
    for x in range(28, 34):
        for y in range(4, 8):
            world[y][x] = 6  # store
    for x in range(2, MAP_W - 2):
        for y in range(14, MAP_H - 2):
            if world[y][x] == 0 and random.random() < 0.15:
                world[y][x] = 1  # some roads
    for y in range(2, MAP_H - 2):
        for x in range(2, MAP_W - 2):
            if world[y][x] == 0 and random.random() < 0.12:
                world[y][x] = 1

    # Player
    px, py = 6 * TILE, 14 * TILE
    vx, vy = 0, 0
    in_car = True
    car_x, car_y = px, py
    walk_speed = 4
    car_speed = 0
    car_angle = 0  # degrees, 0 = right
    car_max = 8
    car_accel = 0.4
    car_friction = 0.92
    car_turn = 3
    job_timer = 0
    job_earn = 50
    menu = None  # "bank", "job", "stock", "store", None
    stock_tick = 0
    crash_cooldown = 0
    npcs = []
    for _ in range(12):
        nx = random.randint(2, MAP_W - 2) * TILE + TILE // 2
        ny = random.randint(14, MAP_H - 2) * TILE + TILE // 2
        nvx = random.uniform(-2, 2)
        nvy = random.uniform(-2, 2)
        npcs.append({"x": nx, "y": ny, "vx": nvx, "vy": nvy, "in_car": random.random() > 0.5})
    other_cars = []
    for _ in range(8):
        cx = random.randint(0, MAP_W - 1) * TILE + TILE // 2
        cy = HIGHWAY_Y * TILE + TILE
        other_cars.append({"x": cx, "y": cy, "vx": random.uniform(2, 5)})

    cam_x, cam_y = px - W // 2, py - H // 2

    def world_at(tx, ty):
        if 0 <= tx < MAP_W and 0 <= ty < MAP_H:
            return world[ty][tx]
        return -1

    def can_drive(ax, ay):
        tx, ty = int(ax // TILE), int(ay // TILE)
        t = world_at(tx, ty)
        return t in (1, 2)

    def can_walk(ax, ay):
        tx, ty = int(ax // TILE), int(ay // TILE)
        return 0 <= tx < MAP_W and 0 <= ty < MAP_H

    running = True
    while running:
        dt = 1
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
                    tx, ty = int(px // TILE), int(py // TILE)
                    t = world_at(tx, ty)
                    if t == 3:
                        menu = "bank"
                    elif t == 4:
                        menu = "job"
                    elif t == 5:
                        menu = "stock"
                    elif t == 6:
                        menu = "store"
                    elif in_car and can_walk(px, py):
                        in_car = False
                        px, py = car_x, car_y
                    elif not in_car and can_drive(car_x, car_y) and math.hypot(px - car_x, py - car_y) < TILE * 1.5:
                        in_car = True
                        px, py = car_x, car_y
                if menu == "bank":
                    if event.key == pygame.K_1:
                        amt = min(cash, 100)
                        cash -= amt
                        bank += amt
                    if event.key == pygame.K_2:
                        amt = min(bank, 100)
                        bank -= amt
                        cash += amt
                if menu == "job" and event.key == pygame.K_1 and job_timer == 0:
                    job_timer = 300
                    menu = None
                if menu == "stock":
                    if event.key == pygame.K_1:
                        c = COMPANIES[0]
                        if cash >= STOCK_PRICES[c] and STOCK_PRICES[c] > 0:
                            cash -= STOCK_PRICES[c]
                            STOCK_HOLDINGS[c] = STOCK_HOLDINGS.get(c, 0) + 1
                    if event.key == pygame.K_2:
                        c = COMPANIES[0]
                        if STOCK_HOLDINGS.get(c, 0) > 0:
                            STOCK_HOLDINGS[c] -= 1
                            cash += STOCK_PRICES[c]

        if not running:
            break

        # Update stock prices
        stock_tick += 1
        if stock_tick >= 120:
            stock_tick = 0
            for c in COMPANIES:
                STOCK_PRICES[c] = max(10, STOCK_PRICES[c] * random.uniform(0.92, 1.1))

        if crash_cooldown > 0:
            crash_cooldown -= 1

        if not menu:
            if in_car:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    car_angle -= car_turn
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    car_angle += car_turn
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    car_speed = min(car_max, car_speed + car_accel)
                if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    car_speed = max(-car_max * 0.5, car_speed - car_accel)
                car_speed *= car_friction
                if car_speed != 0:
                    rad = math.radians(car_angle)
                    car_x += math.cos(rad) * car_speed * 4
                    car_y += math.sin(rad) * car_speed * 4
                car_x = max(TILE, min(MAP_W * TILE - TILE, car_x))
                car_y = max(TILE, min(MAP_H * TILE - TILE, car_y))
                if not can_drive(car_x, car_y):
                    car_speed *= -0.5
                    crash_cooldown = 30
                px, py = car_x, car_y
            else:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    py -= walk_speed
                if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    py += walk_speed
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    px -= walk_speed
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    px += walk_speed
                px = max(0, min(MAP_W * TILE, px))
                py = max(0, min(MAP_H * TILE, py))

            # Job timer
            if job_timer > 0:
                job_timer -= 1
                if job_timer == 0:
                    cash += job_earn
            # NPCs
            for n in npcs:
                n["x"] += n["vx"]
                n["y"] += n["vy"]
                if n["x"] < TILE or n["x"] > (MAP_W - 1) * TILE:
                    n["vx"] *= -1
                if n["y"] < TILE or n["y"] > (MAP_H - 1) * TILE:
                    n["vy"] *= -1
            for oc in other_cars:
                oc["x"] += oc["vx"]
                if oc["x"] > MAP_W * TILE:
                    oc["x"] = 0
                if oc["x"] < 0:
                    oc["x"] = (MAP_W - 1) * TILE
                if in_car and crash_cooldown == 0 and abs(car_x - oc["x"]) < TILE and abs(car_y - oc["y"]) < TILE * 1.2:
                    car_speed *= -0.3
                    crash_cooldown = 60

        cam_x += (px - cam_x - W // 2) * 0.08
        cam_y += (py - cam_y - H // 2) * 0.08
        cam_x = max(0, min(MAP_W * TILE - W, cam_x))
        cam_y = max(0, min(MAP_H * TILE - H, cam_y))

        # Draw
        screen.fill(SKY)
        for ty in range(MAP_H):
            for tx in range(MAP_W):
                t = world[ty][tx]
                rx = tx * TILE - cam_x
                ry = ty * TILE - cam_y
                if rx < -TILE or ry < -TILE or rx > W + TILE or ry > H + TILE:
                    continue
                if t == 0:
                    pygame.draw.rect(screen, GRASS, (rx, ry, TILE + 1, TILE + 1))
                elif t == 1:
                    pygame.draw.rect(screen, ROAD, (rx, ry, TILE + 1, TILE + 1))
                    pygame.draw.line(screen, ROAD_LINE, (rx + TILE // 2, ry), (rx + TILE // 2, ry + TILE))
                elif t == 2:
                    pygame.draw.rect(screen, (40, 40, 50), (rx, ry, TILE + 1, TILE + 1))
                    for i in range(0, TILE, 8):
                        pygame.draw.line(screen, ROAD_LINE, (rx, ry + i), (rx + TILE, ry + i))
                elif t == 3:
                    pygame.draw.rect(screen, BANK_COL, (rx, ry, TILE + 1, TILE + 1))
                elif t == 4:
                    pygame.draw.rect(screen, JOB_COL, (rx, ry, TILE + 1, TILE + 1))
                elif t == 5:
                    pygame.draw.rect(screen, STOCK_COL, (rx, ry, TILE + 1, TILE + 1))
                elif t == 6:
                    pygame.draw.rect(screen, STORE_COL, (rx, ry, TILE + 1, TILE + 1))

        for oc in other_cars:
            ox = oc["x"] - cam_x
            oy = oc["y"] - cam_y
            if -TILE < ox < W + TILE and -TILE < oy < H + TILE:
                pygame.draw.rect(screen, NPC_CAR, (ox - 12, oy - 18, 24, 36))
        for n in npcs:
            nx = n["x"] - cam_x
            ny = n["y"] - cam_y
            if -20 < nx < W + 20 and -20 < ny < H + 20:
                pygame.draw.circle(screen, MUTED, (int(nx), int(ny)), 8)

        if in_car:
            draw_x = car_x - cam_x
            draw_y = car_y - cam_y
            pygame.draw.rect(screen, PLAYER_CAR, (draw_x - 14, draw_y - 20, 28, 40))
        else:
            pygame.draw.circle(screen, PLAYER_FOOT, (int(px - cam_x), int(py - cam_y)), 12)

        # UI
        screen.blit(font.render(f"Cash: ${cash}  Bank: ${bank}", True, TEXT), (10, 10))
        screen.blit(font_small.render("E: enter building / get in or out of car", True, MUTED), (10, H - 50))
        if menu:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            if menu == "bank":
                screen.blit(font.render("BANK - 1: Deposit $100  2: Withdraw $100  ESC: Close", True, TEXT), (W // 2 - 200, H // 2 - 20))
            if menu == "job":
                screen.blit(font.render("JOB - 1: Work for $50 (wait for timer)  ESC: Close", True, TEXT), (W // 2 - 240, H // 2 - 20))
            if menu == "stock":
                screen.blit(font.render("STOCKS - 1: Buy " + COMPANIES[0] + "  2: Sell  ESC: Close", True, TEXT), (W // 2 - 180, H // 2 - 40))
                screen.blit(font_small.render(f"Price: ${STOCK_PRICES[COMPANIES[0]]:.1f}  You own: {STOCK_HOLDINGS.get(COMPANIES[0], 0)}", True, MUTED), (W // 2 - 120, H // 2))
            if menu == "store":
                screen.blit(font.render("STORE - Coming soon. ESC: Close", True, TEXT), (W // 2 - 120, H // 2 - 20))

        pygame.display.flip()
        clock.tick(FPS)

    save_save(cash, bank, STOCK_HOLDINGS, STOCK_PRICES)
    pygame.quit()


if __name__ == "__main__":
    main()
