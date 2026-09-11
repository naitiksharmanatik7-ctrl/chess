"""
Pygame rendering + input handling.

All chess move logic lives in board_logic.py (no pygame import there).
This file only knows how to draw the board/pieces and how to turn mouse
clicks into calls into board_logic — it doesn't know anything about
whether a move is "legal" beyond basic piece movement.

"""
import pygame as pg
from PIL import Image

import board_logic as bl

print('\n\n\n\n\n\n+1 sign = black peices and -1 sign = white peices \n')

board_imgpath = r'assets\chessboard1.png'
peices_imgpath = r'assets\chess_pieces.png'

# To print debug info to console of any function
debug = ['click']

# ---- pygame / asset setup ----
pg.init()
with Image.open(board_imgpath) as img:
    width, height = img.size
    if width == height:
        board_side = width
    else:
        print('board image is not square')
        quit()

with Image.open(peices_imgpath) as img:
    width, height = img.size
    peices_side = int(width / 6)  # sprite sheet is 6 pieces wide

cell = board_side / 8
offset = int(cell / 3)

screen = pg.display.set_mode((board_side + 2 * offset, board_side + 2 * offset))
screen.fill('gray')
clock = pg.time.Clock()
running = True
boardimg = pg.image.load(board_imgpath)
peices = pg.image.load(peices_imgpath)
text_font = pg.font.Font(None, int(cell / 2.4))

pg.display.set_caption("CHESS")
icon = pg.image.load(r'assets\logo.jpg')
pg.display.set_icon(pg.transform.smoothscale(icon, (32, 32)))

# ---- game state ----
board = bl.new_board()
turn = -1          # white moves first (white pieces are negative)
moves = []          # undo history, shared with board_logic.backtrack()
next_moves = []     # legal destinations for the currently selected piece
change_peice = []   # [piece value, [x, y]] of the currently selected piece, or []


def peicelocsprite(val):
    """Sprite-sheet (x, y) offset for a piece value, or None for empty."""
    if val == 0:
        return None
    # (sheet_col, sheet_row) — row 0 = white, row 1 = black
    lookup = {
        1: (1, 1), 2: (0, 1), 3: (4, 1), 4: (3, 1), 5: (2, 1), 6: (5, 1),
        -1: (1, 0), -2: (0, 0), -3: (4, 0), -4: (3, 0), -5: (2, 0), -6: (5, 0),
    }
    col, row = lookup[val]
    return (col * peices_side, row * peices_side)


def numbers():
    for i in range(8):
        tsur1 = text_font.render(str(i), True, 'black')
        tsur2 = text_font.render(str(i), True, 'black')
        screen.blit(tsur1, (offset / 4, i * cell + offset + int(cell / 2.5)))
        screen.blit(tsur2, (i * cell + offset + int(cell / 2.5), offset / 4))


def load_board():
    screen.blit(boardimg, (offset, offset))
    for i in range(len(board)):
        for j in range(len(board[i])):
            val = board[i][j]
            if val == 0:
                continue
            p = peicelocsprite(val)
            croppedsec = peices.subsurface(pg.Rect(p[0], p[1], peices_side, peices_side))
            peiceimg = pg.transform.smoothscale(croppedsec, (cell, cell))
            screen.blit(peiceimg, (j * cell + offset, i * cell + offset))


def highlight(x, y, color=(235, 215, 0)):
    if 0 <= x < 8 and 0 <= y < 8:
        pg.draw.rect(screen, color, (y * cell + offset, x * cell + offset, cell, cell), 4)


def rectangle(x, y):
    """Marker for a capture-move destination."""
    pg.draw.rect(screen, (173, 43, 31), (y * cell + offset, x * cell + offset, cell, cell), 3)


def draw_circle(x, y):
    """Marker for a quiet-move destination."""
    if board[x][y] == 0:
        pg.draw.circle(
            screen, (160, 250, 206),
            (y * cell + offset + cell / 2, x * cell + offset + cell / 2), 10,
        )
    else:
        print(f'{x},{y} cant draw circle there as a peice exist there')


def draw_moves(quiet_moves, capture_moves):
    """Draw the move markers for a selected piece. Rendering only — no logic."""
    for x, y in quiet_moves:
        draw_circle(x, y)
    for x, y in capture_moves:
        rectangle(x, y)


def click(x, y):
    """Board-click state machine: first click selects a piece, second click moves it."""
    global next_moves, change_peice, turn

    if 'click' in debug: print(f'click (x, y) -> {x} , {y}')

    load_board()
    highlight(x, y)

    # second click: attempt to move the selected piece to (x, y)
    if (x, y) in next_moves and change_peice:
        old_sign = bl.tellsign(change_peice[0])
        new_sign = bl.tellsign(board[x][y])

        if new_sign != old_sign and board[x][y] not in (-2, 2):  # can't capture own piece or a king
            bl.apply_move(board, moves, change_peice[1], [x, y])
            load_board()

            turn *= -1
            next_moves = []
            change_peice = []
            return

    # otherwise: clear selection, and select a new piece if this click landed on one
    next_moves = []
    change_peice = []

    #if it is a piece of the current turn, select it and show its moves
    if board[x][y] != 0 and bl.tellsign(board[x][y]) == turn:
        change_peice = [board[x][y], [x, y]]
        quiet , capture = bl.calnextmoves(board, x, y)
        next_moves = quiet + capture
        draw_moves(quiet, capture)


def backtrack_ui():
    """Undo the last move and redraw, or report there's nothing to undo."""
    if bl.backtrack(board, moves):
        load_board()
    else:
        print('No previous moves left')


numbers()
load_board()


def gameloop():
    global running
    while running:
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                x, y = event.pos
                if offset < x < offset + cell * 8 and offset < y < offset + cell * 8:
                    click(int((y - offset) / cell), int((x - offset) / cell))

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_z and (event.mod & pg.KMOD_CTRL):
                    backtrack_ui()

            if event.type == pg.QUIT:
                running = False
                pg.quit()
                return

        pg.display.update()
        clock.tick(60)


if __name__ == "__main__":
    gameloop()
