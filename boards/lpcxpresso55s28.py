from mcutool.board import Board as BaseBoard

class Board(BaseBoard):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def programming(self, filepath, **kwargs):
        return super().programming(filepath, **kwargs)
