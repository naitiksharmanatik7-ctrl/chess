# Example file showing a basic pygame "game loop"
import pygame as pg
from PIL import Image

'''
make sure you are running it in python 3.12 (for pygame) above modules are installed
--> board: 500 x 500 | cell = 62.5 x 62.5 | peice in array = 60 x 60
--> black_queen: 1  | black_king: 2  | black_rook: 3  | black_knight: 4  | black_bishop: 5  | black_pawn: 6
--> white_queen: -1 | white_king: -2 | white_rook: -3 | white_knight: -4 | white_bishop: -5 | white_pawn: -6
--> Nothing: 0
example to place a black knight:  screen.blit(peices,(5*(cell) +20 , 2*cell +20),pg.Rect(3*peices_side,0,peices_side,peices_side))
'''

print('\n\n\n\n\n\n+1 sign = black peices and -1 sign = white peices \n')

moves = [] 
kingloc = [[7,4],[0,4],'wnotmoved','bnotmoved']#contains kings location = [white_king , black_king ,white_king_moved , black_king_moved]
isrookmoved = ['wlnotmoved','wrnotmoved','blnotmoved','brnotmoved']#[white_left_rook_moved , white_right_rook_moved , black_left_rook_moved , black_right_rook_moved]
flag = []
board_imgpath = r'assets\chessboard3.png'
peices_imgpath = r'assets\chess_pieces.png'
pins = {}#it contains info of pinned peices in format {peice location : pinning peice location}

# pygame setup
pg.init()
with Image.open(board_imgpath) as img:
    width, height = img.size
    if width == height: board_side = width
    else: print('board image is not square');quit()

with Image.open(peices_imgpath) as img:
    width, height = img.size
    peices_side = width//6

cell = (board_side/8) ; offset = int(cell/3)

screen = pg.display.set_mode((board_side +2*offset , board_side +2*offset)) ;screen.fill('gray')
clock = pg.time.Clock()
running = True
boardimg = pg.image.load(board_imgpath)
peices = pg.image.load(peices_imgpath)
text_font = pg.font.Font(None , int(cell/2.4))
#title
pg.display.set_caption("CHESS")
icon = pg.Surface((32, 32))
icon.fill((0, 0, 0)) ;pg.draw.circle(icon, (255, 0, 0), (16,16), 7)
pg.display.set_icon(icon)

#---------------------------------------------------------------------------------------------
board = []
def numbers():
    for i in range(8):
        tsur1 = text_font.render(str(i),True,'black') 
        tsur2 = text_font.render(str(i),True,'black')

        screen.blit(tsur1 , (offset/4  ,  (i)*cell + offset + int(cell/2.5)))
        screen.blit(tsur2 , ((i)*cell + offset + int(cell/2.5)  ,  offset/4))

def initial():#setup's board variable in that list in required format
    order = [3,4,5,1,2,5,4,3]
    board.append(order);board.append([6,6,6,6 ,6,6,6,6])
    for i in range(4):board.append([0,0,0,0 ,0,0,0,0])
    board.append([-6,-6,-6,-6 ,-6,-6,-6,-6]);board.append([-3,-4,-5,-1,-2,-5,-4,-3])

def load_board():
    screen.blit(boardimg,(offset,offset))
    for i in range(len(board)):
        for j in range(len(board[i])):
            val = board[i][j]

            if val>0:
                croppedsec = peices.subsurface( pg.Rect((val-1)*peices_side,0,peices_side,peices_side) )
                peiceimg = pg.transform.smoothscale(croppedsec, (cell , cell) )
                screen.blit(peiceimg , (j*cell +offset , i*cell +offset))

            elif val<0:
                croppedsec = peices.subsurface( pg.Rect(-(val+1)*peices_side,peices_side,peices_side,peices_side) )
                peiceimg = pg.transform.smoothscale(croppedsec, (cell , cell) )#scaling cropped image to cell size
                screen.blit(peiceimg , (j*cell +offset , i*cell +offset))
            else:pass

def highlight(x,y,color = (235,215,0)):#position of cell on board acc to number lines
    #(object , color , rect , border_width)
    if (0<=x<8)and(0<=y<8):
        pg.draw.rect(screen , color , ((y)*cell+offset , (x)*cell+offset , cell , cell) , 4)

def tellsign(x):return (x > 0) - (x < 0)

def rectangle(x,y):
    pg.draw.rect(screen,(173, 43, 31),((y)*cell+offset , (x)*cell+offset , cell , cell),3)

def draw_circle(x,y):
    if board[x][y] == 0:
        pg.draw.circle(screen, (160, 250, 206), ((y)*cell +offset +(cell/2) , (x)*cell +offset +(cell/2)), 10)
    else:print(f'{x},{y} cant draw circle there as a peice exist there')

def line(point,direc,ignore_peices=[0]):#ignore peices contains signs of peices who we ignore
    tx,ty = point ;sign = tellsign(board[tx][ty]) ;result = [(tx,ty)]
    while (True):
        if 'n' in direc: tx -= 1
        if 's' in direc: tx += 1
        if 'w' in direc: ty -= 1
        if 'e' in direc: ty += 1

        if ((0<=tx<8) and (0<=ty<8)):
            if tellsign(board[tx][ty]) in ignore_peices: result.append((tx,ty))
            elif tellsign(board[tx][ty]) == -sign: result.append((tx,ty));break
            else: break
        else: break
    return result

def banned_pos(turn):#banned position for king
    global next_moves,change_peice
    #print('calculating banned positions')

    offsets = [[0,0],[+1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,-1],[1,-1],[-1,1]]#points around king
    points = [] ;result = [] ;king = []

    if turn == 1:  king = kingloc[1]
    if turn == -1: king = kingloc[0]

    for i in offsets:
        points.append( (king[0]+i[0] , king[1]+i[1]) )

    for i in range(len(board)):
        for j in range(len(board[i])):
            #print(i,j,':',board[i][j],' ',end='')
            if (tellsign(board[i][j]) == -turn):
                if (board[i][j] not in (2,-2)):
                    calnextmoves(i,j,show= False)
                    for k in points:
                        if k in next_moves: result.append(tuple(k))
                    next_moves = [] ;change_peice = []
                elif (board[i][j] == turn*2):
                    otherkpoi = []#other kings points
                    for k in offsets:
                        otherkpoi.append( (board[i][j]+k[0] , board[i][j]+k[1]) )
                    for l in points:
                        if l in otherkpoi: result.append(tuple(k))
                    

    next_moves = [] ;change_peice = []
    result = set(result)

    #print('banned positions:' ,result)
    return result

def direction(point1,point2):
    result = ''
    if point1[0] > point2[0]:result = result+'n'
    elif point1[0] < point2[0]:result = result+'s'

    if point1[1] > point2[1]:result = result+'w'
    elif point1[1] < point2[1]:result = result+'e'
    return result

def valid_points_in_check(sign): #sign to which check is came
    points = []
    if sign == 1:    king = kingloc[1]
    elif sign == -1: king = kingloc[0]

    if len(flag) == 2:
        peice = flag[-1] ;dir = direction(king,peice)
        points = line(king,dir)
        #print('vcheck:',dir,king,points)
    elif len(flag) == 3:
        pass

    return points

def values(list_of_points):
    result = []
    for i in list_of_points:
        result.append(board[i[0]][i[1]])
    return result

def ispinning(peice_loc):#checks does given peice is pinning any other peice or not
    #print('checking pinning for:' ,peice_loc)
    pl = peice_loc ;sign = tellsign(board[peice_loc[0]][peice_loc[1]])
    directions = ['n','e','w','s' ,'nw','ne','sw','se'] #north,east,west,south
    pinnedpeice = None

    for direc in directions:
        points = line(peice_loc,direc,ignore_peices=[ 0 , -tellsign(board[peice_loc[0]][peice_loc[1]]) ])
        val = values(points)
        if (-sign*2) in val:
            count = 0 
            for j in range(len(val)):
                if val[j] == -sign*2:break
                if tellsign(val[j]) == -sign: count += 1 ; pinnedpeice = points[j]
            if count == 1: return (True , (pinnedpeice,peice_loc))
    return (False , None)

def canitcastle(kinglocation):
    castle = [False, False] #castle = [leftside (true or false) , rightside (true or false)]
    kinginplaceleft = False #stores does king and rook are not moved and in their original place or not
    kinginplaceright = False

    if kinglocation == kingloc[0]:#white king
        if (kingloc[2] == 'wnotmoved'):
            if (isrookmoved[0] == 'wlnotmoved'): kinginplaceleft = True
            if (isrookmoved[1] == 'wrnotmoved'): kinginplaceright = True

    elif kinglocation == kingloc[1]:#black king
        if (kingloc[3] == 'bnotmoved'):
            if (isrookmoved[2] == 'blnotmoved'): kinginplaceleft = True
            if (isrookmoved[3] == 'brnotmoved'): kinginplaceright = True

    print('kinginplace:',kinginplaceleft,kinginplaceright,kinglocation,kingloc)
    if kinginplaceleft == True:
        #left side castle
        castle[0] = True
        for i in range(3):
            if board[7][i+1] != 0:castle[0] = False ;print('canitcastle:',7,i+1) ;break 

    if kinginplaceright == True:
        #right side castle
        castle[1] = True
        for i in range(2):
            if board[7][i+5] != 0:castle[1] = False ;print('canitcastle:',7,i+5) ;break 
    return castle

                
#change_peice = [peice value , location] , next_moves = [(x,y) , (x1,y1) , ...]
change_peice , next_moves = [],[]
def calnextmoves(x,y,show = True):
    global next_moves ,change_peice ,flag ,pins
    change_peice = [board[x][y],[x,y]] #it contains info of which peice position you want to change
    sign = tellsign(board[x][y]) ;capture_moves = []

    lines_of_check = None
    if len(flag) != 0:
        if (flag[0] == 'check') and (board[x][y] != sign*2):
            lines_of_check = valid_points_in_check(-tellsign( board [flag[1][0]] [flag[1][1]] ))
            lines_of_check.pop(0) #to remove king's loc from it who is in check
    
    #if peice is pinned then return as it can't move anywhere
    if ((x,y) in pins.keys()):
        print('this peice',(x,y),'is pinned by',pins[(x,y)])
        return None
    
    #--------------------------------------------------------------------------------------------------------------------------------------------------------
    if board[x][y] in {-6,+6}: #for pawn
        #for straight movement
        if board[x+sign][y] == 0:
            next_moves.append((x+sign,y))
            if (board[x+(2*sign)][y] == 0) and (x in {6,1}):
                next_moves.append((x+(2*sign),y))
        
        #for diagonal capture
        if (0<=(x+sign)<=7) and (0<=(y+sign)<=7) and (tellsign(board[x+sign][y+sign]) == -sign):
            capture_moves.append((x+sign,y+sign))

        if (0<=(x+sign)<=7) and (0<=(y-sign)<=7) and (tellsign(board[x+sign][y-sign]) == -sign):    
            capture_moves.append((x+sign,y-sign))
    #--------------------------------------------------------------------------------------------------------------------------------------------------------
    elif board[x][y] in {4,-4}: #for knights
        points = [[+1,+2],[+1,-2],[-1,+2],[-1,-2]  ,  [+2,+1],[+2,-1],[-2,+1],[-2,-1]]
        for i in points:
            tx,ty = x+i[0],y+i[1]
            if (0<=tx<8) and (0<=ty<8):
                if (board[tx][ty] == 0): next_moves.append((tx,ty))
                elif (tellsign(board[tx][ty]) == -sign): capture_moves.append((tx,ty))
    #--------------------------------------------------------------------------------------------------------------------------------------------------------
    elif board[x][y] in {2,-2}: #for kings
        temp = change_peice
        banpos = banned_pos(turn) ;points = set()
        offsets = [[0,0],[+1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,-1],[1,-1],[-1,1]]#points around king
        for i in offsets:
            if (0<=x+i[0]<8) and (0<=y+i[1]<8): points.add( (x+i[0] , y+i[1]) )

        next_moves.extend( list(points - banpos) )
        for i in list(next_moves):
            if tellsign(board[i[0]][i[1]]) == sign:  next_moves.remove(i)
            if tellsign(board[i[0]][i[1]]) == -sign: capture_moves.append(i) ;next_moves.remove(i)
        change_peice = temp
    #--------------------------------------------------------------------------------------------------------------------------------------------------------
    elif board[x][y] in {-1,+1}: #for queens
        directions = ['n','e','w','s' ,'nw','ne','sw','se'] #north,east,west,south
        for i in directions:
            points = line((x,y),i) ; points.pop(0)#deleting moving peice's name for next moves
            for j in range(len(points)):
                tx,ty = points[j]
                if (board[tx][ty] == 0): next_moves.append((tx,ty))
                elif (tellsign(board[tx][ty]) == -sign): capture_moves.append((tx,ty))
    #--------------------------------------------------------------------------------------------------------------------------------------------------------
    elif board[x][y] in {-3,+3}: #for rooks
        directions = ['n','e','w','s'] #north,east,west,south
        for i in directions:
            points = line((x,y),i) ; points.pop(0)#deleting moving peice's name for next moves
            for j in range(len(points)):
                tx,ty = points[j]
                if (board[tx][ty] == 0): next_moves.append((tx,ty))
                elif (tellsign(board[tx][ty]) == -sign): capture_moves.append((tx,ty))
    #--------------------------------------------------------------------------------------------------------------------------------------------------------
    elif board[x][y] in {-5,+5}: #for bishops
        directions = ['nw','ne','sw','se'] #north,east,west,south
        for i in directions:
            points = line((x,y),i) ; points.pop(0)#deleting moving peice's name for next moves
            for j in range(len(points)):
                tx,ty = points[j]
                if (board[tx][ty] == 0): next_moves.append((tx,ty))
                elif (tellsign(board[tx][ty]) == -sign): capture_moves.append((tx,ty))
    #--------------------------------------------------------------------------------------------------------------------------------------------------------
    
    #for checking pins of queen , rook and bishop
    if (board[x][y] in {-5,-3,-1,5,3,1}) and (board[x][y] not in pins.keys()):
        is_pinning, pin_info = ispinning((x,y))
        if is_pinning:
            print('pinning:',pin_info[0],'by:',pin_info[1])
            pins[pin_info[0]] = pin_info[1]

    if (lines_of_check != None) and (board[x][y] != sign*2):
        v ,n ,c = set(lines_of_check) ,set(next_moves) ,set(capture_moves)
        lines_of_check = list(v & (n | c)) #intersection btw n and v
    
    #graphics for moves
    if (show == True):
        if lines_of_check == None: #when there is no check
            for i in next_moves:    draw_circle (i[0],i[1])
            for i in capture_moves: rectangle (i[0],i[1])

        else: #when there is a check
            for i in lines_of_check:
                if (tellsign(board[i[0]][i[1]]) == 0): draw_circle (i[0],i[1])
                elif (tellsign(board[i[0]][i[1]]) == -sign): rectangle (i[0],i[1])

    if (board[x][y] != sign*2):
        if lines_of_check == None: next_moves.extend(capture_moves)
        else: next_moves = lines_of_check
    else: next_moves.extend(capture_moves)



turn = -1
def click(x,y):#checks clicks on board only
    global next_moves ,change_peice ,turn ,flag
    load_board();highlight(x,y)

    #condition for placing peices
    if ((x,y) in next_moves)and(change_peice!=[]):
        signol = (change_peice[0] > 0) - (change_peice[0] < 0)#sign of old location
        signnl = (board[x][y] > 0) - (board[x][y] < 0)#sign of old location

        if (signnl != signol) and (board[x][y] not in (-2,2)):
            #tracking moves for backtracking 
            if board[x][y] == 0: moves.append(( change_peice[0] , change_peice[1] , [x,y] ))
            else: moves.append(( change_peice[0] , change_peice[1] , [x,y] ,board[x][y]))

            # every time you place peice in check make flag back to None
            if flag != []: flag = []

            #placing peice
            board[x][y] = change_peice[0] ;x_,y_ = change_peice[1] ;board[x_][y_] = 0
            load_board()
            if (x in [7,0]) and (board[x][y]in[6,-6]):print('promotion case')

            #does king or rook moved (used for castelling)
            if (board[x][y] == 2): kingloc[1] = [x,y] ;kingloc[3] = 'bmoved' ;print(kingloc)
            elif (board[x][y] == -2): kingloc[0] = [x,y] ;kingloc[2] = 'wmoved' ;print(kingloc)
            if (board[x][y] == -3):
                if (y == 0): isrookmoved[0] = 'wlmoved' 
                elif (y == 7): isrookmoved[1] = 'wrmoved' 
                print(isrookmoved)
            elif (board[x][y] == 3):
                if (y == 0): isrookmoved[2] = 'blmoved' 
                elif (y == 7): isrookmoved[3] = 'brmoved' 
                print(isrookmoved)

            #checking for checks and king movements
            next_moves = [] ;change_peice = []
            calnextmoves(x,y,show = False);values = []
            for i in next_moves: values.append(board [i[0]] [i[1]] )
            #print('click check case\n',next_moves,'\n',values)
            if (-turn*2) in values:
                flag = ['check',change_peice[1]] ;print('check to:' ,-turn*2 ,'| flag:' ,flag)

            #banned_pos(turn)

            #after placing peice switching turn
            if (turn == 1):    turn = -1
            elif (turn == -1): turn = 1

            next_moves = [] ;change_peice = [] ;return None
    else: next_moves = [] ;change_peice = []

    if (board[x][y] != 0) and (tellsign(board[x][y]) == turn):
        calnextmoves(x,y)



def backtrack():
    if moves != []:
        if len(moves[-1]) == 3:
            pval,oldloc,newloc = moves[-1] ;board[newloc[0]][newloc[1]] = 0
        elif len(moves[-1]) == 4:
            pval,oldloc,newloc,eleminatedpval = moves[-1] 
            board[newloc[0]][newloc[1]] = eleminatedpval
        board[oldloc[0]][oldloc[1]] = pval
        load_board() ;moves.pop()
    else: print('No previous moves left')



initial();numbers()
load_board()

while running:
    for event in pg.event.get():
        
        if event.type == pg.MOUSEBUTTONDOWN:
            x, y = event.pos
            if (offset < x < (offset+cell*8)) and (offset < y < (offset+cell*8)): #for clicking on peices
                click(int((y-offset)/cell) , int((x-offset)/cell))
            #else: print('>>> please click inside the board')
            
        if event.type == pg.KEYDOWN: #for ctrl + z
            if event.key == pg.K_z and (event.mod & pg.KMOD_CTRL):
                backtrack()
        
        if event.type == pg.KEYDOWN: #for a
            if event.key == pg.K_a:
                print('a',canitcastle(kingloc[0]))

        if event.type == pg.QUIT:
            running = False;quit()
            
    pg.display.update()

    clock.tick(60)  # limits FPS to 60

#pg.quit()
