from typing import NamedTuple
import torrent_parser as tp
import typing
import math
import os



class File(NamedTuple):
    index: int
    path: str
    size: int
    offset: int


class TorrentSlice(NamedTuple):
    first_index: int
    first_offset: int
    first_size: int
    jumps: int
    last_size: int


class Torrent:
    def __init__(self, torrnt_path: str | os.PathLike):
        self.__torrent_path = torrnt_path
        self.__torrent_info = tp.parse_torrent_file(torrnt_path)
        
        files = list()
        pos_pointer = 0
        for file_index, file in enumerate(self.__torrent_info['info']['files']):
            size = file['length']
            path = os.path.join(*file['path'])
            files.append(File(file_index, path, size, pos_pointer))
            pos_pointer += size
        self.__files = tuple(files)

        self.__torrent_info['info']['pieces'] = tuple(self.__torrent_info['info']['pieces'])

    @property
    def name(self) -> str:
        return self.__torrent_info['info']['name']
    
    @property
    def path(self):
        return self.__torrent_path
    
    @property
    def numFiles(self) -> int:
        return len(self.files)
    
    @property
    def pieceLength(self) -> int:
        return self.__torrent_info['info']['piece length']

    @property
    def files(self) -> tuple[File, ...]:
        return self.__files
    
    @property
    def totalSize(self) -> int:
        return sum(map(lambda f:f.size, self.files))
    
    @property
    def numPieces(self) -> int:
        return math.ceil(self.totalSize/self.pieceLength)
    
    @property
    def pieceRange(self) -> range:
        return range(self.numPieces)
    
    @property
    def fileRange(self) -> range:
        return range(self.numFiles)
    
    @property
    def hashes(self) -> tuple[str, ...]:
        return self.__torrent_info['info']['pieces']
    
    def mapFile(self, file_index:int, file_offset:int=0, size:typing.Optional[int]=None) -> TorrentSlice:

        if file_index not in self.fileRange:
            raise IndexError('file index out of range')
        
        offset = file_offset + self.files[file_index].offset

        if not size: size = self.files[file_index].size - file_offset

        if (offset + size) > self.totalSize:
            raise ValueError('selection out of torrent range')
        
        piece_index = math.floor(offset/self.pieceLength)
        piece_offset = offset % self.pieceLength
        first_size = min(size, self.pieceLength - piece_offset)
        n_pieces = math.ceil((size - (piece_offset))/self.pieceLength) + 1
        jumps = n_pieces - 1
        last_size = size - min(size, self.pieceLength - piece_offset) - jumps * self.pieceLength

        return TorrentSlice(piece_index, piece_offset, first_size, jumps, last_size)

