import copy

BOARD = 20
BLOCKS = 5

class Piece(object):
    
    FULL_SET = None
    
    def __init__(self, off):
        self.offsets = sorted(off)
        self._normalize()
        self.pos = (0,0)
    
    def moveto(self, newpos):
        self.pos = newpos
    
    def print_shape(self):
        max_x = max([x for (x, y) in self.offsets])
        max_y = max([y for (x, y) in self.offsets])
        printout = ""
        for i in range(max_x+1):
            for j in range(max_y+1):
                if (i,j) in self.offsets:
                    printout += "#"
                else:
                    printout += " "
            printout += "\n"
        print printout
    
    def flipH(self):
        self.offsets = sorted([(-x, y) for (x, y) in self.offsets])
        self._normalize()
        return self
    
    def flipV(self):
        self.offsets = sorted([(x, -y) for (x, y) in self.offsets])
        self._normalize()
        return self
    
    def rotCCW(self):
        self.offsets = sorted([(-y, x) for (x, y) in self.offsets])
        self._normalize()
        return self
    
    def rotCW(self):
        self.offsets = sorted([(y, -x) for (x, y) in self.offsets])
        self._normalize()
        return self
    
    def _normalize(self):
        min_x = min([x for (x, y) in self.offsets])
        min_y = min([y for (x, y) in self.offsets])
        self.offsets = [(x - min_x, y - min_y) for (x, y) in self.offsets]
    
    def __eq__(self, other):
        """check for match up to symmetries"""
        if len(self.offsets) != len(other.offsets):
            return False
        
        # make shallow copy of list
        memo = self.offsets[:]
        
        def match():
            # python list == list checks for all elements
            return self.offsets == other.offsets
        
        # check rotations
        for i in range(4):
            if match():
                self.offsets = memo
                return True
            self.rotCW()
        # flip and check mirrored rotations
        self.flipH()
        for i in range(4):
            if match():
                self.offsets = memo
                return True
            self.rotCW()
        # no match found; therefore not equal
        self.offsets = memo
        return False
        
    def __ne__(self, other):
        return not (self == other)
    
    @staticmethod
    def make_pieces():
        if Piece.FULL_SET is None:
        
            from Queue import Queue
            pieces = []
                
            def snap(piece, next_x, next_y):
                """copy the current piece. pair it with the next-offset in a tuple.
                this acts as a snapshot of the current state of BFS"""
                return (piece[:], (next_x, next_y))
        
            Q = Queue()
            Q.put(snap([], 0, 0))
        
            def bfs_extend(piece, fro, nsew):
                """extend from <fro> in the direction specified by <nsew>
                If such an extension is a collision, nothing happens."""
                x, y = fro
                if nsew == 0:
                    next = (x, y+1)
                elif nsew == 1:
                    next = (x, y-1)
                elif nsew == 2:
                    next = (x+1, y)
                elif nsew == 3:
                    next = (x-1, y)
                if next not in piece:
                    Q.put(snap(piece, *next))
        
            while not Q.empty():
                piece, bump = Q.get()
                piece.append(bump)
                # if it's valid and new, add it to the final list
                if len(piece) > 0 and len(piece) <= BLOCKS and Piece(piece) not in pieces:
                    pieces.append(Piece(piece))
                # only extend if doing so would not make pieces that are too large
                if len(piece) < BLOCKS:
                    # potential to extend from each existing block
                    for fro in piece:
                        # bfs extend in 4 directions
                        for nsew in range(4):
                            bfs_extend(piece, fro, nsew)
            Piece.FULL_SET = pieces
            return pieces
        else:
            return Piece.FULL_SET

class Player(object):
    
    def __init__(self, name):
        self.pieces = copy.deepcopy(Piece.FULL_SET)
        self.played = [] # pieces played already
        self.name = name

class Game(object):
    def __init__(self):
        Piece.make_pieces()
        self.players = [Player("temp") for i in range(4)]
        self.board_pieces = {}
        self.board_flat = [[0] * BOARD for i in range(BOARD)]
        self.turn = 0
    
    def is_valid_move(self, piece):
        return True # TODO
    
    def take_turn(self, piece):
        if self.is_valid_move(piece):
            self.turn += 1
            self.board_pieces[piece.pos] = piece
            # TODO flat, etc