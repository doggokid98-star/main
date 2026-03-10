"""
Fruit Catch - Move the basket to catch falling fruit. Don't miss too many!
"""
import pygame
import random

pygame.init()
W, H = 480, 560
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Fruit Catch")
clock = pygame.time.Clock()
FPS = 60

basket_x = W // 2 - 40
fruits = []
score = 0
lives = 5
spawn_timer = 0
COLORS = [(255, 100, 100), (100, 200, 100), (255, 200, 50), (200, 100, 255), (100, 200, 255)]
font = pygame.font.SysFont("segoeui", 28)
game_over = False


def main():
    global basket_x, fruits, score, lives, spawn_timer, game_over
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over and event.key == pygame.K_SPACE:
                    game_over = False
                    fruits.clear()
                    score = 0
                    lives = 5

        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                basket_x -= 9
            if keys[pygame.K_RIGHT]:
                basket_x += 9
            basket_x = max(0, min(W - 80, basket_x))
            spawn_timer += 1
            if spawn_timer >= 25:
                spawn_timer = 0
                fruits.append({
                    "x": random.randint(20, W - 40), "y": -30,
                    "vy": 4 + score // 50, "color": random.choice(COLORS), "r": 18
                })
            for f in fruits[:]:
                f["y"] += f["vy"]
                if f["y"] > H:
                    fruits.remove(f)
                    lives -= 1
                    if lives <= 0:
                        game_over = True
                elif (f["y"] + f["r"] >= H - 55 and
                      basket_x <= f["x"] <= basket_x + 80 and
                      f["y"] - f["r"] <= H - 30):
                    score += 10
                    fruits.remove(f)

        screen.fill((240, 248, 255))
        pygame.draw.rect(screen, (139, 90, 43), (0, H - 50, W, 50))
        pygame.draw.arc(screen, (80, 50, 30), (basket_x, H - 55, 80, 40), 3.14, 0, 5)
        pygame.draw.rect(screen, (80, 50, 30), (basket_x, H - 45, 80, 15))
        for f in fruits:
            pygame.draw.circle(screen, f["color"], (int(f["x"]), int(f["y"])), f["r"])
        screen.blit(font.render(f"Score: {score}  Lives: {lives}", True, (40, 40, 60)), (10, 10))
        if game_over:
            screen.blit(font.render("Game Over - SPACE to restart", True, (220, 80, 80)), (W // 2 - 160, H // 2 - 20))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()
