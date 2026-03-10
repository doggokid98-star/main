"""
Memory Match - Flip cards to find pairs. Clean and satisfying.
"""
import pygame
import random

pygame.init()
W, H = 640, 520
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Memory Match")
clock = pygame.time.Clock()
FPS = 60

CARD_W, CARD_H = 80, 100
MARGIN = 12
COLORS = [(200, 80, 80), (80, 180, 100), (80, 120, 220), (220, 180, 50),
          (180, 80, 200), (80, 200, 200), (220, 120, 80), (120, 120, 180)]


def main():
    font = pygame.font.SysFont("segoeui", 28)
    n_pairs = 8
    cards = []
    for i in range(n_pairs):
        c = COLORS[i % len(COLORS)]
        cards.append({"id": i, "rect": None, "flipped": False, "matched": False, "color": c})
        cards.append({"id": i, "rect": None, "flipped": False, "matched": False, "color": c})
    random.shuffle(cards)
    cols = 4
    rows = (len(cards) + cols - 1) // cols
    start_x = (W - (cols * (CARD_W + MARGIN) - MARGIN)) // 2
    start_y = 80
    for i, card in enumerate(cards):
        c, r = i % cols, i // cols
        card["rect"] = pygame.Rect(start_x + c * (CARD_W + MARGIN), start_y + r * (CARD_H + MARGIN), CARD_W, CARD_H)
    flipped_ids = []
    moves = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                for card in cards:
                    if card["matched"] or card["flipped"]:
                        continue
                    if card["rect"].collidepoint(pos):
                        if len(flipped_ids) < 2:
                            card["flipped"] = True
                            flipped_ids.append(card)
                            if len(flipped_ids) == 2:
                                moves += 1
                                if flipped_ids[0]["id"] == flipped_ids[1]["id"]:
                                    flipped_ids[0]["matched"] = True
                                    flipped_ids[1]["matched"] = True
                                    flipped_ids.clear()
                                else:
                                    pass  # will unflip after delay
                        break

        if len(flipped_ids) == 2:
            pygame.time.delay(600)
            flipped_ids[0]["flipped"] = False
            flipped_ids[1]["flipped"] = False
            flipped_ids.clear()

        screen.fill((30, 35, 55))
        for card in cards:
            r = card["rect"]
            if card["matched"]:
                pygame.draw.rect(screen, (80, 80, 100), r)
                pygame.draw.rect(screen, card["color"], r.inflate(-8, -8))
            elif card["flipped"]:
                pygame.draw.rect(screen, card["color"], r)
                pygame.draw.rect(screen, (255, 255, 255), r, 3)
            else:
                pygame.draw.rect(screen, (70, 75, 110), r)
                pygame.draw.rect(screen, (100, 110, 160), r, 2)
        matched_count = sum(1 for c in cards if c["matched"])
        screen.blit(font.render(f"Moves: {moves}  Pairs: {matched_count // 2}/{n_pairs}", True, (255, 255, 255)), (20, 20))
        if matched_count == len(cards):
            screen.blit(font.render("You win! ESC to quit.", True, (100, 255, 150)), (W // 2 - 120, H - 50))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()
