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
    
    def width(self):
        return max([c for (r, c) in self.offsets])

    def height(self):
        return max([r for (r, c) in self.offsets])

    def OB(self):
        """returns tuple of (out_bounds, out_bounds_w, out_bounds_h)"""
        out_bounds_w = False
        out_bounds_h = False
        if self.pos[0] < 0 or self.pos[0] + self.height() >= BOARD:
            out_bounds_h = True
        if self.pos[1] < 0 or self.pos[1] + self.width() >= BOARD:
            out_bounds_w = True
        return (out_bounds_h or out_bounds_w, out_bounds_w, out_bounds_h)

    def set_owner(self, owner):
        self.owner = owner
        self.hash = self.id << 2 | self.owner.id

    def moveto(self, *args):
        if len(args) == 2:
            self.pos = (args[0], args[1])
        elif len(args) == 1:
            self.pos = args[0]
        else:
            print "pos has %d components...?" % len(args)

    def occupied(self):
        return [(offr + self.pos[0], offc + self.pos[1]) for (offr,offc) in self.offsets]
    
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

    def __init__(self, num, player, game, pos=None):
        self.n = num
        self.p = player
        self.g = game
        self.pi = 0 # piece index
        self.active_pos = pos if pos else (0, 0)

    def piece(self):
        return self.p.pieces[self.pi]

    def player(self):
        return self.p

    def next_piece(self):
        self.pi = (self.pi + 1) % len(self.p.pieces)

    def prev_piece(self):
        self.pi = (self.pi + len(self.p.pieces) - 1) % len(self.p.pieces)

    def nudge(self, offset):
        offr, offc = offset
        memo = self.piece().pos
        self.piece().moveto(memo[0] + offr, memo[1] + offc)
        if not self._check_piece_bounds():
            print "out of bounds"
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
        for pr, pc in self.piece().occupied():
            if pr < 0 or pr >= BOARD or pc < 0 or pc >= BOARD:
                return False
        return True

    def is_valid(self):
        pr, pc = self.piece().pos
        occupied = self.piece().occupied()
        has_corner = False
        corners = self.g.corners[self.p.id]
        open_squares = self.g.open_squares[self.p.id]
        for loc in occupied:
            # record whether it has a corner
            if loc in corners:
                has_corner = True
            # if any occupied block is invalid, the turn is invalid and we can return
            if loc not in open_squares:
                return False
        return has_corner

class Game(object):
    def __init__(self):
        Piece.make_pieces()
        self.players = [Player("temp") for i in range(4)]
        self.turn_count = 0

        # make grid(s) of valid spaces for each player to move
        self._init_grids()
        self._init_piece_locations()

        # start with a new turn
        self.turn = Turn(self.turn_count, self.players[0], self)

    @staticmethod
    def _grid(val=None):
        return [[val] * BOARD for i in range(BOARD)]

    @staticmethod
    def _all_spaces():
        import itertools
        return itertools.product(range(BOARD), range(BOARD))

    @staticmethod
    def _start_position(pid):
        if pid == 0:
            return (0,0)
        elif pid == 1:
            return (BOARD-1, 0)
        elif pid == 2:
            return (BOARD-1, BOARD-1)
        elif pid == 3:
            return (0, BOARD-1)
        else:
            print "-- no start position for player %d --" % pid

    def _init_grids(self):
        # using set of tuples instead of 2D array - makes lookup easier
        self.open_squares = [set(Game._all_spaces()) for i in range(4)]
        self.corners = [set([Game._start_position(i)]) for i in range(4)]

    def _init_piece_locations(self):
        """move pieces into a reasonable starting position"""
        for i in range(1,4):
            startcorner = list(self.corners[i])[0]
            for pi in self.players[i].pieces:
                pi.moveto(startcorner)
                out, out_w, out_h = pi.OB()
                if out_h:
                    pi.moveto(pi.pos[0] - pi.height(), pi.pos[1])
                if out_w:
                    pi.moveto(pi.pos[0], pi.pos[1] - pi.width())

    def _advance_turn(self):
        self.turn_count += 1
        self.turn = Turn(self.turn_count, self.players[self.turn_count % 4], self)

    def take_turn(self):
        if self.turn.is_valid():
            pid = self.turn.player().id
            # first, update grids for the current player
            my_corners = self.corners[pid]
            my_open_squares = self.open_squares[pid]
            occupied = set(self.turn.piece().occupied())
            # mark the square as closed (for all players!)
            for pi in range(4):
                self.open_squares[pi] -= occupied
            # for each new occupied space, update adjacent spaces
            for o in occupied:
                # mark diagonals as corners
                my_corners |= set(diag(o))
                # mark adjacents as closed (edges can't touch!)
                my_open_squares -= set(around(o))
            #TODO - broken
            #self.players[pid].pieces.remove(self.turn.piece())
            #self.players[pid].played.append(self.turn.piece())
            self._advance_turn()
