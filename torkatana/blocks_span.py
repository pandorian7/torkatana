from .torrent_info import TorrentInfo
from .priority_span import PrioritySpan

class BlockSpan:
    def __init__(self, torrent: TorrentInfo):
        self.__torrent = torrent
        self.__span = []
        self.__piece_map = {index : None for index in torrent.pieceRange}

        '''This Property will be used when calling AddPieceToTail to automatically add blocks
        and when calling gropuByNPieces if n_blocks is not provided'''
        self.PiecesPerBlock = None

    @classmethod
    def fromPrioritySpan(cls, priority_span: PrioritySpan):
        """Create a BlockSpan from a Priority Span 0 Priority 
        will be skippled and all others will be considered"""

        bs = cls(priority_span.torrent)
        bs.addBlock()
        for i, priority in enumerate(priority_span.span):
            if priority:
                bs.addPieceToBlock(-1, i)
        return bs

    @classmethod
    def fromArray(cls, torrent: TorrentInfo, span: list[list[int]]):
        bs = cls(torrent)
        for block in span:
            bs.addBlock()
            for piece in block:
                bs.addPieceToBlock(-1, piece)
        return bs

    @property
    def torrent(self) -> TorrentInfo:
        return self.__torrent
    
    def addBlock(self):
        self.__span.append(list())
        return len(self.__span) - 1
    
    def toArray(self):
        return tuple(map(tuple, self.__span))  
    
    def addPieceToBlock(self, block_index: int, piece_index: int):
        if block_index < 0:
            block_index = len(self.__span) + block_index
        if piece_index not in self.torrent.pieceRange:
            raise IndexError('piece index out of range')
        if not self.__piece_map[piece_index]:
            self.__span[block_index].append(piece_index)
            self.__piece_map[piece_index] = (block_index, len(self.__span[block_index]) - 1)
        return self.__piece_map[piece_index]
    
    def pieceAt(self, piece_index: int):
        return self.__piece_map[piece_index]
    
    def gropuByNPieces(self, n_pieces: int|None = None) -> 'BlockSpan':
        if not n_pieces:
            n_pieces = self.PiecesPerBlock
        new_bs = BlockSpan(self.torrent)
        new_bs.addBlock()
        for block in self.__span:
            for piece in block:
                if len(new_bs.__span[-1]) == n_pieces:
                    new_bs.addBlock()
                new_bs.addPieceToBlock(-1, piece)
        
        self.__piece_map = new_bs.__piece_map
        self.__span = new_bs.__span
    
    def addPieceToTail(self, piece_index: int):
        if not self.PiecesPerBlock:
            raise AttributeError('PiecesPerBlock not set')
        if len(self.__span[-1]) >= self.PiecesPerBlock:
            self.addBlock()
        self.addPieceToBlock(-1, piece_index)