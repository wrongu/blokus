from game import Piece, Game
from render import Render

if __name__ == '__main__':
    g = Game()
    
    p = Piece([(0,0), (0,1), (1,0)])
    p.pos = (8, 12)
    
    g.take_turn(p)

    r = Render(g)