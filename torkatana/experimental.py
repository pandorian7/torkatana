from pathlib import Path

from .torrent import Torrent
from .blocker import locatePieceInBlock
from .verify import verifyPieceByBytes
from .types import PieceState
from .physical import reader, writer

def blockReader(torrent: 'Torrent'):
    return reader(torrent.absPathToBlock)

def blockWriter(torrent: 'Torrent'):
    return writer(torrent.absPathToBlock)

def getBlockPieceRange(torrent: 'Torrent', block_index: int) -> range:
    if block_index not in torrent.blockRange:
        raise IndexError('index out of range')
    block_range_start = torrent.numPiecesInBlock*block_index
    block_range_end = min(block_range_start+torrent.numPiecesInBlock, torrent.numPieces)
    block_range = range(block_range_start, block_range_end)
    return block_range


def splitBlock(torrent: 'Torrent', block_index:int , block_writer):
    block_range = getBlockPieceRange(torrent, block_index)
    with torrent.reader() as reader:
        for i in block_range:
            piece = torrent.readPiece(reader, i)
            block, offset = locatePieceInBlock(torrent.pieceLength, torrent.numPiecesInBlock, i)
            block_path = torrent.absPathToBlock(block)
            block_path.touch(exist_ok=True)
            yield block_writer(block, offset, piece)

def verifyBlock(torrent: 'Torrent', block_index: int, block_reader):
    block_range = getBlockPieceRange(torrent, block_index)
    for i in block_range:
        block, offset = locatePieceInBlock(torrent.pieceLength, torrent.numPiecesInBlock, i)
        piece = block_reader(block, offset, torrent.pieceSize(i))
        state = verifyPieceByBytes(torrent, i, piece)
        if state != PieceState.OK:
            print(i, state)
        yield state


def mergeBlocks(torrent: 'Torrent', output_directory):
    def __read_piece_from_block(piece_index, offset, size, block_reader):
        block_index, block_offset = locatePieceInBlock(torrent.pieceLength, torrent.numPiecesInBlock, piece_index)
        data = block_reader(block_index, block_offset + offset, size)
        return data
    
    def __read_chunks(t_slice, block_reader):
        yield __read_piece_from_block(t_slice.first_index, t_slice.first_offset, t_slice.first_size, block_reader)

        for i in range(t_slice.first_index+1, t_slice.first_index+t_slice.jumps):
            yield __read_piece_from_block(i, 0, torrent.pieceLength, block_reader)

        yield __read_piece_from_block(t_slice.first_index+t_slice.jumps, 0, t_slice.last_size, block_reader)


    with blockReader(torrent) as block_reader:
        for file in torrent.files:
            torrent_slice = torrent.mapFile(file.index)
            file_path = Path(output_directory) / file.path
            file_path.parent.mkdir(exist_ok=True, parents=True)
            with open(file_path, 'wb') as file_out:
                for chunk in __read_chunks(torrent_slice, block_reader):
                    yield file_out.write(chunk)
