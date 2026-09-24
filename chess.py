import pygame as pg
from PIL import Image
import game_logic as gl

'''
--> board: 500 x 500 | cell = 62.5 x 62.5 | peice in array = 60 x 60
--> glack_queen: 1  | black_king: 2  | black_rook: 3  | black_knight: 4  | black_bishop: 5  | black_pawn: 6
--> white_queen: -1 | white_king: -2 | white_rook: -3 | white_knight: -4 | white_bishop: -5 | white_pawn: -6
--> Nothing: 0
example to place a black knight:  screen.blit(peices,(5*62.5 +20 , 2*62.5 +20),pg.Rect(3*60,0,60,60))
'''

#------------------variables-------------------
board_imgpath = r'assets\chessboard1.png' ; peices_imgpath = r'assets\chess_pieces.png'

with Image.open(board_imgpath) as img: #tells board image size
    width, height = img.size
    if width == height: board_side = width
    else: print('board image is not square');quit()

with Image.open(peices_imgpath) as img: #tells info about peices spritesheet
    w, h = img.size
    peices_side = int(w / 6) #tells peice side length based on spritesheet

cell = (board_side/8) ; offset = int(cell/3)

#-----------------pygame setup--------------
pg.init()

screen = pg.display.set_mode((board_side +2*offset , board_side +2*offset)) ;screen.fill('gray')
clock = pg.time.Clock()
board_pgobj = pg.image.load(board_imgpath)   #board pygame object
peices_pgobj = pg.image.load(peices_imgpath) #peices_pgobj 
text_font = pg.font.Font(None , int(cell/2.4))

screen.blit(board_pgobj, (offset, offset)) #draws board on screen

def numbers():
    if 'numbers' in gl.debug: #shows number based on its index on the board
        for i in range(8): #draws numbers 0 - 7 (vertically)
                number = text_font.render(str( i ),True,'black')
                screen.blit(number , (offset/3 , offset + (i)*(cell) + (cell/2)))
        for i in range(8): #draws numbers 0 - 7 (horizontally)
                number = text_font.render(str( i ),True,'black')
                screen.blit(number , (offset + (i)*(cell) + (cell/2) , offset/3))
        return

    for i in range(8): #draws numbers 1 - 8 (vertically)
        number = text_font.render(str( i+1 ),True,'black')
        screen.blit(number , (offset/3 , offset + (7 - i)*(cell) + (cell/2)))

    for i in ('a','b','c','d','e','f','g','h'): #draws letters a - h (ordinal value of a = 97) (horizontally)
        symbols = text_font.render(i,True,'black')
        screen.blit(symbols , (offset + (ord(i) - 97)*(cell) + (cell/2)  ,  offset + (cell*8)))
numbers()

#---Title and Logo---
pg.display.set_caption("CHESS")
icon = pg.image.load(r'assets\logo.jpg')
# icon.fill((0, 0, 0)) ;pg.draw.circle(icon, (255, 0, 0), (16,16), 7)
pg.display.set_icon( pg.transform.smoothscale(icon, (32, 32)) )

#-----------Helping Functions------------

def highlight(x, y, color=(235, 215, 0)):
    if 0 <= x < 8 and 0 <= y < 8:
        pg.draw.rect(screen, color, (y * cell + offset, x * cell + offset, cell, cell), 4)

def peicelookup(val): #provides the position of the peice in the spritesheet based on its value in the board array.
    if val == 0:
        return None
    elif val > 6 or val < -6:
        print(f"peicelookup -> Invalid piece value: {val}") ; quit()

    # (sheet_col, sheet_row) — row 0 = white, row 1 = black
    lookup = {
         1: (1, 1),  2: (1, 0),  3: (1, 4),  4: (1, 3),  5: (1, 2),  6: (1, 5),
        -1: (0, 1), -2: (0, 0), -3: (0, 4), -4: (0, 3), -5: (0, 2), -6: (0, 5),  }
    return lookup[val]

def draw_circle(x , y , clr = (160, 250, 206)):
    if gl.board[x][y] == 0:
        pg.draw.circle(screen, clr , ((y)*cell +offset +(cell/2) , (x)*cell +offset +(cell/2)), 10)
    else:print(f'{x},{y} cant draw circle there as a peice exist there')

def draw_rectangle(x , y , clr = (173, 43, 31)):
    pg.draw.rect(screen,clr,((y)*cell+offset , (x)*cell+offset , cell , cell),3)

#-----------Main Functions---------------

def load_board():
    screen.blit(board_pgobj, (offset, offset))
    for i in range(8):
        for j in range(8):
            val = gl.board[i][j]
            p = peicelookup(val)
            if p == None: continue #doing nothing for val = 0 

            crop = pg.Rect (p[1]*peices_side , p[0]*peices_side , peices_side , peices_side)
            screen.blit(peices_pgobj, (j * cell + offset, i * cell + offset), crop)


def click(row, col):
    if 'click' in gl.debug: print(f'(click) -> row: {row} , col: {col} , val: {gl.board[row][col]} , nextmoves: {gl.next_moves} , peice: {gl.current_peice}')
    load_board()
    highlight(row, col)

    # second click: attempt to move the selected piece to (x, y)
    if (row , col) in gl.next_moves and gl.current_peice:
        peice = gl.current_peice
        if 'click' in gl.debug:
            print(f'    peice moved from:{peice} to {(row , col)} \n')

        gl.board[row] [col] =  gl.board[peice[0]] [peice[1]]
        gl.board[peice[0]] [peice[1]] = 0
        load_board()

        gl.current_peice , gl.next_moves , gl.capture_moves = () , [] , [] #reseting used variables
        gl.turn *= -1 #toggling the turn 
        return 

    # first click: select a piece and calculate its next moves
    if (gl.board[row][col] != 0) and (gl.tellsign(gl.board[row][col]) == gl.turn):
        next, capture = gl.calnextmoves(row , col)

        for i in next: draw_circle(i[0] , i[1])
        for i in capture: draw_rectangle(i[0] , i[1])
        gl.next_moves = next + capture
        #draw_moves(quiet, capture)

load_board() #initial board load

#-----------pygame mainloop------------
while True:
    for event in pg.event.get():
        
        if event.type == pg.MOUSEBUTTONDOWN:
            x, y = event.pos
            if (offset < x < (offset+cell*8)) and (offset < y < (offset+cell*8)): #for clicking on peices
                click(int((y-offset)/cell) , int((x-offset)/cell))
            else: print('>>> please click inside the board')
            
        if event.type == pg.KEYDOWN: #for ctrl + z
            if event.key == pg.K_z and (event.mod & pg.KMOD_CTRL):
                pass
                #backtrack()

        if event.type == pg.QUIT:
            pg.quit() ; quit()
            
    pg.display.update()

    clock.tick(60)  # limits FPS to 60
