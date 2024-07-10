from typing import TYPE_CHECKING, Callable
from hashlib import sha1

from .types import PieceReaderFunc, Path, PieceState
from .physical import read_piece

if TYPE_CHECKING:
    from .torrent import TorrentBase


def verifyPiece(torrent: 'TorrentBase', get_abs_path: Callable[[int], Path], reader: PieceReaderFunc, piece_index: int) -> PieceState:
    data = read_piece(torrent, get_abs_path, reader, piece_index)

    hash = sha1(data)

    state = torrent.hashes[piece_index] == hash.hexdigest()

    if state:
        return PieceState.OK
    if len(data) == torrent.pieceSize(piece_index):
        return PieceState.CORRUPT
    return PieceState.INCOMPLETE


def verityTorrent(torrent: 'TorrentBase', get_abs_path: Callable[[int], Path], reader: PieceReaderFunc):
    for pi in torrent.pieceRange:
        yield verifyPiece(torrent, get_abs_path, reader, pi)


def touchVerify(get_abs_path: Callable[[int], Path], num_files: int) -> tuple[int, ...]:
    missing_files = list()
    for file_index in range(num_files):
        abs_path = get_abs_path(file_index)
        if not abs_path.exists():
            missing_files.append(file_index)

    return tuple(missing_files)