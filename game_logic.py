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
prev_peice , prev_valid_moves = () , [] #stores the info about previous peice's (location , valid moves) for placing that in (second click)

#------------------------------------Helping Functions-----------------------------------

def tellsign(x): #returns from (-1 , 0 , +1) — the sign of the given number.
    return (x > 0) - (x < 0)

def line(point , direc , turn = None , signs_in_list = [0]):
    # signs in list contain signs of those peices which we can contain in resultant list 
    # returns a line from a given peice : ['given peice', ... 'in between positions' ... , 'other peice or end']

    tx,ty = point ;result = [(tx,ty)]
    if turn is None: turn = tellsign(board[tx][ty]) #if turn is not given , then we will take the sign of the peice at the given point

    while (True):
        if 'n' in direc: tx -= 1
        if 's' in direc: tx += 1
        if 'w' in direc: ty -= 1
        if 'e' in direc: ty += 1

        if ((0 <= tx < 8) and (0 <= ty < 8)):
            if tellsign(board[tx][ty]) in signs_in_list: result.append((tx,ty)) 
            elif tellsign(board[tx][ty]) == -turn: result.append((tx,ty));break #Reached Opponent's Peice 
            else: break #Reached End
        else: break

    return result

def is_square_attacked(x , y , turn): #checks if the square is attacked by opponent's peice or not
    result = False #; turn = -turn #to check for opponent's peices
    os = -turn #opponent's sign 
    by_whom = []

    if 'is_square_attacked' in debug:
        print(f'==>(is_square_attacked) -> square: {(x , y)} , turn: {turn}')

    #checking from all directions for (rook , bishop , queen)
    dir = ['n','e','w','s' ,'nw','ne','sw','se'] #north , east... , north_west , north_east... etc
    for i in dir:
        line1 = line((x,y) , i , turn = turn)
        if board[ line1[-1][0] ][ line1[-1][1]] in (os*3 , os*5 , os*1): result = True ; by_whom.append(line1[-1]) ; break 

    #checking for knight's attack
    offsets = [[+1,+2],[+1,-2],[-1,+2],[-1,-2]  ,  [+2,+1],[+2,-1],[-2,+1],[-2,-1]]
    for i in offsets:
        tx , ty = x+i[0] , y+i[1] #adding offsets to current location

        if (0 <= tx < 8) and (0 <= ty < 8): #if point is in the board , then
            if board[tx][ty] == (os * 4): result = True ; by_whom.append((tx, ty)) ; break

    #checking for king's attack
    offsets = [[0,0],[+1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,-1],[1,-1],[-1,1]]#points around king
    for i in offsets:
        tx , ty = x+i[0] , y+i[1] #adding offsets to current location

        if (0 <= tx < 8) and (0 <= ty < 8): #if point is in the board , then
            if board[tx][ty] == (os * 2): result = True ; by_whom.append((tx, ty)) ; break

    #checking for pawn's attack
    if (0 <= (x + turn) < 8) and (0 <= (y + turn) < 8): #right side capture move
        if board[x + turn][y + turn] == (os * 6): result = True ; by_whom.append((x + turn, y + turn))
    if (0 <= (x + turn) < 8) and (0 <= (y - turn) < 8): #left side capture move
        if board[x + turn][y - turn] == (os * 6): result = True ; by_whom.append((x + turn, y - turn))

    if 'is_square_attacked' in debug:
        print(f'    result: {result} , by_whom: {by_whom}')
    return result
                

#--------------------------------------Main Functions-----------------------------------------

def calnextmoves(x , y): #tells the next possible moves for the given peice
    sign = tellsign(board[x][y])
    current_peice , next_moves , capture_moves = (x , y) , [] , []
    
    if 'calnextmoves' in debug:
        print(f'==>(calnextmoves) -> peice:{(x , y)} , val:{ board[x][y] } , turn: {turn} ')

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
                if (board[tx][ty] == 0):                 next_moves.append((tx,ty))
                elif (tellsign(board[tx][ty]) == -sign): capture_moves.append((tx,ty))

    #-------------------------------------
    elif board[x][y] in (-5,+5): #for bishops
        directions = ['nw','ne','sw','se'] #north,east,west,south
        for i in directions:
            points = line((x,y),i) ; points.pop(0)#deleting moving peice's name for next moves
            for j in range(len(points)):
                tx,ty = points[j]
                if (board[tx][ty] == 0):                 next_moves.append((tx,ty))
                elif (tellsign(board[tx][ty]) == -sign): capture_moves.append((tx,ty))

    #-------------------------------------
    elif board[x][y] in (4,-4): # for knights
        offsets = [[+1,+2],[+1,-2],[-1,+2],[-1,-2]  ,  [+2,+1],[+2,-1],[-2,+1],[-2,-1]]

        for i in offsets:
            tx , ty = x+i[0] , y+i[1] #adding offsets to current location

            if (0 <= tx < 8) and (0 <= ty < 8): #if point is in the board , then
                if (board[tx][ty] == 0):                 next_moves.append( (tx,ty) )
                elif (tellsign(board[tx][ty]) == -sign): capture_moves.append( (tx,ty) )

    #-------------------------------------
    elif board[x][y] in (-1,+1): #for queens
        directions = ['n','e','w','s' ,'nw','ne','sw','se'] #north,east,west,south

        for i in directions:
            points = line((x,y),i) ; points.pop(0)#deleting moving peice's name for next moves

            for j in range(len(points)):
                tx,ty = points[j]
                if (board[tx][ty] == 0):                 next_moves.append((tx,ty))
                elif (tellsign(board[tx][ty]) == -sign): capture_moves.append((tx,ty))

    #-------------------------------------
    elif board[x][y] in (2,-2): #for kings
        offsets = [[0,0],[+1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,-1],[1,-1],[-1,1]]#points around king

        for i in offsets:
            tx , ty = x+i[0] , y+i[1] #adding offsets to current location

            if (0 <= tx < 8) and (0 <= ty < 8): #if point is in the board , then
                if (board[tx][ty] == 0) and (not is_square_attacked(tx , ty , turn)):                 next_moves.append( (tx,ty) )
                elif (tellsign(board[tx][ty]) == -sign) and (not is_square_attacked(tx , ty , turn)): capture_moves.append( (tx,ty) )

    if 'calnextmoves' in debug:
        print(f'    next moves: {next_moves} ,capture moves: {capture_moves}')
    return (next_moves , capture_moves)