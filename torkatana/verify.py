from typing import TYPE_CHECKING, Callable
from hashlib import sha1

from .types import ReaderFunc, Path, PieceState
from .physical import read_piece

if TYPE_CHECKING:
    from .torrent import TorrentBase

def verifyPieceByBytes(torrent: 'TorrentBase', piece_index:int, piece_bytes:bytes):
    hash = sha1(piece_bytes)

    state = torrent.hashes[piece_index] == hash.hexdigest()

    if state:
        return PieceState.OK
    if len(piece_bytes) == torrent.pieceSize(piece_index):
        return PieceState.CORRUPT
    return PieceState.INCOMPLETE


def verifyPiece(torrent: 'TorrentBase', get_abs_path: Callable[[int], Path], reader: ReaderFunc, piece_index: int) -> PieceState:
    data = read_piece(torrent, get_abs_path, reader, piece_index)

    return verifyPieceByBytes(torrent, piece_index, data)

    # hash = sha1(data)

    # state = torrent.hashes[piece_index] == hash.hexdigest()

    # if state:
    #     return PieceState.OK
    # if len(data) == torrent.pieceSize(piece_index):
    #     return PieceState.CORRUPT
    # return PieceState.INCOMPLETE


def verifyTorrent(torrent: 'TorrentBase', get_abs_path: Callable[[int], Path], reader: ReaderFunc):
    for pi in torrent.pieceRange:
        yield verifyPiece(torrent, get_abs_path, reader, pi)


def touchVerify(get_abs_path: Callable[[int], Path], num_files: int) -> tuple[int, ...]:
    missing_files = list()
    for file_index in range(num_files):
        abs_path = get_abs_path(file_index)
        if not abs_path.exists():
            missing_files.append(file_index)

    return tuple(missing_files)
