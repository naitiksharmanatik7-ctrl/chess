"""
Pure chess board logic — no pygame, no rendering.

Board is an 8x8 list of lists. Sign = color (positive = black, negative =
white). Values: 1 queen, 2 king, 3 rook, 4 knight, 5 bishop, 6 pawn
(negate every value for the white equivalent).

Deliberately NOT included here (removed so it can be rewritten from
scratch): check detection, pin detection, castling. calnextmoves() below
only knows "how does this piece type move on an otherwise-empty board" —
it does not know whether a move would leave your own king in check, and
the king's moves are just its 8 adjacent squares with no restriction.
"""
from chess import debug

def new_board():
    return [
        [3, 4, 5, 1, 2, 5, 4, 3],
        [6, 6, 6, 6, 6, 6, 6, 6],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [-6, -6, -6, -6, -6, -6, -6, -6],
        [-3, -4, -5, -1, -2, -5, -4, -3],
    ]


def tellsign(x):
    """-1, 0, or +1 — the 'color' of a board value."""
    return (x > 0) - (x < 0)


def line(board, point, direc, ignore_peices=(0,)):
    """
    Walk one square at a time from `point` in direction `direc` (any
    combination of 'n', 's', 'e', 'w' — e.g. 'ne') until the edge of the
    board or a non-ignored piece is hit. Returns the visited squares,
    including the starting point and the blocking piece's square (if any).
    Used by queen/rook/bishop move generation.
    """
    if 'line' in debug: print(f'line (point, direc, ignore_peices) -> {point} {direc} {ignore_peices}')

    tx, ty = point
    sign = tellsign(board[tx][ty])
    result = [(tx, ty)]
    while True:
        if 'n' in direc: tx -= 1
        if 's' in direc: tx += 1
        if 'w' in direc: ty -= 1
        if 'e' in direc: ty += 1

        if 0 <= tx < 8 and 0 <= ty < 8:
            if tellsign(board[tx][ty]) in ignore_peices:
                result.append((tx, ty))
            elif tellsign(board[tx][ty]) == -sign:
                result.append((tx, ty))
                break
            else:
                break
        else:
            break
    return result


def calnextmoves(board, x, y):
    """
    Move generation for the piece at (x, y).
    Returns (next_moves, capture_moves) as lists of (row, col) tuples.
    Pure function: no drawing, no globals, no check/pin/castling logic.
    """
    if 'calnextmoves' in debug: print(f'calnextmoves (x, y) -> {x} , {y}')

    sign = tellsign(board[x][y])
    next_moves = []
    capture_moves = []

    if board[x][y] in (-6, 6):  # pawn
        if board[x + sign][y] == 0:
            next_moves.append((x + sign, y))
            if board[x + 2 * sign][y] == 0 and x in (6, 1):
                next_moves.append((x + 2 * sign, y))
        for dy in (sign, -sign):
            tx, ty = x + sign, y + dy
            if 0 <= tx <= 7 and 0 <= ty <= 7 and tellsign(board[tx][ty]) == -sign:
                capture_moves.append((tx, ty))

    elif board[x][y] in (4, -4):  # knight
        offsets = [(1, 2), (1, -2), (-1, 2), (-1, -2),
                   (2, 1), (2, -1), (-2, 1), (-2, -1)]
        for dx, dy in offsets:
            tx, ty = x + dx, y + dy
            if 0 <= tx < 8 and 0 <= ty < 8:
                if board[tx][ty] == 0:
                    next_moves.append((tx, ty))
                elif tellsign(board[tx][ty]) == -sign:
                    capture_moves.append((tx, ty))

    elif board[x][y] in (2, -2):  # king — adjacent squares only, no check filtering
        offsets = [(1, 0), (-1, 0), (0, 1), (0, -1),
                   (1, 1), (-1, -1), (1, -1), (-1, 1)]
        for dx, dy in offsets:
            tx, ty = x + dx, y + dy
            if 0 <= tx < 8 and 0 <= ty < 8:
                if board[tx][ty] == 0:
                    next_moves.append((tx, ty))
                elif tellsign(board[tx][ty]) == -sign:
                    capture_moves.append((tx, ty))

    elif board[x][y] in (-1, 1):  # queen
        for direc in ('n', 'e', 'w', 's', 'nw', 'ne', 'sw', 'se'):
            for tx, ty in line(board, (x, y), direc)[1:]:
                if board[tx][ty] == 0:
                    next_moves.append((tx, ty))
                elif tellsign(board[tx][ty]) == -sign:
                    capture_moves.append((tx, ty))

    elif board[x][y] in (-3, 3):  # rook
        for direc in ('n', 'e', 'w', 's'):
            for tx, ty in line(board, (x, y), direc)[1:]:
                if board[tx][ty] == 0:
                    next_moves.append((tx, ty))
                elif tellsign(board[tx][ty]) == -sign:
                    capture_moves.append((tx, ty))

    elif board[x][y] in (-5, 5):  # bishop
        for direc in ('nw', 'ne', 'sw', 'se'):
            for tx, ty in line(board, (x, y), direc)[1:]:
                if board[tx][ty] == 0:
                    next_moves.append((tx, ty))
                elif tellsign(board[tx][ty]) == -sign:
                    capture_moves.append((tx, ty))

    if 'calnextmoves' in debug: print(f'calnextmoves (next_moves , capture_moves) -> {next_moves} , {capture_moves}')
    return next_moves, capture_moves


def apply_move(board, moves, old_loc, new_loc):
    """
    Move the piece at old_loc to new_loc. Mutates `board` in place and
    appends enough info to `moves` for backtrack() to undo it later.
    """
    ox, oy = old_loc
    nx, ny = new_loc
    pval = board[ox][oy]
    captured = board[nx][ny]

    if captured == 0:
        moves.append((pval, [ox, oy], [nx, ny]))
    else:
        moves.append((pval, [ox, oy], [nx, ny], captured))

    board[nx][ny] = pval
    board[ox][oy] = 0


def backtrack(board, moves):
    """Undo the last move recorded by apply_move(). Returns True if something was undone."""
    if not moves:
        return False
    last = moves.pop()
    if len(last) == 3:
        pval, oldloc, newloc = last
        board[newloc[0]][newloc[1]] = 0
    else:
        pval, oldloc, newloc, captured = last
        board[newloc[0]][newloc[1]] = captured
    board[oldloc[0]][oldloc[1]] = pval
    return True
