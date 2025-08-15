import curses
import random
import time
import argparse

# Configuration
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
TICK_RATE = 0.5  # seconds between automatic drops

SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
]

COLORS = [
    curses.COLOR_CYAN,
    curses.COLOR_YELLOW,
    curses.COLOR_MAGENTA,
    curses.COLOR_GREEN,
    curses.COLOR_RED,
    curses.COLOR_BLUE,
    curses.COLOR_WHITE,
]


def rotate(shape):
    """Rotate shape clockwise."""
    return [list(row) for row in zip(*shape[::-1])]


def create_board():
    return [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]


def check_collision(board, shape, offset):
    off_y, off_x = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                new_y = y + off_y
                new_x = x + off_x
                if new_x < 0 or new_x >= BOARD_WIDTH or new_y >= BOARD_HEIGHT:
                    return True
                if new_y >= 0 and board[new_y][new_x]:
                    return True
    return False


def merge(board, shape, offset, color):
    off_y, off_x = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                board[y + off_y][x + off_x] = color


def remove_complete_lines(board):
    new_board = [row for row in board if any(cell == 0 for cell in row)]
    cleared = BOARD_HEIGHT - len(new_board)
    while len(new_board) < BOARD_HEIGHT:
        new_board.insert(0, [0 for _ in range(BOARD_WIDTH)])
    return new_board, cleared


def draw_board(stdscr, board, current, offset):
    stdscr.clear()
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if cell:
                stdscr.addstr(y, x * 2, "[]", curses.color_pair(cell))
    shape, color = current
    off_y, off_x = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell and y + off_y >= 0:
                stdscr.addstr(y + off_y, (x + off_x) * 2, "[]", curses.color_pair(color))
    stdscr.refresh()


def game_loop(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    for i, color in enumerate(COLORS, start=1):
        curses.init_pair(i, color, curses.COLOR_BLACK)

    board = create_board()
    current_shape = random.choice(SHAPES)
    current_color = random.randint(1, len(COLORS))
    offset = [0, BOARD_WIDTH // 2 - len(current_shape[0]) // 2]
    last_tick = time.time()
    score = 0

    while True:
        draw_board(stdscr, board, (current_shape, current_color), offset)
        stdscr.addstr(0, BOARD_WIDTH * 2 + 2, f"Score: {score}")
        try:
            key = stdscr.getch()
        except Exception:
            key = -1
        if key == curses.KEY_LEFT and not check_collision(board, current_shape, (offset[0], offset[1] - 1)):
            offset[1] -= 1
        elif key == curses.KEY_RIGHT and not check_collision(board, current_shape, (offset[0], offset[1] + 1)):
            offset[1] += 1
        elif key == curses.KEY_DOWN and not check_collision(board, current_shape, (offset[0] + 1, offset[1])):
            offset[0] += 1
        elif key == curses.KEY_UP:
            rotated = rotate(current_shape)
            if not check_collision(board, rotated, offset):
                current_shape = rotated
        elif key == ord('q'):
            break

        if time.time() - last_tick > TICK_RATE:
            if not check_collision(board, current_shape, (offset[0] + 1, offset[1])):
                offset[0] += 1
            else:
                merge(board, current_shape, offset, current_color)
                board, cleared = remove_complete_lines(board)
                score += cleared
                current_shape = random.choice(SHAPES)
                current_color = random.randint(1, len(COLORS))
                offset = [0, BOARD_WIDTH // 2 - len(current_shape[0]) // 2]
                if check_collision(board, current_shape, offset):
                    stdscr.addstr(BOARD_HEIGHT // 2, BOARD_WIDTH, "GAME OVER")
                    stdscr.nodelay(False)
                    stdscr.getch()
                    break
            last_tick = time.time()
        time.sleep(0.05)


def self_test():
    board = create_board()
    shape = [[1, 1, 1, 1]]
    offset = (0, 0)
    assert not check_collision(board, shape, offset)
    merge(board, shape, offset, 1)
    board, cleared = remove_complete_lines(board)
    assert cleared == 0
    # fill a row
    board[-1] = [1] * BOARD_WIDTH
    board, cleared = remove_complete_lines(board)
    assert cleared == 1
    print("self-test passed")


def main():
    parser = argparse.ArgumentParser(description="Simple Tetris game")
    parser.add_argument('--test', action='store_true', help='run self-tests and exit')
    args = parser.parse_args()
    if args.test:
        self_test()
    else:
        curses.wrapper(game_loop)


if __name__ == '__main__':
    main()
