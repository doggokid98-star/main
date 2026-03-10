"""
Puzzle Slide - Slide the tiles to order 1-15. One empty space.
"""
import pygame
import random

pygame.init()
W, H = 420, 500
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Puzzle Slide")
clock = pygame.time.Clock()
FPS = 60

TILE = 95
GAP = 5
grid = list(range(1, 16)) + [0]
empty = 15
moves = 0
font = pygame.font.SysFont("segoeui", 36, bold=True)
font_small = pygame.font.SysFont("segoeui", 22)
solved = False


def main():
    global grid, empty, moves, solved
    # Shuffle (only solvable permutations)
    for _ in range(200):
        r = random.randint(0, 3)
        if r == 0 and empty % 4 != 0:
            grid[empty], grid[empty - 1] = grid[empty - 1], grid[empty]
            empty -= 1
        elif r == 1 and empty % 4 != 3:
            grid[empty], grid[empty + 1] = grid[empty + 1], grid[empty]
            empty += 1
        elif r == 2 and empty >= 4:
            grid[empty], grid[empty - 4] = grid[empty - 4], grid[empty]
            empty -= 4
        elif r == 3 and empty < 12:
            grid[empty], grid[empty + 4] = grid[empty + 4], grid[empty]
            empty += 4
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    grid = list(range(1, 16)) + [0]
                    empty = 15
                    moves = 0
                    solved = False
                    for _ in range(200):
                        r = random.randint(0, 3)
                        if r == 0 and empty % 4 != 0:
                            grid[empty], grid[empty - 1] = grid[empty - 1], grid[empty]
                            empty -= 1
                        elif r == 1 and empty % 4 != 3:
                            grid[empty], grid[empty + 1] = grid[empty + 1], grid[empty]
                            empty += 1
                        elif r == 2 and empty >= 4:
                            grid[empty], grid[empty - 4] = grid[empty - 4], grid[empty]
                            empty -= 4
                        elif r == 3 and empty < 12:
                            grid[empty], grid[empty + 4] = grid[empty + 4], grid[empty]
                            empty += 4
                    continue
                if solved:
                    continue
                if event.key == pygame.K_LEFT and empty % 4 != 3:
                    grid[empty], grid[empty + 1] = grid[empty + 1], grid[empty]
                    empty += 1
                    moves += 1
                if event.key == pygame.K_RIGHT and empty % 4 != 0:
                    grid[empty], grid[empty - 1] = grid[empty - 1], grid[empty]
                    empty -= 1
                    moves += 1
                if event.key == pygame.K_UP and empty < 12:
                    grid[empty], grid[empty + 4] = grid[empty + 4], grid[empty]
                    empty += 4
                    moves += 1
                if event.key == pygame.K_DOWN and empty >= 4:
                    grid[empty], grid[empty - 4] = grid[empty - 4], grid[empty]
                    empty -= 4
                    moves += 1
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not solved:
                mx, my = event.pos
                start_x = (W - 4 * TILE - 3 * GAP) // 2
                start_y = 100
                for i in range(16):
                    c, r = i % 4, i // 4
                    tx = start_x + c * (TILE + GAP)
                    ty = start_y + r * (TILE + GAP)
                    if tx <= mx <= tx + TILE and ty <= my <= ty + TILE and grid[i] != 0:
                        if i == empty - 1 and empty % 4 != 0:
                            grid[empty], grid[empty - 1] = grid[empty - 1], grid[empty]
                            empty -= 1
                            moves += 1
                        elif i == empty + 1 and empty % 4 != 3:
                            grid[empty], grid[empty + 1] = grid[empty + 1], grid[empty]
                            empty += 1
                            moves += 1
                        elif i == empty - 4 and empty >= 4:
                            grid[empty], grid[empty - 4] = grid[empty - 4], grid[empty]
                            empty -= 4
                            moves += 1
                        elif i == empty + 4 and empty < 12:
                            grid[empty], grid[empty + 4] = grid[empty + 4], grid[empty]
                            empty += 4
                            moves += 1
                        break

        solved = grid[:15] == list(range(1, 16))
        screen.fill((25, 28, 45))
        start_x = (W - 4 * TILE - 3 * GAP) // 2
        start_y = 100
        for i in range(16):
            c, r = i % 4, i // 4
            x = start_x + c * (TILE + GAP)
            y = start_y + r * (TILE + GAP)
            if grid[i] == 0:
                pygame.draw.rect(screen, (45, 50, 70), (x, y, TILE, TILE))
            else:
                pygame.draw.rect(screen, (70, 120, 200), (x, y, TILE, TILE))
                pygame.draw.rect(screen, (100, 150, 255), (x, y, TILE, TILE), 2)
                screen.blit(font.render(str(grid[i]), True, (255, 255, 255)), (x + TILE // 2 - 12, y + TILE // 2 - 18))
        screen.blit(font_small.render(f"Moves: {moves}  Arrow keys or click  R=shuffle", True, (200, 200, 220)), (20, 30))
        if solved:
            screen.blit(font.render("Solved!", True, (100, 255, 150)), (W // 2 - 55, H - 60))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()
