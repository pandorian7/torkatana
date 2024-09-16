from .types import FilePath, Path, ReaderFunc

from typing import TYPE_CHECKING, Callable, Optional, Literal, BinaryIO
from contextlib import contextmanager

if TYPE_CHECKING:
    from .torrent import TorrentBase


def absPathToFile(torrent: 'TorrentBase', torrent_path: FilePath, file_index: int):
    return Path(torrent_path) / torrent.files[file_index].path


def read_piece(torrent: 'TorrentBase',
               get_abs_path: Callable[[int], Path],
               reader: ReaderFunc,
               index: int) -> bytes:
    piece = bytes()
    f_slices = torrent.mapBlock(index)
    for slice in f_slices:
        f_path = get_abs_path(slice.file_index)
        if not f_path.exists():
            continue
        piece += reader(slice.file_index, slice.offset, slice.size)
    return piece


def __reader_or_writer_wrapper(get_abs_path: Callable[[int], Path], mode: Literal['read', 'write']):
    o_file: Optional[BinaryIO] = None
    o_file_index = -1
    in_context = True

    def read_or_write(file_index: int, file_offset: int, amount_or_data: int | bytes) -> int | bytes:
        nonlocal in_context, o_file, o_file_index
        # o = open

        open_mode: Literal['rb', 'r+b']

        if mode == 'read':
            open_mode = 'rb'
        else:
            open_mode = 'r+b'

        if not in_context:
            raise Exception('use with context manager')

        if isinstance(o_file, BinaryIO):
            if o_file_index != file_index:
                o_file.close()
                o_file = None

        if not isinstance(o_file, BinaryIO):
            o_file = open(get_abs_path(file_index), open_mode)
            o_file_index = file_index

        if (o_file.tell() != file_offset):
            o_file.seek(file_offset)

        ret = None
        if mode == 'read':
            if isinstance(amount_or_data, int):
                ret = o_file.read(amount_or_data)
        else:
            if isinstance(amount_or_data, bytes):
                ret = o_file.write(amount_or_data)

        assert ret is not None

        return ret

    def close_file():
        nonlocal o_file, in_context
        if isinstance(o_file, BinaryIO):
            o_file.close()
        o_file = None
        in_context = False

    return read_or_write, close_file


@contextmanager
def reader(get_abs_path: Callable[[int], Path]):
    __reader, closer = __reader_or_writer_wrapper(get_abs_path, 'read')

    def _reader(file_index: int, file_offset: int, amount: int) -> bytes:
        ret = __reader(file_index, file_offset, amount)
        assert isinstance(ret, bytes)
        return ret

    try:
        yield _reader
    finally:
        closer()


@contextmanager
def writer(get_abs_path: Callable[[int], Path]):
    __writer, closer = __reader_or_writer_wrapper(get_abs_path, 'write')

    def _writer(file_index: int, file_offset: int, data: bytes) -> int:
        ret = __writer(file_index, file_offset, data)
        assert isinstance(ret, int)
        return ret

    try:
        yield _writer
    finally:
        closer()
