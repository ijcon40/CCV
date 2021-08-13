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
        
        target = movestr[-2:] # all (non-castle) moves end with the target
        pieceloc = ['x', 'x', 'x'] # format: piece label, rank, file

        self._enpassant = '' # unless this move is a double pawn move, there is no enpassant

        castled = False

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
            pieceloc[0] = movestr[0] if self._turn == 'w' else movestr[0].lower()
            

        
        # otherwise look for the pawn that moved  
        else: 
            pieceloc[0] = 'P' if self._turn == 'w' else 'p'
            # every pawn move starts with the rank
            pieceloc[1] = movestr[0]

            if movestr[1] == 'x': # pawn capture pawn
                # if the turn is white, move down a file, otherwise move up a file
                pieceloc[2] = chr(ord(movestr[-1]) - (1 if self._turn == 'w' else -1))
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

b = Board()
b._board[7] = ['R', 'x', 'x', 'x', 'K', 'B', 'N', 'R']
b.makemove('O-O-O')
print(b.getFEN())

def parsePGN(filename):
    f = open(filename, 'r')

    in_game = False
    curr_board = Board()

    for line in f:
        # if this line marks the beginning of a game, enter in_game state
        if len(line) >= 2 and line[:2] == '1.':
            in_game = True         
        
        # if we are presently in game, make the moves, parse them, add them to the json


        # if the end of this line contains an 'end of game marker', i.e. 0-1, 1/2-1/2, 1-0
        # then we have finished parsing the game, and we can continue looking for the next one
        if line[-1] in ('0-1', '1/2-1/2', '1-0'):
            in_game = False
