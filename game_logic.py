'''
this module contains the actual logic for the board game.
'''

#----------------------------------------variables-------------------------------------
board = [
        [3, 4, 5, 1, 2, 5, 4, 3],
        [6, 6, 6, 6, 6, 6, 6, 6],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [-6, -6, -6, -6, -6, -6, -6, -6],
        [-3, -4, -5, -1, -2, -5, -4, -3], ]
turn = -1 #1 for black's turn, -1 for white's turn
debug = ['click','numbers','calnextmoves'] #for printing debug info of func to console
current_peice , next_moves , capture_moves = () , [] , [] #stores the next possible moves for the current selected peice

#------------------------------------Helping Functions-----------------------------------

def tellsign(x): #returns from (-1 , 0 , +1) — the sign of the given number.
    return (x > 0) - (x < 0)

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


#--------------------------------------Main Functions-----------------------------------------

def calnextmoves(x , y): #tells the next possible moves for the given peice
    global current_peice , next_moves , capture_moves

    sign = tellsign(board[x][y])
    current_peice , next_moves , capture_moves = (x , y) , [] , []
    
    if 'calnextmoves' in debug:
        print(f'calnextmoves) -> peice:{(x , y)} , val:{ board[x][y] } , turn: {turn} ')

    #-------------------------------------
    if board[x][y] in (-6, 6):  # For PAWN
        if (0 <= (x+sign) <= 7) and (0 <= y <= 7): #single straight move
            if board[x + sign][y] == 0: next_moves.append((x + sign, y))

            if (0 <= (x + (2*sign)) <= 7) and (0 <= y <= 7): #double straight move
                if (board[x + 2 * sign][y] == 0) and (x in (6, 1)): next_moves.append((x + 2 * sign, y))

        if (0 <= (x+sign) <= 7) and (0 <= (y+sign) <= 7): #right side capture move
            if tellsign(board[x + sign][y + sign]) == -sign: capture_moves.append((x + sign, y + sign))
        if (0 <= (x+sign) <= 7) and (0 <= (y-sign) <= 7): #left side capture move
            if tellsign(board[x + sign][y - sign]) == -sign: capture_moves.append((x + sign, y - sign))

    #-------------------------------------
    if board[x][y] in (-3, 3):  # For ROOK
        directions = ['n','e','w','s'] #north,east,west,south
        for i in directions:
            points = line((x,y),i) ; points.pop(0)#deleting moving peice's name for next moves
            for j in range(len(points)):
                tx,ty = points[j]
                if (board[tx][ty] == 0): next_moves.append((tx,ty))
                elif (tellsign(board[tx][ty]) == -sign): capture_moves.append((tx,ty))

    #-------------------------------------
    elif board[x][y] in {-5,+5}: #for bishops
        directions = ['nw','ne','sw','se'] #north,east,west,south
        for i in directions:
            points = line((x,y),i) ; points.pop(0)#deleting moving peice's name for next moves
            for j in range(len(points)):
                tx,ty = points[j]
                if (board[tx][ty] == 0): next_moves.append((tx,ty))
                elif (tellsign(board[tx][ty]) == -sign): capture_moves.append((tx,ty))

    #-------------------------------------
    elif board[x][y] in {-1,+1}: #for queens
        directions = ['n','e','w','s' ,'nw','ne','sw','se'] #north,east,west,south
        for i in directions:
            points = line((x,y),i) ; points.pop(0)#deleting moving peice's name for next moves
            for j in range(len(points)):
                tx,ty = points[j]
                if (board[tx][ty] == 0): next_moves.append((tx,ty))
                elif (tellsign(board[tx][ty]) == -sign): capture_moves.append((tx,ty))

    #-------------------------------------
    elif board[x][y] in {2,-2}: #for kings
        offsets = [[0,0],[+1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,-1],[1,-1],[-1,1]]#points around king
        pass

    if 'calnextmoves' in debug:
        print(f'    next moves: {next_moves} ,capture moves: {capture_moves}')
    return (next_moves , capture_moves)