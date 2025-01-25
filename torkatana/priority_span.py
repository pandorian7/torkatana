from .torrent_info import TorrentInfo
from .types import Priority

class PrioritySpan:
    def __init__(self, torrent: TorrentInfo, default_priority: Priority = 7):
        self.__torrent = torrent
        self.__span = [default_priority] * torrent.numPieces
    
    @property
    def torrent(self) -> TorrentInfo:
        return self.__torrent
    
    @property
    def span(self) -> tuple[int, ...]:
        return tuple(self.__span)

    @classmethod
    def Paused(cls, torrent: TorrentInfo):
        """All the pirces has the Priority 0"""
        return cls(torrent, 0)
    
    def setFilePriority(self, file_index: int, priority: Priority):
        for i in self.torrent.filePieceRange(file_index):
            self.__span[i] = priority

    def addFile(self, file_index: int):
        self.setFilePriority(file_index, 7)

    def excludeFile(self, file_index: int):
        self.setFilePriority(file_index, 0)

    def setPiecePriority(self, piece_index: int, priority: Priority):
        self.__span[piece_index] = priority

    def setPriceRangePriority(self, start: int, end: int, priority: Priority):
        for i in range(start, end):
            self.setPiecePriority(i, priority)

    