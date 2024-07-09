from functools import partial
import torrent_parser as tp
from typing import Optional
import os.path
import math

from .types import File, TorrentSlice, FileSlice, FilePath, Path, PieceReaderFunc
from .physical import absPathToFile, read_piece, reader
from .verify import touchVerify, verifyPiece


class TorrentBase:
    def __init__(self, torrnt_path: FilePath):
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

        self.__torrent_info['info']['pieces'] = tuple(
            self.__torrent_info['info']['pieces'])

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
        return sum(map(lambda f: f.size, self.files))

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

    def pieceSize(self, pieceIndex: int) -> int:
        if pieceIndex not in self.pieceRange:
            return 0
        elif pieceIndex == self.numPieces-1:
            return self.totalSize-(self.pieceLength*(self.numPieces-1))
        else:
            return self.pieceLength

    def mapFile(self, file_index: int, file_offset: int = 0, size: Optional[int] = None) -> TorrentSlice:

        if file_index not in self.fileRange:
            raise IndexError('file index out of range')

        offset = file_offset + self.files[file_index].offset

        if not size:
            size = self.files[file_index].size - file_offset

        if (offset + size) > self.totalSize:
            raise ValueError('selection out of torrent range')

        piece_index = math.floor(offset/self.pieceLength)
        piece_offset = offset % self.pieceLength
        first_size = min(size, self.pieceLength - piece_offset)
        jumps = math.ceil((size-first_size)/self.pieceLength)
        last_size = size - first_size - (jumps-1) * self.pieceLength

        return TorrentSlice(piece_index, piece_offset, first_size, jumps, last_size)

    def mapBlock(self, piece_index: int, piece_offset: int = 0, size: Optional[int] = None, dynamic_size: bool = True) -> tuple[FileSlice, ...]:
        if piece_index not in self.pieceRange:
            raise IndexError("piece index out of range")

        # TORRENT_ASSERT_PRECOND(num_files() > 0);
        # TORRENT_ASSERT_PRECOND(size >= 0);

        slices = list()

        # if (m_files.empty()) return ret;
        # TORRENT_ASSERT(max_file_offset / m_piece_length > static_cast<int>(piece));

        if not size:
            size = self.pieceSize(piece_index)

        # offset in the torrent
        global_offset = piece_index * self.pieceLength + piece_offset

        if not (global_offset <= self.totalSize - size):
            if not dynamic_size:
                raise ValueError("selection out of torrent range")
            else:
                size = self.totalSize - global_offset

        for file in self.files[::-1]:
            if file.offset <= global_offset:
                pointer_file_index = file.index
                break

        file_offset = global_offset - self.files[pointer_file_index].offset

        while (size > 0):
            pointer_file = self.files[pointer_file_index]

            # I don't understand why this condition is here
            # if (file_offset < std::int64_t(file_iter->size))
            file_size = min(pointer_file.size - file_offset, size)
            fs = FileSlice(pointer_file.index, file_offset, file_size)
            slices.append(fs)
            file_offset = 0
            size -= file_size
            if (size > 0):
                pointer_file_index = self.files[pointer_file_index+1].index

        return tuple(slices)


class Torrent(TorrentBase):
    __physical_path: Optional[FilePath] = None

    def setPhysicalPath(self, path: FilePath):
        self.__physical_path = Path(path)
        return self

    @property
    def physicalPath(self):
        if isinstance(self.__physical_path, Path):
            return self.__physical_path
        raise Exception('physical path required')

    def getFile(self, file_index: int):
        return self.files[file_index]

    def absPathToFile(self, file_index: int) -> Path:
        return partial(absPathToFile, self, self.physicalPath)(file_index)

    def touchVerify(self):
        return touchVerify(self.absPathToFile, self.numFiles)

    def readPiece(self, reader: PieceReaderFunc, piece_index: int):
        return read_piece(self, self.absPathToFile, reader, piece_index)

    def verifyPiece(self, reader: PieceReaderFunc, piece_index: int):
        return verifyPiece(self, self.absPathToFile, reader, piece_index)

    def reader(self):
        return reader(self.absPathToFile)
