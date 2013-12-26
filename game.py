import copy

BOARD = 20
BLOCKS = 5

def around(loc, adj=[(0,-1), (1, 0), (0, 1), (-1, 0)]):
    arnd = []
    x, y = loc
    for offx, offy in adj:
        nx = x + offx
        ny = y + offy
        if nx >= 0 and nx < BOARD and ny >= 0 and ny < BOARD:
            arnd.append((nx, ny))
    return arnd

def diag(loc):
    return around(loc, adj=[(-1,-1), (1, -1), (1, 1), (-1, 1)])

class Piece(object):
    
    FULL_SET = None
    _NEXT_ID = 0
    
    def __init__(self, off):
        self.offsets = sorted(off)
        self._normalize()
        self.pos = (0,0)
        self.id = 0 # each shape has an id (0 through 20)
        self.owner = None # the player who owns this piece
    
    def set_owner(self, owner):
        self.owner = owner
        self.hash = self.id << 2 | self.owner.id

    def moveto(self, newpos):
        self.pos = newpos

    def occupied(self):
        return [(ox + self.pos[0], oy + self.pos[1]) for (ox,oy) in self.offsets]
    
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
        self.offsets = sorted([(r, -c) for (r, c) in self.offsets])
        self._normalize()
        return self
    
    def flipV(self):
        self.offsets = sorted([(-r, c) for (r, c) in self.offsets])
        self._normalize()
        return self
    
    def rotCCW(self):
        self.offsets = sorted([(-c, r) for (r, c) in self.offsets])
        self._normalize()
        return self
    
    def rotCW(self):
        self.offsets = sorted([(c, -r) for (r, c) in self.offsets])
        self._normalize()
        return self
    
    def _normalize(self):
        min_r = min([r for (r, y) in self.offsets])
        min_c = min([c for (r, c) in self.offsets])
        self.offsets = [(r - min_r, c - min_c) for (r, c) in self.offsets]

    def sym(self, other):
        """check for match up to symmetries"""
        if len(self.offsets) != len(other.offsets):
            return False
        
        # make shallow copy of list
        memo = self.offsets[:]
        
        def match():
            # conveniently, python's "list == list" checks all corresponding elements
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

            def exists_as_sym(piece):
                for p in pieces:
                    if p.sym(Piece(piece)):
                        return True
                return False
        
            while not Q.empty():
                piece, bump = Q.get()
                piece.append(bump)
                # if it's valid and new, add it to the final list
                if len(piece) > 0 and len(piece) <= BLOCKS and not exists_as_sym(piece):
                    newpiece = Piece(piece)
                    newpiece.id = Piece._NEXT_ID
                    Piece._NEXT_ID += 1
                    pieces.append(newpiece)
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
    
    _NEXT_ID = 0

    def __init__(self, name):
        self.id = Player._NEXT_ID
        self.played = [] # pieces played already
        self.name = name
        Player._NEXT_ID += 1

        # set my pieces
        self.pieces = copy.deepcopy(Piece.FULL_SET)
        for p in self.pieces:
            p.set_owner(self)

class Turn(object):

    def __init__(self, num, player, game):
        self.n = num
        self.p = player
        self.g = game
        self.pi = 0 # piece index

    def piece(self):
        return self.p.pieces[self.pi]

    def player(self):
        return self.p

    def next_piece(self):
        self.pi = (self.pi + 1) % len(self.p.pieces)

    def prev_piece(self):
        self.pi = (self.pi + len(self.p.pieces) - 1) % len(self.p.pieces)

    def nudge(self, offset):
        ox, oy = offset
        memo = self.piece().pos
        self.piece().pos = (memo[0] + ox, memo[1] + oy)
        if not self._check_piece_bounds():
            self.piece().pos = memo

    def rotCW(self):
        self.piece().rotCW()
        if not self._check_piece_bounds():
            self.piece().rotCCW()

    def rotCCW(self):
        self.piece().rotCCW()
        if not self._check_piece_bounds():
            self.piece().rotCW()

    def flipH(self):
        self.piece().flipH()
        if not self._check_piece_bounds():
            self.piece().flipH()

    def flipV(self):
        self.piece().flipV()
        if not self._check_piece_bounds():
            self.piece().flipV()

    def _check_piece_bounds(self):
        for px, py in self.piece().occupied():
            if px < 0 or px >= BOARD or py < 0 or py >= BOARD:
                return False
        return True

    def is_valid(self):
        px, py = self.piece().pos
        occupied = self.piece().occupied()
        has_corner = False
        corners = self.g.corners[self.p.id]
        open_squares = self.g.open_squares[self.p.id]
        for (x, y) in occupied:
            # record whether it has a corner
            if corners[x][y]:
                has_corner = True
            # if any occupied block is invalid, the turn is invalid and we can return
            if not open_squares[x][y]:
                return False
        return has_corner

class Game(object):
    def __init__(self):
        Piece.make_pieces()
        self.players = [Player("temp") for i in range(4)]
        self.turn_count = 0

        # make grid(s) of valid spaces for each player to move
        self.init_grids()

        # start with a new turn
        self.turn = Turn(self.turn_count, self.players[0], self)

    @staticmethod
    def _grid(val=None):
        return [[val] * BOARD for i in range(BOARD)]

    def init_grids(self):
        self.open_squares = [Game._grid(True) for i in range(4)] # grid for each player
        self.corners = [Game._grid(False) for i in range(4)] # grid for each player
        # set starting corners for each player
        self.corners[0][0]      [0]       = True
        self.corners[1][BOARD-1][0]       = True
        self.corners[2][BOARD-1][BOARD-1] = True
        self.corners[3][0]      [BOARD-1] = True

    def _advance_turn(self):
        self.turn_count += 1
        self.turn = Turn(self.turn_count, self.players[self.turn_count % 4], self)

    def take_turn(self):
        if self.turn.is_valid():
            pid = self.turn.player().id
            # first, update grids for the current player
            corners = self.corners[pid]
            my_open_squares = self.open_squares[pid]
            # for each new occupied space...
            for (ox, oy) in self.turn.piece().occupied():
                # mark the square as closed (for all players!)
                for pi in range(4):
                    self.open_squares[pi][ox][oy] = False
                # mark diagonals as corners
                for dx, dy in diag((ox, oy)):
                    self.corners[dx][dy] = True
                # mark adjacents as closed (edges can't touch!)
                for ax, ay in around((ox, oy)):
                    my_open_squares[ax][ay] = False
            self._advance_turn()
