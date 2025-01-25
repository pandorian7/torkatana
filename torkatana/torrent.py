from functools import partial
import torrent_parser as tp
from typing import Callable, Optional
import os.path
import math

from torkatana.blocker import getBlockNamerAndParser, getNBlocks, getNDigits

from .types import File, TorrentSlice, FileSlice, FilePath, Path, ReaderFunc
from .physical import absPathToFile, read_piece, reader, writer
from .verify import touchVerify, verifyPiece, verifyTorrent


# class Torrent(TorrentBase):
#     __physical_path: Optional[FilePath] = None
#     __blocks_path: Optional[FilePath] = None
#     __block_pattern: Optional[str] = None
#     __num_pieces_in_block: Optional[int] = None
#     __namer: Optional[Callable[[int], str]] = None
#     __parser: Optional[Callable[[str], int]] = None


#     def setNPiecesInBlock(self, n: int):
#         self.__num_pieces_in_block = n
#         return self


#     @property
#     def numPiecesInBlock(self):
#         self.__namer = self.__parser = None
#         if isinstance(self.__num_pieces_in_block, int):
#             return self.__num_pieces_in_block
#         raise Exception('N pieces in block required')

#     @property
#     def blockSize(self):
#         return self.numPiecesInBlock*self.pieceLength

#     @property
#     def numBlocks(self):
#         return getNBlocks(self.totalSize, self.blockSize)

#     @property
#     def blockRange(self):
#         return range(self.numBlocks)


#     def readPiece(self, reader: ReaderFunc, piece_index: int):
#         return read_piece(self, self.absPathToFile, reader, piece_index)

#     def verifyPiece(self, reader: ReaderFunc, piece_index: int):
#         return verifyPiece(self, self.absPathToFile, reader, piece_index)
from .torrent_info import TorrentInfo
from .torrent_physical import TorrentPhysical
from .blocks_span import BlockSpan
from .torrent_blocks import TorrentBlocks

class TorKatana:
    
    def __init__(self, torrent_path: FilePath, physical_path: FilePath, blocks_path: FilePath, block_pattern: Optional[str] = None):
        """if block_pattern is not provided it will be set to 'block_{index}'"""
        if not block_pattern:
            block_pattern = 'block_{index}'
        self.__torrent = TorrentInfo(torrent_path)
        self.__physical = TorrentPhysical(self.torrent, physical_path)
        self.__blocks = TorrentBlocks(blocks_path, block_pattern)


    @property
    def torrent(self) -> Optional[TorrentInfo]:
        return self.__torrent

    @property
    def physical(self) -> Optional[TorrentPhysical]:
        return self.__physical

    @property
    def blockSpan(self) -> Optional[BlockSpan]:
        return self.__block_span

    @blockSpan.setter
    def blockSpan(self, value: BlockSpan):
        self.__block_span = value

    @property
    def blocks(self) -> Optional[TorrentBlocks]:
        return self.__blocks

