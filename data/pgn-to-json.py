import os
from sys import argv

import json
import re
'''
the format of the json is as follows

{
    <FEN string 1>:
    {
        count: <number of times the board has shown up>,
        moves: // the set of boards that have followed from this
        [
            <FEN string>,
            <FEN string>,
            ...
        ],
        games: // the set of games (in some string format) that the board was played
        [
            <descriptive game string>,
            <descriptive game string>,
            ...
        ]
    }
    <FEN string 2>:
    {
        ...
    }
    ...
}
            
'''

# loop through all the .pgn files in this directory
data_dir = 'raw-data'

# output/update data 
output_filename = 'move-data.json'

# this probably is not only not necessary but actively wrong
if os.path.isfile(output_filename):
    os.remove(output_filename)

outfile = open(output_filename, 'w')


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

    
    # given two locations as strings in algebraic notation,
    # determine if there are pieces obstructing the two
    # NOTE: the given locations must be in a straight line from one another, or this doesn't make sense
    def is_obstructed(self, pos1, pos2):
        convert_to_xy = lambda pos: (7 - (ord(pos[1]) - ord('1')), ord(pos[0]) - ord('a'))
        
        x1, y1 = convert_to_xy(pos1)
        x2, y2 = convert_to_xy(pos2)

        x_change = 1 if x1 < x2 else (0 if x1 == x2 else -1)
        y_change = 1 if y1 < y2 else (0 if y1 == y2 else -1)

        s,t = x1 + x_change, y1 + y_change
        while s != x2 or t != y2:
            if self._board[s][t] != 'x':
                return True
            
            s += x_change
            t += y_change
        
        return False


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


    # prints the board in a human-readable format (for debugging)
    def prettyprint(self):
        row_divider = ('+-'*8 + '+')
        encase = lambda strlist, div: div + (div.join(strlist)) + div 
        
        cleaned_board = [[ch if ch != 'x' else ' ' for ch in row] for row in self._board]
        
        print('  ' + row_divider)
        for i, row in enumerate(cleaned_board):
            print(str(8 - i), end=' ')
            print(encase(row, '|'))
            print('  ' + row_divider)
        print('   a b c d e f g h')


    # Given a halfmove in algebraic notation (devoid of context) alter the board state 
    # movestr does not contain the move number or marking for what turn it is, this is held in the board class
    # movestr is assumed to be valid. if it isn't, and is impossible to interpret (no piece able to make the given move)
    #    then the program crashes. 
    def makemove(self, movestr):
        # rank r is {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'}
        # file f is {'1', '2', '3', '4', '5', '6', '7', '8'}
        # converting {r, f} to { f -> [7, 0], r -> [0, 7] } 
        alg_to_coords = lambda r, f: (7 - (ord(f) - ord('1')) , ord(r) - ord('a'))
      
        
        if '+' not in movestr and '#' not in movestr:
            target = movestr[-2:] # all (non-castle) moves end with the target
        else:
            target = movestr[-3:-1] # if this is a check, ignore the +
    


        pieceloc = ['x', 'x', 'x'] # format: piece label, rank, file

        remove_enpassant = True # unless this move is a double pawn move, there is no enpassant

        castled = False
        promoted = False


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


        # if this is a promotion
        if '=' in movestr:
            r, f = alg_to_coords(*movestr[:2])
            self._board[r][f] = movestr[-1] if self._turn == 'w' else movestr[-1].lower()
            promoted = True
        # if this is a castle, move the king and rook correspondingly and disallow castles
        elif movestr == "O-O": # kingside 
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
            elif movestr[1] in 'abcdefgh' and movestr[2] in 'abcdefghx':
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
                        
                        if not self.is_obstructed( potential_locs[i], target ):
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
                    if distance(potential_locs[i][0], target[0]) == distance(potential_locs[i][1], target[1]) \
                      and not self.is_obstructed( potential_locs[i], target ):
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
                    rankdist = distance(potential_locs[i][0], target[0])
                    filedist = distance(potential_locs[i][1], target[1])

                    if (rankdist == filedist or rankdist == 0 or filedist == 0) \
                      and not self.is_obstructed( potential_locs[i], target ):
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
            
                # check if this was an enpassant capture if possible
                if ''.join(target) == self._enpassant:
                    self._board[7 - (ord(self._enpassant[1]) - ord('1')) + (1 if self._turn == 'w' else -1)][ord(self._enpassant[0]) - ord('a')] = 'x'

            # otherwise, normal pawn move
            elif self._turn == 'w':
                coords = alg_to_coords(*target)
                # check one file below for the pawn
                if self._board[coords[0] + 1][coords[1]] == 'P':
                    pieceloc[2] = chr(ord(target[1]) - 1)
                elif self._board[coords[0] + 2][coords[1]] == 'P':
                    pieceloc[2] = chr(ord(target[1]) - 2)
                    self._enpassant = str(target[0]) + chr(ord(target[1]) - 1)
                    remove_enpassant = False
                else:
                    print(f"invalid pawn move {''.join(target)}")
            else: # normal black pawn move
                coords = alg_to_coords(*target)
                # check one file below for the pawn
                if self._board[coords[0] - 1][coords[1]] == 'p':
                    pieceloc[2] = chr(ord(target[1]) + 1)
                elif self._board[coords[0] - 2][coords[1]] == 'p':
                    pieceloc[2] = chr(ord(target[1]) + 2)
                    self._enpassant = str(target[0]) + chr(ord(target[1]) + 1)
                    remove_enpassant = False
                else:
                    print(f"invalid pawn move {''.join(target)}")

        self._turn = 'w' if self._turn == 'b' else 'b'
        if remove_enpassant:
            self._enpassant = ''

        if castled or promoted: return

        # replace the piece's starting location with a blank, replace the piece's target with the name
        target_coords = alg_to_coords(*target)
        self._board[target_coords[0]][target_coords[1]] = pieceloc[0]

        start_coords = alg_to_coords(*pieceloc[1:])
        self._board[start_coords[0]][start_coords[1]] = 'x'

# end board class

"""
b = Board()
b._board[-1] = ['R', 'N', 'B', 'x', 'x', 'x', 'x', 'R']
b.makemove('Rd1')
print(b.getFEN())
"""

output_data = {}

def addDatum(FEN):
    if FEN in output_data:
        return

    output_data[FEN] = { \
        'count': 1,  \
        'moves': [], \
        'games': []  \
    }

def visitBoard(currFEN, game, prevFEN = None):
    if currFEN not in output_data:
        addDatum(currFEN)
    else:
        output_data[currFEN]['count'] += 1

    output_data[currFEN]['games'].append(game)

    if prevFEN != None:
        output_data[prevFEN]['moves'].append(currFEN)




def parsePGN(filename, ):
    f = open(filename, 'r')

    curr_board = Board()

    # every iteration of this loop will either be a blank line or encapsulate a full game, assuming each game is of the form
    #
    # [Title "Data"]
    # [Title "Data"]
    #       .
    #       .
    #       .
    # 
    # < Game in PGN format
    # Broken by any amount 
    # of line breaks >
    # 


    while (line := f.readline()) != '':
        continue_writing = True
        
        if len(line) < 3:
            continue
        
        # given all the game data we have, form a string that represents the game
        # STRING FORMAT: LOCATION, EVENT, WHITE, BLACK
        def get_title(string):
            # assumes everything before ' "' is the title, everything after is the data
            return string[1 : string.index(' "')]
    
        def get_quoted(string):
            # finds the part of the string in quotes
            firstquot = string.index('"')
            secondquot = string.index('"', firstquot+1)
            return string[firstquot+1 : secondquot]
        

        # read all the metadata about the game
        gamedata = {}
        while line[0] == '[':
            gamedata[get_title(line)] = get_quoted(line)
            line = f.readline()
        # line is now at the blank line in between the metadata and the PGN

        relevant_data = ("Site", "Event", "White", "Black")
        vals = []
        for key in relevant_data:
            if key in gamedata:
                vals.append(gamedata[key])
        gamestr = ', '.join(vals)

        # gamestr = ', '.join([gamedata[key] for key in ('Site', 'Event', 'White', 'Black')])
        # print(f"\n{gamestr}")

        curr_board = Board()

        prevFEN = ''
        currFEN = curr_board.getFEN()
        visitBoard(currFEN, gamestr)

        
        piece_regex = re.compile('(([RBNQK]|[a-h])?[a-h]?[1-8]?x?[a-h][1-8](\+|#)?)|O-O(-O)?|[a-h][18]=[RBKQ]')
        def is_move(movestr):
            return re.fullmatch(piece_regex, movestr) is not None
            '''
                                 captures v                    v alternatively, castle
            '(([RBNQK]|[a-h])?[a-h]?[1-8]?x?[a-h][1-8](\+|#)?)|O-O(-O)?|[a-h][18]=[RBKQ]'
               ^piece  ^pawn   ^     ^      ^-target-^ ^check/mate      ^ alternatively promote
                               |-----+--distinguishes rank or file if necessary
            '''

        # lines in this loop are of the form "n.moveA moveB m.moveC moveD ...\n" 
        while len(line := f.readline()) > 1:
            if not continue_writing:
                continue

            # split into tokens by '.'
            # most tokens are of the form "moveX moveY k", 
            # except the first is of the form "n" and the last is of the form "moveX moveY\n" 
            temp = line.split('.') 

            # preliminary going through the line and finding each of the moves in the line
            moves = []
            for tok in temp:
                potential_moves = tok.split()
                for move in potential_moves:
                    if is_move(move):
                        moves.append(move)


            # now that we've isolated the algebraic notation of every move in this line
            # run it on the board and adjust the data
            for move in moves:
                # print(f"{'white' if curr_board._turn == 'w' else 'black'} {move}")

                # if there is some problem with the data or with my program (it's possible!)
                # just drop the rest of this board -- there is enough data to go around
                try:
                    curr_board.makemove(move)
                except:
                    continue_writing = False
                    break

                prevFEN, currFEN = currFEN, curr_board.getFEN()
                visitBoard(currFEN, gamestr, prevFEN)
                #curr_board.prettyprint() 
        
    
    f.close()

# parsePGN('raw-data/Bucharest2021.pgn')
for filename in os.listdir(data_dir):
    if filename.endswith('.pgn'):
        print(filename)
        parsePGN(os.path.join(data_dir, filename))


json.dump(output_data, outfile)
outfile.close()
