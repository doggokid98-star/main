"""
Typing Defender - Type falling words to destroy them. Great for typing practice.
"""
import pygame
import random

pygame.init()
W, H = 700, 550
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Typing Defender")
clock = pygame.time.Clock()
FPS = 60

WORDS = ["python", "game", "code", "key", "type", "quick", "fast", "word", "defend", "attack",
         "laser", "ship", "space", "score", "bonus", "extra", "level", "speed", "power", "magic"]
typed = ""
words_list = []
spawn_timer = 0
score = 0
lives = 3
font = pygame.font.SysFont("consolas", 28)
font_big = pygame.font.SysFont("segoeui", 36)


def main():
    global typed, words_list, spawn_timer, score, lives
    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over:
                    if event.key == pygame.K_SPACE:
                        game_over = False
                        lives = 3
                        score = 0
                        words_list.clear()
                        typed = ""
                    continue
                if event.key == pygame.K_BACKSPACE:
                    typed = typed[:-1]
                elif event.unicode.isalpha() or event.unicode == " ":
                    typed += event.unicode.lower()

        if not game_over:
            spawn_timer += 1
            if spawn_timer >= 60:
                spawn_timer = 0
                word = random.choice(WORDS)
                words_list.append({"text": word, "y": 0, "x": random.randint(50, W - 150), "speed": 0.8 + score / 500})
            for w in words_list[:]:
                w["y"] += w["speed"]
                if w["y"] > H - 50:
                    words_list.remove(w)
                    lives -= 1
                    if lives <= 0:
                        game_over = True
                if typed.strip() == w["text"]:
                    score += len(w["text"]) * 2
                    words_list.remove(w)
                    typed = ""

        screen.fill((18, 22, 35))
        pygame.draw.rect(screen, (50, 55, 80), (20, H - 55, W - 40, 45))
        screen.blit(font.render("Type: " + typed + "_", True, (200, 255, 200)), (30, H - 48))
        for w in words_list:
            screen.blit(font.render(w["text"], True, (255, 220, 100)), (w["x"], int(w["y"])))
        screen.blit(font_big.render(f"Score: {score}  Lives: {lives}", True, (255, 255, 255)), (20, 15))
        if game_over:
            over = font_big.render("Game Over - SPACE to restart", True, (255, 100, 100))
            screen.blit(over, (W // 2 - over.get_width() // 2, H // 2 - 30))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()
