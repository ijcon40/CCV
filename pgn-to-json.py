import os
from sys import argv

# loop through all the .pgn files in this directory
data_dir = 'raw-data'

# output/update data 
output_file = 'move-data.json'

# command line argument to decide if we overwrite or update the existing data (if it exists)
if len(argv) > 1 and argv[1] == '-overwrite':
    if os.path.isfile(output_file):
        os.remove(output_file)


class Board:
    # initializes a board in the starting position
    def __init__(self):
        self._board = [\
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'], \
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'], \
            ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'], \
            ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'], \
            ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'], \
            ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'], \
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'], \
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'], \
        ]
        self._turn = 'w'
        self._castle = ['K', 'Q', 'k', 'q']
        self._enpassant = ''


    # translate the board state to FEN
    def getFEN(self):
        FEN = ''
        for row in self._board:
            count_spaces = 0
            for i in range(8):
                if row[i] == 'x':
                    count_spaces += 1
                else:
                    FEN += str(count_spaces) if count_spaces != 0 else ''
                    FEN += row[i]
                    count_spaces = 0
            
            if count_spaces != 0:
                FEN += str(count_spaces)
            
            if row != self._board[-1]:
                FEN += '/'

        FEN += ' ' + self._turn
        FEN += ' ' + (''.join(self._castle) if len(self._castle) > 0 else '-')
        FEN += ' ' + (self._enpassant if self._enpassant != '' else '-')

        return FEN        


    # Given a halfmove in algebraic notation (devoid of context) alter the board state 
    # movestr does not contain the move number or marking for what turn it is, this is held in the board class
    # movestr is assumed to be valid. if it isn't, and is impossible to interpret (no piece able to make the given move)
    #    then the program crashes. 
    def makemove(self, movestr):
        # rank r is {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'}
        # file f is {'1', '2', '3', '4', '5', '6', '7', '8'}
        # converting {r, f} to { f -> [7, 0], r -> [0, 7] } 
        alg_to_coords = lambda r, f: (7 - (ord(f) - ord('1')) , ord(r) - ord('a'))
      
        
        if '+' not in movestr:
            target = movestr[-2:] # all (non-castle) moves end with the target
        else:
            target = movestr[-3:-1] # if this is a check, ignore the +

        pieceloc = ['x', 'x', 'x'] # format: piece label, rank, file

        self._enpassant = '' # unless this move is a double pawn move, there is no enpassant

        castled = False
        
        # if a piece is moving to any of these squares, then it's removing the castle from that rook
        if 'K' in self._castle and target[1:] == ['h', '1']:
            self._castle.remove('K')
        elif 'Q' in self._castle and target[1:] == ['a', '1']:
            self._castle.remove('Q')
        elif 'k' in self._castle and target[1:] == ['h', '8']:
            self._castle.remove('k')
        elif 'q' in self._castle and target[1:] == ['a', '8']:
            self._castle.remove('q')


        # if this is a king move, get rid of the potential to castle 
        if movestr[0] == 'K':
            if self._turn == 'w' and 'K' in self._castle:
                self._castle.remove('K')
            if self._turn == 'w' and 'Q' in self._castle:
                self._castle.remove('Q')
            if self._turn == 'b' and 'k' in self._castle:
                self._castle.remove('k')
            if self._turn == 'b' and 'q' in self._castle:
                self._castle.remove('q')


        # if this is a castle, move the king and rook correspondingly and disallow castles
        if movestr == "O-O": # kingside 
            if self._turn == 'w':
                if 'K' in self._castle: self._castle.remove('K')
                if 'Q' in self._castle: self._castle.remove('Q')
                f = 7 
            else:
                if 'k' in self._castle: self._castle.remove('k')
                if 'q' in self._castle: self._castle.remove('q')
                f = 0

            self._board[f][4] = 'x'
            self._board[f][6] = 'K' if self._turn == 'w' else 'k'
            self._board[f][7] = 'x'
            self._board[f][5] = 'R' if self._turn == 'w' else 'r'
            
            castled = True

        elif movestr == "O-O-O": # queenside
            if self._turn == 'w':
                if 'K' in self._castle: self._castle.remove('K')
                if 'Q' in self._castle: self._castle.remove('Q')
                f = 7 
            else:
                if 'k' in self._castle: self._castle.remove('k')
                if 'q' in self._castle: self._castle.remove('q')
                f = 0

            self._board[f][4] = 'x'
            self._board[f][2] = 'K' if self._turn == 'w' else 'k'
            self._board[f][0] = 'x'
            self._board[f][3] = 'R' if self._turn == 'w' else 'r'
            
            castled = True

        # if this is a piece move, look for the piece
        elif movestr[0] in 'RNBQK': 
            distance = lambda a, b: abs(ord(a) - ord(b))
            
            piece = pieceloc[0] = movestr[0] if self._turn == 'w' else movestr[0].lower()
            potential_locs = []
            for f, row in enumerate(self._board):
                for r, square in enumerate(row):
                    if square == piece:
                        potential_locs.append([ chr(r + ord('a')), str(8-f) ])

            # if there is only one piece with the right name and color, 
            # then we know it must be the one that made the move
            if len(potential_locs) == 1:
                pieceloc[1] = potential_locs[0][0]
                pieceloc[2] = potential_locs[0][1]
            
            # at this point, king moves are handled, since there can only be one king of any color
            # queen moves are not because of the potential for promotions

            # if all pieces can move to this square, the algebraic notation will demonstrate that
            elif movestr[1] in 'abcdefg' and movestr[2] in 'abcdefgx':
                for i in range(len(potential_locs)):
                    if potential_locs[i][0] == movestr[1]:
                        pieceloc[1] = potential_locs[i][0]
                        pieceloc[2] = potential_locs[i][1]
                        break
            elif movestr[1] in '12345678':
                for i in range(len(potential_locs)):
                    if potential_locs[i][1] == movestr[1]:
                        pieceloc[1] = potential_locs[i][0]
                        pieceloc[2] = potential_locs[i][1]
                        break

            # now, using the logic of the piece, look for the only one that can have moved to the target

            # rook - for one of the pieces, either the rank is the same, or the file is
            elif piece in 'rR': 
                for i in range(len(potential_locs)):
                    if (potential_locs[i][0] == target[0] and potential_locs[i][1] != target[1]) \
                      or (potential_locs[i][0] != target[0] and potential_locs[i][1] == target[1]):
                        
                        # TODO: account for obstructions

                        pieceloc[1] = potential_locs[i][0]
                        pieceloc[2] = potential_locs[i][1]
                        break

                # check if this rook move removes a potential castle
                if 'K' in self._castle and pieceloc[1:] == ['h', '1']:
                    self._castle.remove('K')
                elif 'Q' in self._castle and pieceloc[1:] == ['a', '1']:
                    self._castle.remove('Q')
                elif 'k' in self._castle and pieceloc[1:] == ['h', '8']:
                    self._castle.remove('k')
                elif 'q' in self._castle and pieceloc[1:] == ['a', '8']:
                    self._castle.remove('q')

            # bishop - for one of the pieces, the absolute distance between the rook and file are the same
            elif piece in 'bB': 
                for i in range(len(potential_locs)):
                    if distance(potential_locs[i][0], target[0]) == distance(potential_locs[i][1], target[1]):
                        # TODO: account for obstructions
                        pieceloc[1] = potential_locs[i][0]
                        pieceloc[2] = potential_locs[i][1]
                        break

            # knight - for one of the pieces, the distance on one axis is 1, the distance on the other is 2
            elif piece in 'nN':
                for i in range(len(potential_locs)):
                    rankdist = distance(potential_locs[i][0], target[0])
                    filedist = distance(potential_locs[i][1], target[1])

                    if (rankdist == 1 and filedist == 2) or (rankdist == 2 and filedist == 1):
                        pieceloc[1] = potential_locs[i][0]
                        pieceloc[2] = potential_locs[i][1]
                        break
            
            # queen - for one of the pieces, the distance on either axis is the same, or one of them is 0
            else:
                for i in range(len(potential_locs)):
                    # TODO: account for obstructions
                    rankdist = distance(potential_locs[i][0], target[0])
                    filedist = distance(potential_locs[i][1], target[1])

                    if rankdist == filedist or rankdist == 0 or filedist == 0:
                        pieceloc[1] = potential_locs[i][0]
                        pieceloc[2] = potential_locs[i][1]
                        break

        # at this point, we know it was a pawn move
        # look for the pawn that moved and make it

        else: 
            pieceloc[0] = 'P' if self._turn == 'w' else 'p'
            # every pawn move starts with the rank
            pieceloc[1] = movestr[0]

            if movestr[1] == 'x': # pawn capture 
                # if the turn is white, move down a file, otherwise move up a file
                
                pieceloc[2] = chr(ord(movestr[3]) - (1 if self._turn == 'w' else -1))
            # otherwise, normal pawn move
            elif self._turn == 'w':
                coords = alg_to_coords(*target)
                # check one file below for the pawn
                if self._board[coords[0] + 1][coords[1]] == 'P':
                    pieceloc[2] = chr(ord(target[1]) - 1)
                elif self._board[coords[0] + 2][coords[1]] == 'P':
                    pieceloc[2] = chr(ord(target[1]) - 2)
                    self._enpassant = str(target[0]) + chr(ord(target[1]) - 1)
                else:
                    print(f"invalid pawn move {''.join(target)}")
            else: # normal black pawn move
                coords = alg_to_coords(*target)
                # check one file below for the pawn
                if self._board[coords[0] - 1][coords[1]] == 'p':
                    pieceloc[2] = chr(ord(target[1]) + 1)
                elif self._board[coords[0] - 2][coords[1]] == 'p':
                    pieceloc[2] = chr(ord(target[1]) + 2)
                    self._enpassant = str(target[0]) + chr(ord(target[1]) - 1)
                else:
                    print(f"invalid pawn move {''.join(target)}")

        self._turn = 'w' if self._turn == 'b' else 'b'
        if castled: return

        # replace the piece's starting location with a blank, replace the piece's target with the name
        target_coords = alg_to_coords(*target)
        self._board[target_coords[0]][target_coords[1]] = pieceloc[0]

        start_coords = alg_to_coords(*pieceloc[1:])
        self._board[start_coords[0]][start_coords[1]] = 'x'

# end board class

def parsePGN(filename):
    f = open(filename, 'r')

    in_game = False
    curr_board = Board()

    for line in f:
        # if this line marks the beginning of a game, enter in_game state
        if len(line) >= 2 and line[:2] == '1.':
            in_game = True         
        
        if line[0] == '[':
            continue

        # if we are presently in game, make the moves, parse them, add them to the json
        temp = line.split('.')    
        moves = []
        for tok in temp:
            move = tok.split(' ')
            if len(move) == 3: # of the form 'white black next_turn'
                moves.extend(move[:2])
            elif len(move) == 2: # of the form 'white black\n'
                moves.append(move[0])
                moves.append(move[1][:-1])
            else:
                continue
       
        for move in moves:
            if len(move) >= 2:
                curr_board.makemove(move)

        # if the end of this line contains an 'end of game marker', i.e. 0-1, 1/2-1/2, 1-0
        # then we have finished parsing the game, and we can continue looking for the next one
        if line.split(' ')[-1] in ('0-1\n', '1/2-1/2\n', '1-0\n'):
            print(curr_board.getFEN())
            curr_board = Board()
            in_game = False

    f.close()


parsePGN('raw-data/Bucharest2021.pgn')
