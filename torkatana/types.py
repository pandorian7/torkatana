from typing import Callable, NamedTuple
from os import PathLike
from pathlib import Path
from enum import Enum

FilePath = str | PathLike[str]

ReaderFunc = Callable[[int, int, int], bytes]
WriterFunc = Callable[[int, int, bytes], int]
ReaderWriterFunc = ReaderFunc | WriterFunc


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


class FileSlice(NamedTuple):
    file_index: int
    offset: int
    size: int


class PieceState(Enum):
    OK = 0
    CORRUPT = 1
    INCOMPLETE = 2
