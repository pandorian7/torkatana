from .types import FilePath, Path, PieceReaderFunc, BufferedReader

from typing import TYPE_CHECKING, Callable, Optional
from contextlib import contextmanager

if TYPE_CHECKING:
    from .torrent import TorrentBase


def absPathToFile(torrent: 'TorrentBase', torrent_path: FilePath, file_index: int):
    return Path(torrent_path) / torrent.files[file_index].path


def read_piece(torrent: 'TorrentBase',
               get_abs_path: Callable[[int], Path],
               reader: PieceReaderFunc,
               index: int) -> bytes:
    piece = bytes()
    f_slices = torrent.mapBlock(index)
    for slice in f_slices:
        f_path = get_abs_path(slice.file_index)
        if not f_path.exists():
            continue
        piece += reader(slice.file_index, slice.offset, slice.size)
    return piece


@contextmanager
def reader(get_abs_path: Callable[[int], Path]):

    o_file: Optional[BufferedReader] = None
    o_file_index = -1
    in_context = True

    def read(file_index: int, file_offset: int, amount: int) -> bytes:
        nonlocal in_context, o_file, o_file_index
        # o = open
        if not in_context:
            raise Exception('use with context manager')

        if isinstance(o_file, BufferedReader):
            if o_file_index != file_index:
                o_file.close()
                o_file = None

        if not isinstance(o_file, BufferedReader):
            o_file = open(get_abs_path(file_index), 'rb')
            o_file_index = file_index

        if (o_file.tell() != file_offset):
            o_file.seek(file_offset)

        return o_file.read(amount)

    try:
        yield read
    finally:
        if isinstance(o_file, BufferedReader):
            o_file.close()
        o_file = None
        in_context = False
