import Tkinter
from game import BOARD

class TkPieceSprite(object):
    def __init__(self, piece, render):
        self.p = piece
        self.rendered_pos = self.p.pos
        self.r = render
        self._make_squares()

    def update(self, delta=0):
        size = self.r.block_size + self.r.spacing
        if self.p.pos != self.rendered_pos:
            px, py = self.p.pos
            for i in range(len(self.p.offsets)):
                ox, oy = self.p.offsets[i]
                s = self.squares[i]
                bb = self.r.grid_to_bbox(px+ox, py+oy, size)
                self.r.move(s, bb)

    def delete(self):
        for s in self.squares:
            self.r.delete_object(s)
    
    def _make_squares(self):
        rgb = Render.player_num_to_rgb(self.p.owner.id)
        fill = Render.rgb_to_hex(*rgb)
        size = self.r.block_size + self.r.spacing
        self.squares = []
        px, py = self.p.pos
        for ox, oy in self.p.offsets:
            self.squares.append(self.r.draw_grid_object((ox+px, oy+py), size, width=1, fill=fill))

class PlayerPaletteSprite(object):
    def __init__(self, player, render, nesw):
        self.p = player
        self.r = render
        self._make_palette_bbox(nesw)

    def _make_palette_bbox(self, dock):
        """store self.bbox as (x1, y1, x2, y2) of the box in which pieces will be drawn
        """
        m = self.r.margin
        b = self.r.spacing * (BOARD + 1) + self.r.block_size * BOARD
        if dock == 0: # north
            self.bbox = (m, 0, m+b, m)
        elif dock == 1: # east
            self.bbox = (m+b, m, 2*m+b, m+b)
        elif dock == 2: # south
            self.bbox = (m, m+b, m+b, 2*m+b)
        elif dock == 3: # west
            self.bbox = (0, m, m, m+b)

    def update(self, delta=0):
        pass

    def delete(self):
        pass

class Render(object):
    
    def __init__(self, game, block_size=20, spacing=4, margin=50):
        self.g = game
        
        # properties of the window
        self.window_size = block_size * BOARD + spacing*(BOARD+1) + 2*margin
        self.block_size = block_size
        self.spacing = spacing
        self.margin = margin
        
        # initialize TK
        self._master = Tkinter.Tk()
        self._master.title('Blokus')
        self._win = Tkinter.Canvas(self._master, width=self.window_size, height=self.window_size)
        self._win.pack()
        
        # initialize simple graphics
        self._layers = {}
        self._init_background()
        self.sprites = []

        # initialize keyboard controls
        self._create_controls()
        
        self._win.after(20, self.callback)
        self._win.mainloop()
    
    def callback(self):
        self.update()
        self._win.after(20, self.callback)
    
    def _init_background(self):
        self._win.create_rectangle(0, 0, self.window_size, self.window_size, fill='#555', width=0)
        for i in range(BOARD):
            for j in range(BOARD):
                self.draw_grid_object((i, j), self.block_size, fill='#888', width=0)

    def _create_controls(self):

        def take_turn(event):
            self.g.take_turn()
        def move_left(event):
            self.g.turn.nudge(( 0,-1))
        def move_right(event):
            self.g.turn.nudge(( 0, 1))
        def move_up(event):
            self.g.turn.nudge((-1, 0))
        def move_down(event):
            self.g.turn.nudge(( 1, 0))
        def cw(event):
            self.g.turn.rotCW()
        def ccw(event):
            self.g.turn.rotCCW()
        def next(event):
            self.sprites.pop().delete()
            self.g.turn.next_piece()
        def prev(event):
            self.sprites.pop().delete()
            self.g.turn.prev_piece()
        def flipH(event):
            self.g.turn.flipH()
        def flipV(event):
            self.g.turn.flipV()

        self._master.bind('<space>', take_turn)
        self._master.bind('<w>', move_up)
        self._master.bind('<a>', move_left)
        self._master.bind('<s>', move_down)
        self._master.bind('<d>', move_right)
        self._master.bind('<q>', ccw)
        self._master.bind('<e>', cw)
        self._master.bind('<f>', flipH)
        self._master.bind('<r>', flipV)
        self._master.bind('<Right>', next)
        self._master.bind('<Left>', prev)

    def update(self, delta=0):
        # make (new) sprites
        existing_pieces = [spr.p.hash for spr in self.sprites]
        if self.g.turn.piece().hash not in existing_pieces:
            self.sprites.append(TkPieceSprite(self.g.turn.piece(), self))
        # draw sprites
        for sprite in self.sprites:
            sprite.update(delta)
        self.update_layers()
    
    def grid_to_bbox(self, grid_r, grid_c, w):
        cx = self.margin + self.spacing + grid_c * (self.block_size + self.spacing) + self.block_size / 2.0
        cy = self.margin + self.spacing + grid_r * (self.block_size + self.spacing) + self.block_size / 2.0
        return (cx - w/2, cy - w/2, cx + w/2, cy + w/2)

    def make_tk_square(self, grid_r, grid_c, w, **kargs):
        x, y, _, _ = self.grid_to_bbox(grid_r, grid_c, w)
        return self._win.create_rectangle(x, y, w, w, **kargs)
    
    def move(self, obj_id, bbox):
        self._win.coords(obj_id, *bbox)
    
    def alter(self, obj_id, **kargs):
        self._win.itemconfig(obj_id, **kargs)
        
    def draw_grid_object(self, loc, w, type="square", layer=0, **kargs):
        layer_id = 'layer %d' % layer
        self._layers[layer_id] = None
        tags = kargs.get("tags", [])
        tags.append(layer_id)
        kargs["tags"] = tags
        x, y, rx, ry = self.grid_to_bbox(loc[0], loc[1], w)
        if type == "square":
            item = self._win.create_rectangle(
                x, y, rx, ry,
                **kargs)
        elif type == "circle":
            item = self._win.create_oval(
                x, y, rx, ry,
                **kargs)
        return item

    def update_layers(self):
        for layer in self._layers:
            self._win.tag_raise(layer)

    def delete_object(self, obj_id):
        self._win.delete(obj_id)

    @staticmethod
    def rgb_to_hex(r, g, b, normalized=True):
        if normalized:
            r = int(r * 255.)
            g = int(g * 255.)
            b = int(b * 255.)
        return '#%02x%02x%02x' % (r, g, b)

    @staticmethod
    def player_num_to_rgb(num):
        color_lookup = {
            0: (1., 0., 0.),
            1: (0., 1., 0.),
            2: (0., 0., 1.),
            3: (1., 1., 0.)
        }
        return color_lookup.get(num, (0., 0., 0.))