"""Pygame entry point for a minimal Tetris clone."""
from __future__ import annotations

import sys
from typing import Tuple

import pygame

from tetris.game import Game
from tetris.pieces import TETROMINOS

CELL_SIZE = 30
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BOARD_MARGIN = 20
SIDEBAR_WIDTH = 220
BOARD_PIXEL_WIDTH = BOARD_WIDTH * CELL_SIZE
BOARD_PIXEL_HEIGHT = BOARD_HEIGHT * CELL_SIZE
WINDOW_WIDTH = BOARD_MARGIN * 2 + BOARD_PIXEL_WIDTH + SIDEBAR_WIDTH
WINDOW_HEIGHT = BOARD_MARGIN * 2 + BOARD_PIXEL_HEIGHT
BOARD_ORIGIN = (BOARD_MARGIN, BOARD_MARGIN)
SIDEBAR_X = BOARD_MARGIN * 2 + BOARD_PIXEL_WIDTH
BG_COLOR = (16, 20, 28)
GRID_COLOR = (48, 56, 64)
TEXT_COLOR = (236, 240, 241)
GHOST_COLOR = (120, 140, 160)


def draw_block(surface: pygame.Surface, color: Tuple[int, int, int], x: int, y: int) -> None:
    px = BOARD_ORIGIN[0] + x * CELL_SIZE
    py = BOARD_ORIGIN[1] + y * CELL_SIZE
    rect = pygame.Rect(px, py, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, GRID_COLOR, rect, 1)


def draw_board_grid(surface: pygame.Surface) -> None:
    for x in range(BOARD_WIDTH + 1):
        px = BOARD_ORIGIN[0] + x * CELL_SIZE
        pygame.draw.line(
            surface, GRID_COLOR, (px, BOARD_ORIGIN[1]), (px, BOARD_ORIGIN[1] + BOARD_PIXEL_HEIGHT)
        )
    for y in range(BOARD_HEIGHT + 1):
        py = BOARD_ORIGIN[1] + y * CELL_SIZE
        pygame.draw.line(
            surface, GRID_COLOR, (BOARD_ORIGIN[0], py), (BOARD_ORIGIN[0] + BOARD_PIXEL_WIDTH, py)
        )


def draw_preview(surface: pygame.Surface, name: str, rect: pygame.Rect) -> None:
    tetromino = TETROMINOS[name]
    rotation = tetromino.get_rotation(0)
    min_x = min(x for x, _ in rotation)
    max_x = max(x for x, _ in rotation)
    min_y = min(y for _, y in rotation)
    max_y = max(y for _, y in rotation)
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    cell_size = rect.width // 4
    offset_x = rect.x + (rect.width - width * cell_size) // 2
    offset_y = rect.y + (rect.height - height * cell_size) // 2
    for dx, dy in rotation:
        px = offset_x + (dx - min_x) * cell_size
        py = offset_y + (dy - min_y) * cell_size
        block_rect = pygame.Rect(px, py, cell_size, cell_size)
        pygame.draw.rect(surface, tetromino.color, block_rect)
        pygame.draw.rect(surface, GRID_COLOR, block_rect, 1)


def render_sidebar(surface: pygame.Surface, game: Game, font: pygame.font.Font, small_font: pygame.font.Font) -> None:
    sidebar_rect = pygame.Rect(SIDEBAR_X, BOARD_MARGIN, SIDEBAR_WIDTH - BOARD_MARGIN, BOARD_PIXEL_HEIGHT)
    pygame.draw.rect(surface, (24, 30, 38), sidebar_rect)

    # Score and level
    score_text = font.render(f"Score: {game.score}", True, TEXT_COLOR)
    level_text = font.render(f"Level: {game.level}", True, TEXT_COLOR)
    lines_text = font.render(f"Lines: {game.lines_cleared}", True, TEXT_COLOR)
    surface.blit(score_text, (SIDEBAR_X + 12, BOARD_MARGIN + 12))
    surface.blit(level_text, (SIDEBAR_X + 12, BOARD_MARGIN + 40))
    surface.blit(lines_text, (SIDEBAR_X + 12, BOARD_MARGIN + 68))

    # Hold piece
    hold_title = font.render("Hold", True, TEXT_COLOR)
    surface.blit(hold_title, (SIDEBAR_X + 12, BOARD_MARGIN + 110))
    hold_rect = pygame.Rect(SIDEBAR_X + 12, BOARD_MARGIN + 140, 120, 120)
    pygame.draw.rect(surface, GRID_COLOR, hold_rect, 2)
    if game.hold:
        draw_preview(surface, game.hold, hold_rect)

    # Next queue
    next_title = font.render("Next", True, TEXT_COLOR)
    surface.blit(next_title, (SIDEBAR_X + 12, BOARD_MARGIN + 280))
    next_rect_y = BOARD_MARGIN + 310
    for idx, name in enumerate(game.next_queue()[:4]):
        rect = pygame.Rect(SIDEBAR_X + 12, next_rect_y + idx * 90, 120, 80)
        pygame.draw.rect(surface, GRID_COLOR, rect, 2)
        draw_preview(surface, name, rect)

    if game.game_over:
        over_text = font.render("Game Over", True, (240, 100, 100))
        surface.blit(over_text, (SIDEBAR_X + 12, BOARD_MARGIN + BOARD_PIXEL_HEIGHT - 40))
    else:
        controls = [
            "←/→: Move",
            "↓: Soft drop",
            "↑ or X: Rotate",
            "Z: Rotate CCW",
            "Space: Hard drop",
            "C: Hold",
            "Esc: Quit",
        ]
        for i, text in enumerate(controls):
            label = small_font.render(text, True, TEXT_COLOR)
            surface.blit(label, (SIDEBAR_X + 12, BOARD_MARGIN + BOARD_PIXEL_HEIGHT - 170 + i * 20))


def render(screen: pygame.Surface, game: Game, font: pygame.font.Font, small_font: pygame.font.Font) -> None:
    screen.fill(BG_COLOR)
    draw_board_grid(screen)

    # Settled blocks
    for y, row in enumerate(game.settled_cells()):
        for x, cell in enumerate(row):
            if cell is not None:
                draw_block(screen, cell, x, y)

    # Ghost piece
    ghost = game.ghost_position()
    if ghost:
        for x, y in ghost:
            if y < 0:
                continue
            px = BOARD_ORIGIN[0] + x * CELL_SIZE
            py = BOARD_ORIGIN[1] + y * CELL_SIZE
            rect = pygame.Rect(px, py, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GHOST_COLOR, rect, 1)

    # Active piece
    for x, y, color in game.active_cells():
        if y >= 0:
            draw_block(screen, color, x, y)

    render_sidebar(screen, game, font, small_font)
    pygame.display.flip()


def handle_input(game: Game, event: pygame.event.Event) -> None:
    if event.type != pygame.KEYDOWN:
        return
    if event.key == pygame.K_ESCAPE:
        pygame.event.post(pygame.event.Event(pygame.QUIT))
    elif event.key == pygame.K_LEFT:
        game.move(-1)
    elif event.key == pygame.K_RIGHT:
        game.move(1)
    elif event.key == pygame.K_DOWN:
        game.soft_drop()
    elif event.key in (pygame.K_UP, pygame.K_x):
        game.rotate(1)
    elif event.key == pygame.K_z:
        game.rotate(-1)
    elif event.key == pygame.K_SPACE:
        game.hard_drop()
    elif event.key == pygame.K_c:
        game.hold_piece()


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Tetris")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 22)
    small_font = pygame.font.SysFont("arial", 16)

    game = Game(width=BOARD_WIDTH, height=BOARD_HEIGHT)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                handle_input(game, event)

        if not game.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_DOWN]:
                game.soft_drop()
        game.update(dt)
        render(screen, game, font, small_font)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
