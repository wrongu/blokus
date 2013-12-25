import Tkinter
from game import BOARD

class TkPieceSprite(object):
    def __init__(self, piece, renderer):
        self.p = piece
        self.rendered_pos = self.p.pos
        self.renderer = renderer
        self._make_squares()

    def update(self, delta=0):
        size = self.renderer.block_size + self.renderer.spacing
        if self.p.pos != self.rendered_pos:
            px, py = self.p.pos
            for i in range(self.p.offsets):
                ox, oy = self.p.offsets[i]
                s = self.squares[i]
                x, y, _, _ = self.renderer.grid_to_bbox(px+ox, py+oy, size)
                self.renderer.move(s, (x, y))
    
    def _make_squares(self):
        size = self.renderer.block_size + self.renderer.spacing
        self.squares = []
        px, py = self.p.pos
        for ox, oy in self.p.offsets:
            self.squares.append(self.renderer.draw_grid_object((ox+px, oy+py), size, width=0, fill='#F00'))
    
    def __eq__(self, other):
        return self.p == other.p and self.p.pos == other.p.pos
    
    def __ne__(self, other):
        return not (self == other)

class Render(object):
    
    def __init__(self, game, block_size=20, spacing=3):
        self.g = game
        
        # properties of the window
        self.window_size = block_size * BOARD + spacing*(BOARD+1)
        self.block_size = block_size
        self.spacing = spacing
        
        # initialize TK
        self._master = Tkinter.Tk()
        self._master.title('Blokus')
        self._win = Tkinter.Canvas(self._master, width=self.window_size, height=self.window_size)
        self._win.pack()
        
        # initialize simple graphics
        self._layers = {}
        self._init_background()
        self.sprites = []
        
        self._win.after(100, self.callback)
        self._win.mainloop()
    
    def callback(self):
        self.update()
        self._win.after(100, self.callback)
    
    def _init_background(self):
        self._win.create_rectangle(0, 0, self.window_size, self.window_size, fill='#555', width=0)
        for i in range(BOARD):
            for j in range(BOARD):
                self.draw_grid_object((i, j), self.block_size, fill='#888', width=0)

    def update(self, delta=0):
        for pos, piece in self.g.board_pieces.iteritems():
            if TkPieceSprite(piece, self) not in self.sprites:
                self.sprites.append(TkPieceSprite(piece, self))
        for sprite in self.sprites:
            sprite.update(delta)
        self.update_layers()
    
    def grid_to_bbox(self, grid_r, grid_c, w):
        cx = self.spacing + grid_c * (self.block_size + self.spacing) + self.block_size / 2.0
        cy = self.spacing + grid_r * (self.block_size + self.spacing) + self.block_size / 2.0
        return (cx - w/2, cy - w/2, cx + w/2, cy + w/2)

    def make_tk_square(self, grid_r, grid_c, w, **kargs):
        x, y, _, _ = self.grid_to_bbox(grid_r, grid_c, w)
        return self._win.create_rectangle(x, y, w, w, **kargs)
    
    def move(self, obj_id, newpos):
        self._win.coords(obj_id, newpos)
    
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
