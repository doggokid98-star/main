"""
Pong - Classic with leaderboard, pause, difficulty levels, power-ups.
Score resets when you die (lose a life).
Run: python run.py (or from launcher)
"""
import json
import os
import pygame
import random

pygame.init()
pygame.mixer.init()

VIRTUAL_W, VIRTUAL_H = 900, 600
W, H = VIRTUAL_W, VIRTUAL_H
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()
FPS = 60

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LEADERBOARD_PATH = os.path.join(SCRIPT_DIR, "leaderboard.json")

# Colors
BG = (12, 14, 22)
PADDLE = (60, 180, 255)
BALL = (255, 220, 100)
TEXT = (240, 240, 250)
MUTED = (120, 130, 150)
POWER_GREEN = (50, 220, 120)
POWER_RED = (220, 80, 80)
POWER_PURPLE = (180, 100, 255)
POWER_ORANGE = (255, 160, 50)

# Difficulty: ball_speed_mult, paddle_speed, ai_reaction
DIFFICULTIES = {
    "easy": (0.85, 8, 0.4),
    "normal": (1.0, 10, 0.6),
    "hard": (1.25, 12, 0.85),
}

# Power-up types
POWER_TWO_BALLS = "two_balls"
POWER_SPEED_UP = "speed_up"
POWER_SLOW = "slow"
POWER_SHRINK = "shrink"
POWERUPS = [POWER_TWO_BALLS, POWER_SPEED_UP, POWER_SLOW, POWER_SHRINK]
POWER_COLORS = {
    POWER_TWO_BALLS: POWER_GREEN,
    POWER_SPEED_UP: POWER_RED,
    POWER_SLOW: POWER_PURPLE,
    POWER_SHRINK: POWER_ORANGE,
}


def load_leaderboard():
    if os.path.isfile(LEADERBOARD_PATH):
        try:
            with open(LEADERBOARD_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_leaderboard(scores):
    with open(LEADERBOARD_PATH, "w") as f:
        json.dump(scores[:20], f, indent=2)


def main():
    font_big = pygame.font.SysFont("segoeui", 48, bold=True)
    font_mid = pygame.font.SysFont("segoeui", 28)
    font_small = pygame.font.SysFont("segoeui", 22)

    # Game state
    difficulty = "normal"
    lives = 3
    score = 0
    ball_speed_mult = DIFFICULTIES[difficulty][0]
    paddle_speed = DIFFICULTIES[difficulty][1]
    ai_reaction = DIFFICULTIES[difficulty][2]

    paddle_w, paddle_h = 14, 90
    ball_radius = 10
    base_ball_speed = 7 * ball_speed_mult

    player_y = VIRTUAL_H // 2 - paddle_h // 2
    enemy_y = VIRTUAL_H // 2 - paddle_h // 2
    player_x = 30
    enemy_x = VIRTUAL_W - 30 - paddle_w

    balls = []  # list of (x, y, vx, vy) in virtual coords
    balls.append([VIRTUAL_W // 2, VIRTUAL_H // 2, base_ball_speed * (1 if random.random() > 0.5 else -1), random.uniform(-1.5, 1.5)])

    powerups = []  # (x, y, type, timer_until_spawn)
    active_powerups = {}  # name -> frames_left
    powerup_spawn_cooldown = 0
    paused = False
    show_leaderboard = False
    game_over = False
    leaderboard = load_leaderboard()

    def spawn_powerup():
        nonlocal powerup_spawn_cooldown
        if powerup_spawn_cooldown > 0:
            powerup_spawn_cooldown -= 1
            return
        if len(powerups) >= 3 or random.random() > 0.993:
            return
        t = random.choice(POWERUPS)
        powerups.append([random.randint(VIRTUAL_W // 4, 3 * VIRTUAL_W // 4), random.randint(80, VIRTUAL_H - 80), t, 0])
        powerup_spawn_cooldown = 180

    def apply_power(name, frames=600):
        active_powerups[name] = frames

    def reset_ball(which=-1):
        nonlocal lives, game_over
        if which == -1:
            balls.clear()
        else:
            balls.pop(which)
        if not balls:
            lives -= 1
            active_powerups.clear()
            if lives <= 0:
                game_over = True
                leaderboard.append(score)
                leaderboard.sort(reverse=True)
                save_leaderboard(leaderboard)
            else:
                balls.append([VIRTUAL_W // 2, VIRTUAL_H // 2, base_ball_speed * (1 if random.random() > 0.5 else -1), random.uniform(-1.5, 1.5)])

    running = True
    while running:
        dt = 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                W, H = max(320, event.w), max(240, event.h)
                screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_over or show_leaderboard:
                        running = False
                    else:
                        paused = not paused
                if event.key == pygame.K_l and not game_over:
                    show_leaderboard = not show_leaderboard
                if not game_over and not paused and event.key == pygame.K_d:
                    diffs = list(DIFFICULTIES.keys())
                    idx = diffs.index(difficulty)
                    difficulty = diffs[(idx + 1) % len(diffs)]
                    ball_speed_mult, paddle_speed, ai_reaction = DIFFICULTIES[difficulty]
                    base_ball_speed = 7 * ball_speed_mult
                if game_over and event.key == pygame.K_SPACE:
                    running = False
        if not running:
            break

        W, H = screen.get_size()

        if show_leaderboard:
            vs = pygame.Surface((VIRTUAL_W, VIRTUAL_H))
            vs.fill(BG)
            title = font_big.render("High Scores", True, TEXT)
            vs.blit(title, (VIRTUAL_W // 2 - title.get_width() // 2, 40))
            for i, s in enumerate(leaderboard[:10]):
                t = font_mid.render(f"{i + 1}. {s}", True, TEXT)
                vs.blit(t, (VIRTUAL_W // 2 - t.get_width() // 2, 120 + i * 42))
            hint = font_small.render("Press L to close, ESC to quit", True, MUTED)
            vs.blit(hint, (VIRTUAL_W // 2 - hint.get_width() // 2, VIRTUAL_H - 50))
            W, H = screen.get_size()
            if W != VIRTUAL_W or H != VIRTUAL_H:
                screen.blit(pygame.transform.smoothscale(vs, (W, H)), (0, 0))
            else:
                screen.blit(vs, (0, 0))
            pygame.display.flip()
            clock.tick(FPS)
            continue

        if game_over:
            vs = pygame.Surface((VIRTUAL_W, VIRTUAL_H))
            vs.fill(BG)
            over = font_big.render("Game Over", True, (255, 100, 100))
            vs.blit(over, (VIRTUAL_W // 2 - over.get_width() // 2, VIRTUAL_H // 2 - 80))
            sc = font_mid.render(f"Score: {score}", True, TEXT)
            vs.blit(sc, (VIRTUAL_W // 2 - sc.get_width() // 2, VIRTUAL_H // 2 - 20))
            h = font_small.render("Score reset when you die. Press SPACE to exit.", True, MUTED)
            vs.blit(h, (VIRTUAL_W // 2 - h.get_width() // 2, VIRTUAL_H // 2 + 30))
            W, H = screen.get_size()
            if W != VIRTUAL_W or H != VIRTUAL_H:
                screen.blit(pygame.transform.smoothscale(vs, (W, H)), (0, 0))
            else:
                screen.blit(vs, (0, 0))
            pygame.display.flip()
            clock.tick(FPS)
            continue

        if paused:
            vs = pygame.Surface((VIRTUAL_W, VIRTUAL_H))
            vs.fill(BG)
            ptext = font_big.render("Paused", True, TEXT)
            vs.blit(ptext, (VIRTUAL_W // 2 - ptext.get_width() // 2, VIRTUAL_H // 2 - 40))
            W, H = screen.get_size()
            if W != VIRTUAL_W or H != VIRTUAL_H:
                screen.blit(pygame.transform.smoothscale(vs, (W, H)), (0, 0))
            else:
                screen.blit(vs, (0, 0))
            pygame.display.flip()
            clock.tick(FPS)
            continue

        # Update power-up timers
        for k in list(active_powerups):
            active_powerups[k] -= 1
            if active_powerups[k] <= 0:
                del active_powerups[k]
        paddle_h_use = paddle_h
        if POWER_SHRINK in active_powerups:
            paddle_h_use = max(40, paddle_h // 2)
        speed_mult = 1.0
        if POWER_SPEED_UP in active_powerups:
            speed_mult = 1.4
        if POWER_SLOW in active_powerups:
            speed_mult = 0.6

        # Input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            player_y -= paddle_speed
        if keys[pygame.K_DOWN]:
            player_y += paddle_speed
        player_y = max(0, min(VIRTUAL_H - paddle_h_use, player_y))

        # AI
        if balls:
            by = balls[0][1]
            target = by - paddle_h_use // 2
            if enemy_y < target:
                enemy_y = min(enemy_y + paddle_speed * ai_reaction, VIRTUAL_H - paddle_h_use)
            else:
                enemy_y = max(enemy_y - paddle_speed * ai_reaction, 0)
        enemy_y = max(0, min(VIRTUAL_H - paddle_h_use, enemy_y))

        # Power-up spawn
        spawn_powerup()

        # Update power-up pickups (circle vs paddle rect)
        def circle_hits_rect(cx, cy, cr, rx, ry, rw, rh):
            closest_x = max(rx, min(cx, rx + rw))
            closest_y = max(ry, min(cy, ry + rh))
            return (cx - closest_x) ** 2 + (cy - closest_y) ** 2 <= cr ** 2
        for p in powerups[:]:
            p[3] += 1
            if p[3] < 30:
                continue
            px, py, ptype = p[0], p[1], p[2]
            if circle_hits_rect(px, py, 18, player_x, player_y, paddle_w, paddle_h_use):
                apply_power(ptype)
                if ptype == POWER_TWO_BALLS and len(balls) == 1:
                    b = balls[0][:]
                    b[2] = -b[2]
                    balls.append(b)
                powerups.remove(p)
                continue
            if p[3] > 600:
                powerups.remove(p)

        # Update balls
        for b in balls[:]:
            b[0] += b[2] * speed_mult
            b[1] += b[3] * speed_mult
            if b[1] <= ball_radius or b[1] >= VIRTUAL_H - ball_radius:
                b[3] *= -1
            # Player paddle
            if b[0] - ball_radius <= player_x + paddle_w and b[2] < 0:
                if player_y <= b[1] <= player_y + paddle_h_use:
                    b[2] = abs(b[2]) * 1.02
                    b[0] = player_x + paddle_w + ball_radius
                    score += 1
            # Enemy paddle
            if b[0] + ball_radius >= enemy_x and b[2] > 0:
                if enemy_y <= b[1] <= enemy_y + paddle_h_use:
                    b[2] = -abs(b[2]) * 1.02
                    b[0] = enemy_x - ball_radius
            if b[0] < -20:
                reset_ball(balls.index(b))
                break
            if b[0] > VIRTUAL_W + 20:
                reset_ball(balls.index(b))
                break

        # Draw to virtual surface (fixed resolution), then scale to window
        virtual_surf = pygame.Surface((VIRTUAL_W, VIRTUAL_H))
        virtual_surf.fill(BG)
        for y in range(0, VIRTUAL_H, 24):
            pygame.draw.rect(virtual_surf, MUTED, (VIRTUAL_W // 2 - 2, y, 4, 12))
        pygame.draw.rect(virtual_surf, PADDLE, (player_x, player_y, paddle_w, paddle_h_use))
        pygame.draw.rect(virtual_surf, PADDLE, (enemy_x, enemy_y, paddle_w, paddle_h_use))
        for b in balls:
            pygame.draw.circle(virtual_surf, BALL, (int(b[0]), int(b[1])), ball_radius)
        for p in powerups:
            if p[3] >= 30:
                pygame.draw.circle(virtual_surf, POWER_COLORS.get(p[2], TEXT), (int(p[0]), int(p[1])), 14)
        score_t = font_mid.render(f"Score: {score}", True, TEXT)
        virtual_surf.blit(score_t, (20, 20))
        lives_t = font_mid.render(f"Lives: {lives}", True, TEXT)
        virtual_surf.blit(lives_t, (VIRTUAL_W - 120, 20))
        diff_t = font_small.render(f"Difficulty: {difficulty} (D to change)", True, MUTED)
        virtual_surf.blit(diff_t, (VIRTUAL_W // 2 - diff_t.get_width() // 2, 20))
        if active_powerups:
            pw = font_small.render(" | ".join(active_powerups), True, POWER_GREEN)
            virtual_surf.blit(pw, (20, VIRTUAL_H - 36))
        if W != VIRTUAL_W or H != VIRTUAL_H:
            scaled = pygame.transform.smoothscale(virtual_surf, (W, H))
            screen.blit(scaled, (0, 0))
        else:
            screen.blit(virtual_surf, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
