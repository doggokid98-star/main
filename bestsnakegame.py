"""
╔══════════════════════════════════════════════╗
║   MEGA HUB SNAKE RPG / CITY SIMULATOR        ║
║   Built with Python + Pygame                 ║
╚══════════════════════════════════════════════╝

Install:  pip install pygame
Run:      python mega_hub_snake.py
"""

import pygame
import sys
import random
import math
import json
import os
import time

# ─── Init ─────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

W, H = 1000, 700
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("MEGA HUB — Snake RPG City Simulator")
clock = pygame.time.Clock()
FPS = 60

# ─── Colours ──────────────────────────────────────────────────────────────────
BLACK   = (0, 0, 0)
WHITE   = (255, 255, 255)
CYAN    = (0, 229, 255)
PURPLE  = (124, 58, 237)
GREEN   = (34, 197, 94)
RED     = (239, 68, 68)
YELLOW  = (250, 204, 21)
ORANGE  = (249, 115, 22)
BLUE    = (59, 130, 246)
GRAY    = (107, 114, 128)
DGRAY   = (31, 41, 55)
BGDARK  = (8, 11, 16)
SURFACE = (13, 17, 23)
SURFACE2= (22, 27, 36)
ROAD    = (40, 44, 52)
SIDEWALK= (80, 85, 95)
GRASS   = (34, 85, 34)
BUILDG  = (25, 35, 55)
BUILDG2 = (40, 55, 80)
NEONPINK= (255, 20, 147)
GOLD    = (255, 215, 0)

# ─── Fonts ────────────────────────────────────────────────────────────────────
try:
    FONT_BIG   = pygame.font.SysFont("consolas", 48, bold=True)
    FONT_MED   = pygame.font.SysFont("consolas", 28, bold=True)
    FONT_SM    = pygame.font.SysFont("consolas", 18)
    FONT_XS    = pygame.font.SysFont("consolas", 13)
    FONT_TITLE = pygame.font.SysFont("consolas", 64, bold=True)
except:
    FONT_BIG   = pygame.font.Font(None, 48)
    FONT_MED   = pygame.font.Font(None, 28)
    FONT_SM    = pygame.font.Font(None, 18)
    FONT_XS    = pygame.font.Font(None, 13)
    FONT_TITLE = pygame.font.Font(None, 64)

# ─── Save/Load ────────────────────────────────────────────────────────────────
SAVE_FILE = "nova_save.json"

def default_state():
    return {
        "money": 100,
        "bank": 0,
        "debt": 0,
        "social_credit": 50,
        "highscore": 0,
        "skin": 0,
    }

def load_state():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE) as f:
                d = json.load(f)
                base = default_state()
                base.update(d)
                return base
        except:
            pass
    return default_state()

def save_state(gs):
    with open(SAVE_FILE, "w") as f:
        json.dump({k: gs[k] for k in default_state()}, f, indent=2)

# ─── Global game state ────────────────────────────────────────────────────────
gs = load_state()
MODE = "HUB"          # HUB | SNAKE | MINI | CITY | BANK | SHOP | JOB
PREV_MODE = "HUB"
tick = 0              # global animation tick

SNAKE_SKINS = [
    [GREEN, (20, 150, 20)],
    [CYAN,  (0, 120, 180)],
    [NEONPINK, (150, 0, 80)],
    [GOLD,  (200, 160, 0)],
]

# ─── Helpers ──────────────────────────────────────────────────────────────────

def draw_rect_alpha(surf, color, rect, alpha=180, radius=6):
    s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, alpha), (0, 0, rect[2], rect[3]), border_radius=radius)
    surf.blit(s, (rect[0], rect[1]))

def draw_text(surf, text, font, color, cx, cy, anchor="center"):
    t = font.render(str(text), True, color)
    r = t.get_rect()
    if anchor == "center": r.center = (cx, cy)
    elif anchor == "topleft": r.topleft = (cx, cy)
    elif anchor == "topright": r.topright = (cx, cy)
    surf.blit(t, r)

def glow_color(base, t, speed=0.05, lo=0.6, hi=1.0):
    f = lo + (hi-lo) * (0.5 + 0.5*math.sin(t*speed))
    return tuple(min(255, int(c*f)) for c in base)

def pulse_size(base, t, speed=0.08, amount=3):
    return base + int(amount * math.sin(t * speed))

def draw_hud(surf):
    """Always-visible HUD bar at bottom."""
    pygame.draw.rect(surf, SURFACE, (0, H-44, W, 44))
    pygame.draw.line(surf, DGRAY, (0, H-44), (W, H-44), 1)
    items = [
        ("💰", f"${gs['money']}", GREEN),
        ("🏦", f"${gs['bank']}", CYAN),
        ("💳", f"-${gs['debt']}", RED if gs['debt']>0 else GRAY),
        ("⭐", f"{gs['social_credit']}/100", YELLOW),
        ("🏆", f"HI:{gs['highscore']}", PURPLE),
    ]
    for i, (icon, val, col) in enumerate(items):
        x = 30 + i*190
        draw_text(surf, icon, FONT_XS, WHITE, x, H-22, "center")
        draw_text(surf, val, FONT_XS, col, x+18, H-22, "topleft")

# ══════════════════════════════════════════════════════════════════════════════
# HUB MODE
# ══════════════════════════════════════════════════════════════════════════════

class HubMenu:
    OPTIONS = [
        ("🐍 SNAKE",    "SNAKE", CYAN),
        ("🏙 CITY",     "CITY",  GREEN),
        ("🎮 MINI-GAMES","MINI", PURPLE),
        ("🏦 BANK",     "BANK",  YELLOW),
        ("🛒 SHOP",     "SHOP",  ORANGE),
        ("💼 JOBS",     "JOB",   NEONPINK),
    ]

    def __init__(self):
        self.sel = 0
        self.particles = [self._new_particle() for _ in range(60)]

    def _new_particle(self):
        return {
            "x": random.randint(0, W),
            "y": random.randint(0, H),
            "vx": random.uniform(-0.3, 0.3),
            "vy": random.uniform(-0.5, -0.1),
            "r": random.randint(1, 3),
            "col": random.choice([CYAN, PURPLE, GREEN, NEONPINK]),
            "life": random.randint(0, 200),
        }

    def update(self):
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] += 1
            if p["y"] < -10 or p["life"] > 300:
                p.update(self._new_particle())

    def handle(self, event):
        global MODE
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel - 1) % len(self.OPTIONS)
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel + 1) % len(self.OPTIONS)
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.sel = (self.sel - 2) % len(self.OPTIONS)
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                self.sel = (self.sel + 2) % len(self.OPTIONS)
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                MODE = self.OPTIONS[self.sel][1]
                return True
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for i, rect in enumerate(self._card_rects()):
                if rect.collidepoint(mx, my):
                    self.sel = i
                    MODE = self.OPTIONS[i][1]
                    return True
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for i, rect in enumerate(self._card_rects()):
                if rect.collidepoint(mx, my):
                    self.sel = i
        return False

    def _card_rects(self):
        rects = []
        cols, rows = 3, 2
        cw, ch = 260, 120
        sx = (W - cols*cw - (cols-1)*16) // 2
        sy = 300
        for i in range(len(self.OPTIONS)):
            r, c = divmod(i, cols)
            rects.append(pygame.Rect(sx + c*(cw+16), sy + r*(ch+14), cw, ch))
        return rects

    def draw(self, surf):
        # Background
        surf.fill(BGDARK)
        # Particles
        for p in self.particles:
            alpha = min(255, p["life"] if p["life"] < 150 else 300-p["life"])
            draw_rect_alpha(surf, p["col"], (int(p["x"]), int(p["y"]), p["r"]*2, p["r"]*2), alpha)
        # Title
        t_col = glow_color(CYAN, tick, 0.04)
        draw_text(surf, "MEGA", FONT_TITLE, t_col, W//2, 90, "center")
        draw_text(surf, "HUB", FONT_TITLE, glow_color(PURPLE, tick+30, 0.04), W//2, 150, "center")
        draw_text(surf, "Snake RPG · City Simulator", FONT_SM, GRAY, W//2, 210, "center")
        draw_text(surf, "↑↓←→ navigate  ·  ENTER select  ·  mouse click", FONT_XS, GRAY, W//2, 240, "center")
        # Cards
        rects = self._card_rects()
        for i, (label, _, col) in enumerate(self.OPTIONS):
            r = rects[i]
            selected = i == self.sel
            alpha = 220 if selected else 140
            draw_rect_alpha(surf, col if selected else SURFACE2, (r.x, r.y, r.w, r.h), alpha, 12)
            if selected:
                pygame.draw.rect(surf, col, r, 2, border_radius=12)
            draw_text(surf, label, FONT_MED, WHITE if selected else GRAY, r.centerx, r.centery, "center")


# ══════════════════════════════════════════════════════════════════════════════
# SNAKE MODE
# ══════════════════════════════════════════════════════════════════════════════

CELL = 20
COLS = (W - 10) // CELL
ROWS = (H - 80) // CELL
SX = 5   # snake grid origin x
SY = 5   # snake grid origin y

class SnakeGame:
    POWERUPS = ["⚡", "🛡", "💎"]

    def __init__(self):
        self.reset()

    def reset(self):
        cx, cy = COLS//2, ROWS//2
        self.body = [(cx, cy), (cx-1, cy), (cx-2, cy)]
        self.dir = (1, 0)
        self.next_dir = (1, 0)
        self.food = self._spawn()
        self.powerup = None
        self.pu_timer = 0
        self.score = 0
        self.dead = False
        self.move_timer = 0
        self.move_delay = 120   # ms between moves
        self.trail = []
        self.particles = []
        self.active_pu = None
        self.pu_active_timer = 0
        self.paused = False

    def _spawn(self):
        while True:
            pos = (random.randint(1, COLS-2), random.randint(1, ROWS-2))
            if pos not in self.body:
                return pos

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "HUB"
            if event.key == pygame.K_p:
                self.paused = not self.paused
            dirs = {
                pygame.K_UP:    (0,-1), pygame.K_w: (0,-1),
                pygame.K_DOWN:  (0, 1), pygame.K_s: (0, 1),
                pygame.K_LEFT:  (-1,0), pygame.K_a: (-1,0),
                pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
            }
            if event.key in dirs:
                nd = dirs[event.key]
                if (nd[0] != -self.dir[0] or nd[1] != -self.dir[1]):
                    self.next_dir = nd
            if self.dead and event.key == pygame.K_r:
                self.reset()
        return None

    def update(self, dt):
        if self.dead or self.paused:
            return
        self.move_timer += dt
        speed = self.move_delay * (0.6 if self.active_pu == "⚡" else 1.0)
        if self.move_timer < speed:
            return
        self.move_timer = 0
        self.dir = self.next_dir

        hx, hy = self.body[0]
        nx, ny = hx + self.dir[0], hy + self.dir[1]

        # Wall collision (shield blocks once)
        if nx < 0 or nx >= COLS or ny < 0 or ny >= ROWS:
            if self.active_pu == "🛡":
                nx = max(0, min(COLS-1, nx))
                ny = max(0, min(ROWS-1, ny))
                self.active_pu = None
            else:
                self._die()
                return

        # Self collision
        if (nx, ny) in self.body[1:]:
            if self.active_pu != "🛡":
                self._die()
                return
            self.active_pu = None
            return

        self.body.insert(0, (nx, ny))
        self.trail.append({"pos": (nx*CELL+SX, ny*CELL+SY), "life": 0})

        # Eat food
        if (nx, ny) == self.food:
            self.score += 10
            self._food_burst(nx, ny)
            self.food = self._spawn()
            gs["money"] = min(gs["money"] + 2, 99999)
            gs["social_credit"] = min(100, gs["social_credit"] + 1)
            if self.score > gs["highscore"]:
                gs["highscore"] = self.score
            # Spawn powerup occasionally
            if random.random() < 0.25 and self.powerup is None:
                self.powerup = self._spawn()
                self.pu_timer = 300
                self.pu_type = random.choice(self.POWERUPS)
        else:
            self.body.pop()

        # Eat powerup
        if self.powerup and (nx, ny) == self.powerup:
            self.active_pu = self.pu_type
            self.pu_active_timer = 400
            self.powerup = None
            gs["money"] = min(gs["money"] + 10, 99999)

        # Powerup timer
        if self.powerup:
            self.pu_timer -= 1
            if self.pu_timer <= 0:
                self.powerup = None

        if self.active_pu:
            self.pu_active_timer -= 1
            if self.pu_active_timer <= 0:
                self.active_pu = None

        # Update particles
        for p in self.trail:
            p["life"] += 1
        self.trail = [p for p in self.trail if p["life"] < 18]
        for p in self.particles:
            p["x"] += p["vx"]; p["y"] += p["vy"]; p["life"] += 1
        self.particles = [p for p in self.particles if p["life"] < 30]

    def _food_burst(self, gx, gy):
        for _ in range(12):
            self.particles.append({
                "x": gx*CELL+SX+CELL//2, "y": gy*CELL+SY+CELL//2,
                "vx": random.uniform(-3,3), "vy": random.uniform(-3,3),
                "col": random.choice([YELLOW, ORANGE, WHITE]),
                "life": 0,
            })

    def _die(self):
        self.dead = True
        save_state(gs)

    def draw(self, surf):
        surf.fill(BGDARK)
        # Grid
        for x in range(COLS):
            for y in range(ROWS):
                r = pygame.Rect(SX + x*CELL, SY + y*CELL, CELL-1, CELL-1)
                pygame.draw.rect(surf, SURFACE, r)

        skin = SNAKE_SKINS[gs["skin"] % len(SNAKE_SKINS)]

        # Trail
        for p in self.trail:
            alpha = max(0, 80 - p["life"]*5)
            draw_rect_alpha(surf, skin[0], (p["pos"][0], p["pos"][1], CELL-1, CELL-1), alpha, 4)

        # Snake body
        for i, (bx, by) in enumerate(self.body):
            r = pygame.Rect(SX + bx*CELL + 1, SY + by*CELL + 1, CELL-3, CELL-3)
            col = skin[0] if i == 0 else skin[1]
            wave = int(2 * math.sin(tick*0.1 + i*0.4))
            r.inflate_ip(wave, wave)
            pygame.draw.rect(surf, col, r, border_radius=5)
            if i == 0:
                pygame.draw.rect(surf, glow_color(WHITE, tick, 0.05), r, 1, border_radius=5)

        # Food
        fx, fy = self.food
        gs_size = pulse_size(CELL-4, tick)
        fc = glow_color(RED, tick, 0.07)
        fr = pygame.Rect(SX+fx*CELL+(CELL-gs_size)//2, SY+fy*CELL+(CELL-gs_size)//2, gs_size, gs_size)
        pygame.draw.rect(surf, fc, fr, border_radius=gs_size//2)
        # glow ring
        pygame.draw.rect(surf, (*fc, 80), fr.inflate(6, 6), 2, border_radius=gs_size//2+3)

        # Powerup
        if self.powerup:
            px, py = self.powerup
            pc = glow_color(GOLD, tick, 0.08)
            pr = pygame.Rect(SX+px*CELL, SY+py*CELL, CELL, CELL)
            pygame.draw.rect(surf, pc, pr, border_radius=4)
            draw_text(surf, self.pu_type, FONT_XS, WHITE, pr.centerx, pr.centery, "center")

        # Particles
        for p in self.particles:
            a = max(0, 255 - p["life"]*8)
            draw_rect_alpha(surf, p["col"], (int(p["x"]), int(p["y"]), 4, 4), a, 2)

        # Score HUD (top)
        pygame.draw.rect(surf, SURFACE, (0, 0, W, SY))
        draw_text(surf, f"SCORE: {self.score}", FONT_SM, CYAN, 10, SY//2, "topleft")
        draw_text(surf, f"HI: {gs['highscore']}", FONT_SM, YELLOW, 200, SY//2, "topleft")
        if self.active_pu:
            draw_text(surf, f"POWER: {self.active_pu} ({self.pu_active_timer})", FONT_SM, NEONPINK, W//2, SY//2, "center")
        draw_text(surf, "[ESC] Menu  [P] Pause  [R] Restart", FONT_XS, GRAY, W-10, SY//2, "topright")

        if self.paused:
            draw_rect_alpha(surf, BLACK, (0, 0, W, H), 160)
            draw_text(surf, "PAUSED", FONT_BIG, CYAN, W//2, H//2-20, "center")
            draw_text(surf, "Press P to resume", FONT_SM, GRAY, W//2, H//2+40, "center")

        if self.dead:
            draw_rect_alpha(surf, BLACK, (0, 0, W, H), 170)
            draw_text(surf, "GAME OVER", FONT_BIG, RED, W//2, H//2-50, "center")
            draw_text(surf, f"Score: {self.score}  |  Best: {gs['highscore']}", FONT_MED, WHITE, W//2, H//2+10, "center")
            draw_text(surf, "Press R to restart  |  ESC for menu", FONT_SM, GRAY, W//2, H//2+60, "center")


# ══════════════════════════════════════════════════════════════════════════════
# CITY MODE
# ══════════════════════════════════════════════════════════════════════════════

class Car:
    def __init__(self):
        self.reset()

    def reset(self):
        self.lane = random.randint(0, 1)
        self.y = 160 + self.lane * 28
        self.x = -60 if random.random() > 0.5 else W+60
        self.speed = random.uniform(2, 5) * (1 if self.x < 0 else -1)
        self.col = random.choice([RED, BLUE, YELLOW, WHITE, ORANGE, CYAN])
        self.w = random.randint(40, 60)

    def update(self):
        self.x += self.speed
        if self.x > W+80 or self.x < -80:
            self.reset()

    def draw(self, surf):
        r = pygame.Rect(int(self.x), self.y, self.w, 18)
        pygame.draw.rect(surf, self.col, r, border_radius=4)
        # windows
        pygame.draw.rect(surf, (180,220,255), (int(self.x)+6, self.y+3, 12, 10), border_radius=2)
        pygame.draw.rect(surf, (180,220,255), (int(self.x)+22, self.y+3, 10, 10), border_radius=2)


class Pedestrian:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(0, W)
        self.y = random.randint(220, 250)
        self.speed = random.uniform(0.5, 1.5) * random.choice([-1, 1])
        self.col = random.choice([RED, BLUE, GREEN, YELLOW, PURPLE, CYAN, ORANGE, WHITE])
        self.frame = 0
        self.anim = 0

    def update(self):
        self.x += self.speed
        self.anim += 1
        self.frame = int(self.anim / 10) % 4
        if self.x > W+20 or self.x < -20:
            self.reset()

    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        # body
        pygame.draw.circle(surf, self.col, (x, y-12), 5)
        pygame.draw.line(surf, self.col, (x, y-7), (x, y+4), 2)
        # legs
        swing = int(4*math.sin(self.anim*0.3))
        pygame.draw.line(surf, self.col, (x, y+4), (x-swing, y+12), 2)
        pygame.draw.line(surf, self.col, (x, y+4), (x+swing, y+12), 2)
        # arms
        pygame.draw.line(surf, self.col, (x, y-4), (x-swing, y+1), 2)
        pygame.draw.line(surf, self.col, (x, y-4), (x+swing, y+1), 2)


BUILDINGS = [
    {"x": 20,  "w": 90,  "h": 130, "col": BUILDG,  "name": "BANK",       "mode": "BANK"},
    {"x": 130, "w": 80,  "h": 100, "col": BUILDG2, "name": "SHOP",       "mode": "SHOP"},
    {"x": 230, "w": 100, "h": 145, "col": (20,50,70),"name": "ARCADE",   "mode": "MINI"},
    {"x": 350, "w": 85,  "h": 110, "col": (40,30,60),"name": "JOBS",     "mode": "JOB"},
    {"x": 460, "w": 70,  "h": 95,  "col": BUILDG,  "name": "HOTEL",      "mode": None},
    {"x": 550, "w": 110, "h": 155, "col": (30,55,45),"name": "CITY HALL","mode": None},
    {"x": 680, "w": 80,  "h": 120, "col": BUILDG2, "name": "MARKET",     "mode": "SHOP"},
    {"x": 780, "w": 90,  "h": 140, "col": (50,30,30),"name": "CASINO",   "mode": "MINI"},
    {"x": 890, "w": 80,  "h": 100, "col": BUILDG,  "name": "PARK",       "mode": None},
]

class CityMode:
    GROUND_Y = 270  # feet of player

    def __init__(self):
        self.px = W//2
        self.py = self.GROUND_Y
        self.speed = 3
        self.cars = [Car() for _ in range(8)]
        self.peds = [Pedestrian() for _ in range(10)]
        self.anim = 0
        self.facing = 1
        self.msg = ""
        self.msg_timer = 0
        self.near_building = None

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "HUB"
            if event.key in (pygame.K_RETURN, pygame.K_e) and self.near_building:
                if self.near_building["mode"]:
                    return self.near_building["mode"]
        return None

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.px -= self.speed
            self.facing = -1
            self.anim += 1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.px += self.speed
            self.facing = 1
            self.anim += 1
        else:
            self.anim = 0
        self.px = max(20, min(W-20, self.px))

        for c in self.cars: c.update()
        for p in self.peds: p.update()

        # Check near building
        self.near_building = None
        for b in BUILDINGS:
            door_x = b["x"] + b["w"]//2
            door_y = H - 44 - 10  # ground level
            bx = b["x"]
            by = H - 44 - b["h"]
            if abs(self.px - door_x) < 40 and abs(self.py - self.GROUND_Y) < 20:
                self.near_building = b

        if self.msg_timer > 0:
            self.msg_timer -= 1

    def _draw_building(self, surf, b):
        bx = b["x"]
        by = H - 44 - b["h"]
        bw, bh = b["w"], b["h"]
        # Main structure
        pygame.draw.rect(surf, b["col"], (bx, by, bw, bh))
        pygame.draw.rect(surf, tuple(min(255, c+30) for c in b["col"]), (bx, by, bw, bh), 2)
        # Windows
        wrows = bh // 22
        wcols = bw // 20
        for wr in range(1, wrows):
            for wc in range(wcols):
                wx = bx + 6 + wc*18
                wy = by + 8 + wr*18
                if wx + 10 < bx + bw - 4:
                    lit = (tick//30 + wr*3 + wc*7) % 5 != 0
                    wcol = (255,240,180) if lit else (20,30,50)
                    pygame.draw.rect(surf, wcol, (wx, wy, 10, 12), border_radius=1)
        # Door
        dx = bx + bw//2 - 8
        dy = H - 44 - 26
        pygame.draw.rect(surf, (60, 40, 20), (dx, dy, 16, 26), border_radius=2)
        # Name sign
        draw_text(surf, b["name"], FONT_XS, CYAN, bx + bw//2, by + 12, "center")

    def draw(self, surf):
        # Sky gradient
        for y in range(H - 44):
            r = int(8 + y*0.04)
            g = int(11 + y*0.05)
            b = int(16 + y*0.08)
            pygame.draw.line(surf, (r, g, b), (0, y), (W, y))

        # Stars
        for i in range(40):
            sx = (i * 137 + 50) % W
            sy = (i * 97 + 20) % 100
            a = int(120 + 80 * math.sin(tick*0.03 + i))
            draw_rect_alpha(surf, WHITE, (sx, sy, 2, 2), a)

        # Buildings (back layer)
        for b in BUILDINGS:
            self._draw_building(surf, b)

        # Road
        pygame.draw.rect(surf, ROAD, (0, 145, W, 80))
        # Lane markings
        for x in range(0, W, 50):
            off = (tick*2) % 50
            pygame.draw.rect(surf, GRAY, (x - off, 183, 30, 4))

        # Sidewalk
        pygame.draw.rect(surf, SIDEWALK, (0, 225, W, 50))
        # Sidewalk tiles
        for x in range(0, W, 30):
            pygame.draw.line(surf, (90, 95, 105), (x, 225), (x, 275), 1)

        # Cars
        for c in self.cars:
            c.draw(surf)

        # Pedestrians (behind player)
        for p in self.peds:
            if p.y > self.py:
                p.draw(surf)

        # Player
        px, py = int(self.px), int(self.py)
        # Body
        pygame.draw.circle(surf, CYAN, (px, py-22), 8)  # head
        pygame.draw.line(surf, CYAN, (px, py-14), (px, py-2), 3)  # torso
        # Legs
        leg = int(5*math.sin(self.anim*0.25))
        pygame.draw.line(surf, CYAN, (px, py-2), (px-leg, py+10), 2)
        pygame.draw.line(surf, CYAN, (px, py-2), (px+leg, py+10), 2)
        # Arms
        pygame.draw.line(surf, CYAN, (px, py-10), (px-5+leg, py-4), 2)
        pygame.draw.line(surf, CYAN, (px, py-10), (px+5-leg, py-4), 2)

        # Pedestrians (in front of player)
        for p in self.peds:
            if p.y <= self.py:
                p.draw(surf)

        # Near building prompt
        if self.near_building:
            name = self.near_building["name"]
            draw_rect_alpha(surf, SURFACE, (W//2-130, 290, 260, 36), 200, 8)
            if self.near_building["mode"]:
                draw_text(surf, f"[E/ENTER] Enter {name}", FONT_SM, YELLOW, W//2, 308, "center")
            else:
                draw_text(surf, f"{name} (coming soon)", FONT_SM, GRAY, W//2, 308, "center")

        draw_text(surf, "[ESC] Hub  [←→] Move  [E] Enter Building", FONT_XS, GRAY, W//2, 130, "center")


# ══════════════════════════════════════════════════════════════════════════════
# BANK MODE
# ══════════════════════════════════════════════════════════════════════════════

class BankMode:
    OPTS = ["Deposit", "Withdraw", "Borrow", "Pay Debt", "Back"]

    def __init__(self):
        self.sel = 0
        self.amount_str = ""
        self.entering = False
        self.msg = ""
        self.msg_col = GREEN
        self.msg_timer = 0

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if self.entering:
                if event.key == pygame.K_BACKSPACE:
                    self.amount_str = self.amount_str[:-1]
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._do_action()
                    self.entering = False
                    self.amount_str = ""
                elif event.unicode.isdigit():
                    if len(self.amount_str) < 8:
                        self.amount_str += event.unicode
            else:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.sel = (self.sel-1) % len(self.OPTS)
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    self.sel = (self.sel+1) % len(self.OPTS)
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.OPTS[self.sel] == "Back":
                        return "HUB"
                    self.entering = True
                if event.key == pygame.K_ESCAPE:
                    return "HUB"
        return None

    def _do_action(self):
        try:
            amt = int(self.amount_str)
        except:
            self._msg("Invalid amount!", RED)
            return
        if amt <= 0:
            self._msg("Amount must be > 0", RED)
            return
        action = self.OPTS[self.sel]
        if action == "Deposit":
            if amt > gs["money"]:
                self._msg("Not enough cash!", RED)
            else:
                gs["money"] -= amt
                gs["bank"] += amt
                self._msg(f"+${amt} deposited!", GREEN)
                gs["social_credit"] = min(100, gs["social_credit"]+2)
        elif action == "Withdraw":
            if amt > gs["bank"]:
                self._msg("Not enough in bank!", RED)
            else:
                gs["bank"] -= amt
                gs["money"] += amt
                self._msg(f"${amt} withdrawn!", CYAN)
        elif action == "Borrow":
            limit = max(0, gs["social_credit"] * 20)
            if gs["debt"] + amt > limit:
                self._msg(f"Credit limit: ${limit}!", RED)
            else:
                gs["money"] += amt
                gs["debt"] += amt
                self._msg(f"Borrowed ${amt}! Repay soon.", YELLOW)
                gs["social_credit"] = max(0, gs["social_credit"]-3)
        elif action == "Pay Debt":
            pay = min(amt, gs["debt"])
            if gs["money"] < pay:
                self._msg("Not enough cash!", RED)
            else:
                gs["money"] -= pay
                gs["debt"] -= pay
                self._msg(f"Paid ${pay} debt!", GREEN)
                gs["social_credit"] = min(100, gs["social_credit"]+5)
        save_state(gs)

    def _msg(self, text, col):
        self.msg = text
        self.msg_col = col
        self.msg_timer = 180

    def update(self):
        if self.msg_timer > 0:
            self.msg_timer -= 1

    def draw(self, surf):
        surf.fill(BGDARK)
        draw_text(surf, "🏦  CITY BANK", FONT_BIG, CYAN, W//2, 70, "center")
        # Stats
        draw_rect_alpha(surf, SURFACE2, (W//2-200, 120, 400, 110), 200, 10)
        draw_text(surf, f"Cash:    ${gs['money']}", FONT_SM, GREEN, W//2-80, 145, "topleft")
        draw_text(surf, f"Bank:    ${gs['bank']}", FONT_SM, CYAN, W//2-80, 170, "topleft")
        draw_text(surf, f"Debt:    ${gs['debt']}", FONT_SM, RED if gs['debt'] else GRAY, W//2-80, 195, "topleft")
        credit_limit = gs["social_credit"] * 20
        draw_text(surf, f"Credit limit: ${credit_limit}", FONT_XS, YELLOW, W//2, 215, "center")

        # Menu
        for i, opt in enumerate(self.OPTS):
            sel = i == self.sel
            col = YELLOW if sel else GRAY
            prefix = "▶ " if sel else "  "
            draw_text(surf, prefix + opt, FONT_MED, col, W//2, 310 + i*50, "center")

        if self.entering:
            draw_rect_alpha(surf, SURFACE, (W//2-150, 580, 300, 50), 230, 8)
            amt_disp = self.amount_str or "0"
            cursor = "_" if (tick//20)%2==0 else ""
            draw_text(surf, f"Amount: ${amt_disp}{cursor}", FONT_SM, WHITE, W//2, 605, "center")

        if self.msg_timer > 0:
            draw_rect_alpha(surf, SURFACE, (W//2-160, 640, 320, 36), 200, 8)
            draw_text(surf, self.msg, FONT_SM, self.msg_col, W//2, 658, "center")

        draw_text(surf, "[↑↓] Navigate  [ENTER] Select  [ESC] Back", FONT_XS, GRAY, W//2, H-60, "center")


# ══════════════════════════════════════════════════════════════════════════════
# SHOP MODE
# ══════════════════════════════════════════════════════════════════════════════

SHOP_ITEMS = [
    {"name": "Cyan Snake Skin",   "price": 50,  "type": "skin", "val": 1, "emoji": "🐍"},
    {"name": "Pink Snake Skin",   "price": 80,  "type": "skin", "val": 2, "emoji": "💜"},
    {"name": "Gold Snake Skin",   "price": 150, "type": "skin", "val": 3, "emoji": "⭐"},
    {"name": "Speed Boost",       "price": 30,  "type": "credit","val": 5,  "emoji": "⚡"},
    {"name": "+10 Social Credit", "price": 20,  "type": "credit","val": 10, "emoji": "❤️"},
    {"name": "Back",              "price": 0,   "type": "back",  "val": 0,  "emoji": "🔙"},
]

class ShopMode:
    def __init__(self):
        self.sel = 0
        self.msg = ""
        self.msg_col = GREEN
        self.msg_timer = 0

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel-1) % len(SHOP_ITEMS)
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel+1) % len(SHOP_ITEMS)
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                item = SHOP_ITEMS[self.sel]
                if item["type"] == "back":
                    return "HUB"
                self._buy(item)
            if event.key == pygame.K_ESCAPE:
                return "HUB"
        return None

    def _buy(self, item):
        if gs["money"] < item["price"]:
            self.msg = "Not enough money!"; self.msg_col = RED
        else:
            gs["money"] -= item["price"]
            if item["type"] == "skin":
                gs["skin"] = item["val"]
                self.msg = f"Bought {item['name']}!"; self.msg_col = GREEN
            elif item["type"] == "credit":
                gs["social_credit"] = min(100, gs["social_credit"] + item["val"])
                self.msg = f"+{item['val']} social credit!"; self.msg_col = CYAN
        self.msg_timer = 150
        save_state(gs)

    def update(self):
        if self.msg_timer > 0: self.msg_timer -= 1

    def draw(self, surf):
        surf.fill(BGDARK)
        draw_text(surf, "🛒  CITY SHOP", FONT_BIG, ORANGE, W//2, 70, "center")
        draw_text(surf, f"Your cash: ${gs['money']}", FONT_SM, GREEN, W//2, 120, "center")

        for i, item in enumerate(SHOP_ITEMS):
            sel = i == self.sel
            y = 190 + i*68
            bw, bh = 500, 54
            bx = W//2 - bw//2
            draw_rect_alpha(surf, ORANGE if sel else SURFACE2, (bx, y, bw, bh), 180 if sel else 120, 10)
            if sel:
                pygame.draw.rect(surf, ORANGE, (bx, y, bw, bh), 2, border_radius=10)
            draw_text(surf, item["emoji"], FONT_MED, WHITE, bx+30, y+bh//2, "center")
            draw_text(surf, item["name"], FONT_SM, WHITE if sel else GRAY, bx+60, y+bh//2, "topleft")
            if item["price"] > 0:
                draw_text(surf, f"${item['price']}", FONT_SM, YELLOW, bx+bw-20, y+bh//2, "topright")

        if self.msg_timer > 0:
            draw_rect_alpha(surf, SURFACE, (W//2-160, 630, 320, 36), 200, 8)
            draw_text(surf, self.msg, FONT_SM, self.msg_col, W//2, 648, "center")

        draw_text(surf, "[↑↓] Navigate  [ENTER] Buy  [ESC] Back", FONT_XS, GRAY, W//2, H-60, "center")


# ══════════════════════════════════════════════════════════════════════════════
# JOBS MODE
# ══════════════════════════════════════════════════════════════════════════════

JOBS = [
    {"name": "📦 Delivery Run",   "pay": 25,  "credit": 5,  "time": 180, "desc": "Deliver 3 packages!"},
    {"name": "🍕 Pizza Maker",    "pay": 15,  "credit": 3,  "time": 120, "desc": "Make 5 pizzas!"},
    {"name": "🎰 Game Contest",   "pay": 40,  "credit": 8,  "time": 240, "desc": "Beat 3 rounds!"},
    {"name": "🧹 City Cleaner",   "pay": 10,  "credit": 10, "time": 90,  "desc": "Clean up city!"},
    {"name": "Back", "pay": 0, "credit": 0, "time": 0, "desc": ""},
]

class JobMode:
    def __init__(self):
        self.sel = 0
        self.working = False
        self.work_timer = 0
        self.work_job = None
        self.msg = ""
        self.msg_col = GREEN
        self.msg_timer = 0
        self.progress = 0

    def handle(self, event):
        if self.working:
            return None
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel-1) % len(JOBS)
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel+1) % len(JOBS)
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                job = JOBS[self.sel]
                if job["pay"] == 0:
                    return "HUB"
                self._start_job(job)
            if event.key == pygame.K_ESCAPE:
                return "HUB"
        return None

    def _start_job(self, job):
        self.working = True
        self.work_timer = job["time"]
        self.work_job = job
        self.progress = 0

    def update(self):
        if self.msg_timer > 0: self.msg_timer -= 1
        if self.working:
            self.work_timer -= 1
            self.progress = 1 - self.work_timer / self.work_job["time"]
            if self.work_timer <= 0:
                gs["money"] += self.work_job["pay"]
                gs["social_credit"] = min(100, gs["social_credit"] + self.work_job["credit"])
                self.msg = f"Job done! +${self.work_job['pay']}, +{self.work_job['credit']} SC"
                self.msg_col = GREEN
                self.msg_timer = 200
                self.working = False
                save_state(gs)

    def draw(self, surf):
        surf.fill(BGDARK)
        draw_text(surf, "💼  JOBS BOARD", FONT_BIG, NEONPINK, W//2, 70, "center")

        if self.working:
            job = self.work_job
            draw_text(surf, f"Working: {job['name']}", FONT_MED, WHITE, W//2, 180, "center")
            # Progress bar
            bw = 500
            bx = W//2-bw//2
            pygame.draw.rect(surf, SURFACE2, (bx, 240, bw, 30), border_radius=8)
            fw = int(bw * self.progress)
            if fw > 0:
                pygame.draw.rect(surf, NEONPINK, (bx, 240, fw, 30), border_radius=8)
            pct = int(self.progress*100)
            draw_text(surf, f"{pct}%", FONT_SM, WHITE, W//2, 255, "center")
            draw_text(surf, job["desc"], FONT_SM, GRAY, W//2, 300, "center")
            # Animated worker
            wx = W//2 + int(80 * math.sin(tick*0.05))
            wy = 400
            pygame.draw.circle(surf, CYAN, (wx, wy-20), 8)
            pygame.draw.line(surf, CYAN, (wx, wy-12), (wx, wy), 3)
            leg = int(6*math.sin(tick*0.15))
            pygame.draw.line(surf, CYAN, (wx, wy), (wx-leg, wy+12), 2)
            pygame.draw.line(surf, CYAN, (wx, wy), (wx+leg, wy+12), 2)
            draw_text(surf, "Working hard...", FONT_SM, GRAY, W//2, 430, "center")
            return

        for i, job in enumerate(JOBS):
            sel = i == self.sel
            y = 160 + i*80
            bw, bh = 520, 64
            bx = W//2 - bw//2
            draw_rect_alpha(surf, NEONPINK if sel else SURFACE2, (bx, y, bw, bh), 170 if sel else 110, 10)
            if sel:
                pygame.draw.rect(surf, NEONPINK, (bx, y, bw, bh), 2, border_radius=10)
            draw_text(surf, job["name"], FONT_SM, WHITE if sel else GRAY, bx+16, y+18, "topleft")
            if job["pay"] > 0:
                draw_text(surf, job["desc"], FONT_XS, GRAY, bx+16, y+40, "topleft")
                draw_text(surf, f"+${job['pay']} +{job['credit']}⭐", FONT_SM, YELLOW, bx+bw-16, y+24, "topright")

        if self.msg_timer > 0:
            draw_rect_alpha(surf, SURFACE, (W//2-200, 580, 400, 36), 200, 8)
            draw_text(surf, self.msg, FONT_SM, self.msg_col, W//2, 598, "center")

        draw_text(surf, "[↑↓] Navigate  [ENTER] Start Job  [ESC] Back", FONT_XS, GRAY, W//2, H-60, "center")


# ══════════════════════════════════════════════════════════════════════════════
# MINI-GAMES HUB
# ══════════════════════════════════════════════════════════════════════════════

class ReactionGame:
    """Click/press SPACE when the circle turns green."""
    def __init__(self):
        self.state = "wait"
        self.wait_time = random.randint(60, 200)
        self.timer = 0
        self.result = None
        self.rounds = 0
        self.wins = 0
        self.reaction_time = 0
        self.best = 9999

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.state == "green":
                    rt = self.timer
                    self.reaction_time = rt
                    self.best = min(self.best, rt)
                    self.wins += 1
                    self.result = f"⚡ {rt} ms! "
                    self.result += "Fast!" if rt < 30 else ("Good!" if rt < 60 else "Slow!")
                    self.state = "result"
                    gs["money"] += 5 if rt < 30 else 2
                    gs["social_credit"] = min(100, gs["social_credit"]+2)
                elif self.state == "wait":
                    self.result = "Too early! -$2"
                    gs["money"] = max(0, gs["money"]-2)
                    self.state = "result"
                elif self.state == "result":
                    self.rounds += 1
                    if self.rounds >= 5:
                        return "done"
                    self.state = "wait"
                    self.wait_time = random.randint(60, 200)
                    self.timer = 0
                    self.result = None
            if event.key == pygame.K_ESCAPE:
                return "exit"
        return None

    def update(self):
        self.timer += 1
        if self.state == "wait" and self.timer >= self.wait_time:
            self.state = "green"
            self.timer = 0

    def draw(self, surf):
        surf.fill(BGDARK)
        draw_text(surf, "⚡ REACTION GAME", FONT_BIG, CYAN, W//2, 80, "center")
        draw_text(surf, f"Round {self.rounds+1}/5  |  Wins: {self.wins}", FONT_SM, GRAY, W//2, 140, "center")

        col = GREEN if self.state == "green" else (RED if self.state == "result" else GRAY)
        size = pulse_size(80, tick) if self.state == "green" else 80
        pygame.draw.circle(surf, col, (W//2, H//2-30), size)
        pygame.draw.circle(surf, WHITE, (W//2, H//2-30), size, 3)

        if self.state == "wait":
            draw_text(surf, "Get ready...", FONT_MED, GRAY, W//2, H//2+80, "center")
            draw_text(surf, "Press SPACE when GREEN", FONT_SM, GRAY, W//2, H//2+120, "center")
        elif self.state == "green":
            draw_text(surf, "PRESS SPACE!", FONT_MED, glow_color(GREEN, tick), W//2, H//2+80, "center")
        elif self.state == "result":
            draw_text(surf, self.result, FONT_MED, YELLOW, W//2, H//2+80, "center")
            draw_text(surf, "Press SPACE for next round", FONT_SM, GRAY, W//2, H//2+120, "center")

        draw_text(surf, "[ESC] Back to mini-game menu", FONT_XS, GRAY, W//2, H-60, "center")


class RomanQuest:
    """Simple number quiz game."""
    ROMANS = {"I":1,"V":5,"X":10,"L":50,"C":100,"D":500,"M":1000}
    NUMS = [(1,"I"),(2,"II"),(3,"III"),(4,"IV"),(5,"V"),(6,"VI"),(9,"IX"),
            (10,"X"),(14,"XIV"),(19,"XIX"),(20,"XX"),(40,"XL"),(50,"L"),
            (90,"XC"),(100,"C"),(400,"CD"),(500,"D"),(900,"CM"),(1000,"M")]

    def __init__(self):
        self.score = 0
        self.round = 0
        self.total = 8
        self.answer = ""
        self.question = None
        self.feedback = ""
        self.fb_timer = 0
        self.fb_col = GREEN
        self._next()

    def _next(self):
        num, rom = random.choice(self.NUMS)
        if random.random() > 0.5:
            self.q_text = f"Roman → Number:  {rom}"
            self.correct = str(num)
            self.hint = "Type the number"
        else:
            self.q_text = f"Number → Roman:  {num}"
            self.correct = rom
            self.hint = "Type Roman numerals"
        self.answer = ""

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if self.fb_timer > 0:
                return None
            if event.key == pygame.K_BACKSPACE:
                self.answer = self.answer[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.answer.strip().upper() == self.correct.upper():
                    self.score += 10
                    gs["money"] += 5
                    gs["social_credit"] = min(100, gs["social_credit"]+2)
                    self.feedback = f"✓ Correct! +$5"; self.fb_col = GREEN
                else:
                    self.feedback = f"✗ Answer: {self.correct}"; self.fb_col = RED
                self.fb_timer = 90
                self.round += 1
                if self.round < self.total:
                    self._next()
            elif event.key == pygame.K_ESCAPE:
                return "exit"
            elif len(self.answer) < 10:
                c = event.unicode.upper()
                if c.isalnum():
                    self.answer += c
        return "done" if self.round >= self.total else None

    def update(self):
        if self.fb_timer > 0: self.fb_timer -= 1

    def draw(self, surf):
        surf.fill(BGDARK)
        draw_text(surf, "🏛 ROMAN QUEST", FONT_BIG, YELLOW, W//2, 80, "center")
        draw_text(surf, f"Round {self.round+1}/{self.total}  |  Score: {self.score}", FONT_SM, GRAY, W//2, 140, "center")
        draw_rect_alpha(surf, SURFACE2, (W//2-250, 220, 500, 80), 200, 10)
        draw_text(surf, self.q_text, FONT_MED, WHITE, W//2, 260, "center")
        draw_text(surf, self.hint, FONT_XS, GRAY, W//2, 310, "center")
        # Input box
        bx, by, bw, bh = W//2-150, 370, 300, 50
        pygame.draw.rect(surf, SURFACE2, (bx, by, bw, bh), border_radius=8)
        pygame.draw.rect(surf, CYAN, (bx, by, bw, bh), 2, border_radius=8)
        cursor = "_" if (tick//20)%2==0 else ""
        draw_text(surf, self.answer + cursor, FONT_MED, WHITE, W//2, by+bh//2, "center")
        if self.fb_timer > 0:
            draw_text(surf, self.feedback, FONT_MED, self.fb_col, W//2, 460, "center")
        draw_text(surf, "[Type answer]  [ENTER] Submit  [ESC] Back", FONT_XS, GRAY, W//2, H-60, "center")


MINI_GAMES = [
    {"name": "⚡ Reaction Game", "desc": "Test your reflexes!",    "cls": ReactionGame},
    {"name": "🏛 Roman Quest",   "desc": "Roman numeral quiz!",    "cls": RomanQuest},
    {"name": "🔙 Back",          "desc": "Return to hub",          "cls": None},
]

class MiniHub:
    def __init__(self):
        self.sel = 0
        self.active = None

    def handle(self, event):
        global MODE
        if self.active:
            result = self.active.handle(event)
            if result == "exit" or result == "done":
                save_state(gs)
                self.active = None
            return None
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel-1) % len(MINI_GAMES)
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel+1) % len(MINI_GAMES)
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                mg = MINI_GAMES[self.sel]
                if mg["cls"] is None:
                    return "HUB"
                self.active = mg["cls"]()
            if event.key == pygame.K_ESCAPE:
                return "HUB"
        return None

    def update(self):
        if self.active:
            self.active.update()

    def draw(self, surf):
        if self.active:
            self.active.draw(surf)
            draw_hud(surf)
            return
        surf.fill(BGDARK)
        draw_text(surf, "🎮  MINI-GAME HUB", FONT_BIG, PURPLE, W//2, 80, "center")
        for i, mg in enumerate(MINI_GAMES):
            sel = i == self.sel
            y = 220 + i*110
            bw, bh = 500, 80
            bx = W//2-bw//2
            draw_rect_alpha(surf, PURPLE if sel else SURFACE2, (bx, y, bw, bh), 180 if sel else 120, 12)
            if sel:
                pygame.draw.rect(surf, PURPLE, (bx, y, bw, bh), 2, border_radius=12)
            draw_text(surf, mg["name"], FONT_MED, WHITE if sel else GRAY, bx+20, y+22, "topleft")
            draw_text(surf, mg["desc"], FONT_XS, GRAY, bx+20, y+52, "topleft")
        draw_text(surf, "[↑↓] Navigate  [ENTER] Play  [ESC] Back", FONT_XS, GRAY, W//2, H-60, "center")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ══════════════════════════════════════════════════════════════════════════════

def main():
    global MODE, tick

    hub   = HubMenu()
    snake = SnakeGame()
    city  = CityMode()
    bank  = BankMode()
    shop  = ShopMode()
    job   = JobMode()
    mini  = MiniHub()

    objects = {
        "HUB":  hub,
        "SNAKE": snake,
        "CITY": city,
        "BANK": bank,
        "SHOP": shop,
        "JOB":  job,
        "MINI": mini,
    }

    while True:
        dt = clock.tick(FPS)
        tick += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_state(gs)
                pygame.quit()
                sys.exit()

            result = objects[MODE].handle(event)
            if result and result in objects:
                if result != MODE:
                    # Re-init fresh on enter
                    if result == "SNAKE": snake.reset()
                    if result == "BANK":  bank.__init__()
                    if result == "SHOP":  shop.__init__()
                    if result == "CITY":  city.__init__()
                MODE = result

        # Update
        if MODE == "SNAKE":
            snake.update(dt)
        elif MODE == "CITY":
            city.update()
        elif MODE == "BANK":
            bank.update()
        elif MODE == "SHOP":
            shop.update()
        elif MODE == "JOB":
            job.update()
        elif MODE == "MINI":
            mini.update()
        elif MODE == "HUB":
            hub.update()

        # Draw
        objects[MODE].draw(screen)

        # HUD on all modes except HUB
        if MODE != "HUB":
            draw_hud(screen)

        pygame.display.flip()


if __name__ == "__main__":
    main()