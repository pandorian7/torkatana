from .types import TorrentSlice

from typing import Literal, overload


class PieceMap:
    def __init__(self, numPieces: int):
        self.__num_pieces = numPieces
        self.__piece_map = [0] * numPieces

    def getMap(self) -> tuple[int, ...]:
        return tuple(self.__piece_map)

    @property
    def pieceRange(self) -> range:
        return range(0, self.__num_pieces)

    def updatePiece(self, pieceIndex: int, mode: Literal[1] | Literal[0]):
        if pieceIndex not in self.pieceRange:
            raise IndexError('piece index out of range')
        self.__piece_map[pieceIndex] = mode

    @overload
    def update(self, element: 'PieceMap'): ...

    @overload
    def update(self, element: TorrentSlice): ...

    def update(self, element):
        if isinstance(element, PieceMap):
            for i in self.pieceRange:
                if element.getMap()[i] == 1:
                    self.updatePiece(i, 1)
        elif isinstance(element, TorrentSlice):
            start = element.first_index
            last = start + element.jumps + 1
            for i in range(start, last):
                self.updatePiece(i, 1)
        else:
            raise TypeError('element type not supported')
        return self
