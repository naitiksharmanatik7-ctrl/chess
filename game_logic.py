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
kingspos = [(0,4) , (7,4)] #stores the position of kings (black , white) for checks and pins
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
            elif tellsign(board[tx][ty]) == -turn: result.append((tx,ty)) ; break #Reached Opponent's Peice 
            else: break #Reached End
        else: break

    return result

def pins(turn): #Returns peices locations which are pinned for a king 
    result = {} #(pinned peice : line of attack) line of attack -> (king , ... pinned peice ... , opponent's peice)

    dir = ['n','e','w','s']
    for i in dir:
        line1 = line(kingspos[turn == -1] , i , turn = turn , signs_in_list = [0 , turn]) #getting the line from king to the direction till the end or opponent's peice
        line_of_attack = line1.copy()
        
        if len(line1) < 3: continue #if the line is less than 3 , then continue
        if board[line1[-1][0]] [line1[-1][1]] in [3 * -turn , 1 * -turn]: #if the last peice in the line is a (rook , queen) of opponent's sign
            line1.pop(-1) ; line1.pop(0) 
            line1 = [i for i in line1 if board[i[0]] [i[1]] != 0] #getting the positions of the peices in the line
            if len(line1) == 1: result[line1[0]] = line_of_attack #if there is only one peice in the line , then it is pinned

    dir = ['ne','se','sw','nw']
    for i in dir:
        line1 = line(kingspos[turn == -1] , i , turn = turn , signs_in_list = [0 , turn]) #getting the line from king to the direction till the end or opponent's peice
        line_of_attack = line1.copy()

        if len(line1) < 3: continue #if the line is less than 3 , then continue
        if board[line1[-1][0]] [line1[-1][1]] in [5 * -turn , 1 * -turn]: #if the last peice in the line is a (bishop , queen) of opponent's sign
            line1.pop(-1) ; line1.pop(0)
            line1 = [i for i in line1 if board[i[0]] [i[1]] != 0] #getting the positions of the peices in the line
            if len(line1) == 1: result[line1[0]] = line_of_attack #if there is only one peice in the line , then it is pinned

    return result

def is_square_attacked(x , y , turn ,tab = 0): #checks if the square is attacked by opponent's peice or not
    result = False #; turn = -turn #to check for opponent's peices
    os = -turn #opponent's sign 
    by_whom = []

    if 'is_square_attacked' in debug:
        print(f'{tab * "    "}==>(is_square_attacked) -> square: {(x , y)} , turn: {turn}')

    #checking from all directions for (rook , bishop , queen)
    #queen
    dir = ['n','e','w','s' ,'nw','ne','sw','se'] #north , east... , north_west , north_east... etc
    for i in dir:
        line1 = line((x,y) , i , turn = turn)
        if len(line1) == 1: continue #if there is only you in the line , then continue
        if board[ line1[-1][0] ][ line1[-1][1]] == os*1: result = True ; by_whom.append(line1[-1]) ; break
    #rook
    dir = ['n','e','w','s'] #north , east... 
    for i in dir:
        line1 = line((x,y) , i , turn = turn)
        if len(line1) == 1: continue #if there is only you in the line , then continue
        if board[ line1[-1][0] ][ line1[-1][1]] == os*3: result = True ; by_whom.append(line1[-1]) ; break
    #bishop
    dir = ['nw','ne','sw','se'] #north , east... , north_west , north_east... etc
    for i in dir:
        line1 = line((x,y) , i , turn = turn)
        if len(line1) == 1: continue #if there is only you in the line , then continue
        if board[ line1[-1][0] ][ line1[-1][1]] == os*5: result = True ; by_whom.append(line1[-1]) ; break

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
        print(f'{tab * "    "}    result: {result} , by_whom: {by_whom}')
    return result , by_whom
                

#--------------------------------------Main Functions-----------------------------------------

def calnextmoves(x , y , tab = 0): #tells the next possible moves for the given peice
    sign = tellsign(board[x][y])
    current_peice , next_moves , capture_moves = (x , y) , [] , []
    
    if 'calnextmoves' in debug:
        print(f'{tab * "    "}==>(calnextmoves) -> peice:{(x , y)} , val:{ board[x][y] } , turn: {turn} ')

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
    elif board[x][y] in (-5,+5): #for bishops
        directions = ['nw','ne','sw','se'] #north,east,west,south
        for i in directions:
            points = line((x,y),i) ; points.pop(0)#deleting moving peice's name for next moves
            for j in range(len(points)):
                tx,ty = points[j]
                if (board[tx][ty] == 0): next_moves.append((tx,ty))
                elif (tellsign(board[tx][ty]) == -sign): capture_moves.append((tx,ty))

    #-------------------------------------
    elif board[x][y] in (4,-4): # for knights
        offsets = [[+1,+2],[+1,-2],[-1,+2],[-1,-2]  ,  [+2,+1],[+2,-1],[-2,+1],[-2,-1]]

        for i in offsets:
            tx , ty = x+i[0] , y+i[1] #adding offsets to current location

            if (0 <= tx < 8) and (0 <= ty < 8): #if point is in the board , then
                if (board[tx][ty] == 0): next_moves.append( (tx,ty) )
                elif (tellsign(board[tx][ty]) == -sign): capture_moves.append( (tx,ty) )

    #-------------------------------------
    elif board[x][y] in (-1,+1): #for queens
        directions = ['n','e','w','s' ,'nw','ne','sw','se'] #north,east,west,south

        for i in directions:
            points = line((x,y),i) ; points.pop(0)#deleting moving peice's name for next moves

            for j in range(len(points)):
                tx,ty = points[j]
                if (board[tx][ty] == 0): next_moves.append((tx,ty))
                elif (tellsign(board[tx][ty]) == -sign): capture_moves.append((tx,ty))

    #-------------------------------------
    elif board[x][y] in (2,-2): #for kings
        offsets = [[0,0],[+1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,-1],[1,-1],[-1,1]]#points around king

        for i in offsets:
            tx , ty = x+i[0] , y+i[1] #adding offsets to current location

            if (0 <= tx < 8) and (0 <= ty < 8): #if point is in the board , then
                if (board[tx][ty] == 0) and (not is_square_attacked(tx , ty , turn , tab = 2)[0]): next_moves.append( (tx,ty) )
                elif (tellsign(board[tx][ty]) == -sign) and (not is_square_attacked(tx , ty , turn , tab = 2)[0]): capture_moves.append( (tx,ty) )

    #check detection logic---------------------------------------------------------
    our_king_pos = kingspos[turn == -1] #getting our king's position
    ischecked , by_whom = is_square_attacked(*our_king_pos , turn = turn , tab = 2) #checking if our king is in check or not
    if ischecked:
        if 'calnextmoves' in debug:
            print(f'{tab * "    "} our king is in check by {by_whom} , possible_next_moves: {next_moves} , possible_capture_moves: {capture_moves}')
        
        if len(by_whom) > 1: #if there are more than one peices attacking our king
            pass
        elif len(by_whom) == 1:
            attacker = by_whom[0]
            if abs(board[attacker[0]][attacker[1]]) in (1,3,5): #if attacker is a ( queen , rook , bishop ) , then:
                direc = ''
                if (our_king_pos[0] - attacker[0]) > 0: direc += 'n'
                elif (our_king_pos[0] - attacker[0]) < 0: direc += 's'
                if (our_king_pos[1] - attacker[1]) > 0: direc += 'w'
                elif (our_king_pos[1] - attacker[1]) < 0: direc += 'e'

                line_of_attack = line(our_king_pos , direc , turn = turn) #getting the line of attack from king to attacker
                line_of_attack.pop(0) #removing the king's position from it
                line_of_attack.pop(-1) #removing the attacker's position from it

                #now next moves will be intersection of next moves and line of attack
                next_moves = [i for i in next_moves if i in line_of_attack]
                if attacker in capture_moves: capture_moves = [attacker] #if attacker is in capture moves , then we can only capture it
                else: capture_moves = [] 

            elif abs(board[attacker[0]][attacker[1]]) in (4 , 6): #if attacker is a knight or pawn, then we can only capture it
                if attacker in capture_moves: capture_moves = [attacker]
                else: capture_moves = []
                next_moves = [] #we can't move anywhere else

    #pining logic---------------------------------------------------------------------------
    pinned_peices = pins(turn) #getting the pinned peices for the current turn
    if current_peice in pinned_peices:
        if 'calnextmoves' in debug: print(f'{tab * "    "} given peice is pinned')
        line_of_attack = pinned_peices[current_peice] ; attacker = line_of_attack[-1]
        line_of_attack.pop(0) ; line_of_attack.pop(-1) #removing the king and attacker from the line of attack
        
        next_moves = [i for i in next_moves if i in line_of_attack] #Intersection of line of attack and next moves
        if attacker in capture_moves: capture_moves = [attacker]
        else: capture_moves = []

    if 'calnextmoves' in debug:
        print(f'{tab * "    "} next moves: {next_moves} ,capture moves: {capture_moves}')
    return (next_moves , capture_moves)