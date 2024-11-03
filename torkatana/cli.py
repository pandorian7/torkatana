from . import progress
from . import Torrent

def verify_torrent(args):
    torrent = Torrent(args.torrent)
    torrent.setPhysicalPath(args.physical)
    progress.verify_progress(torrent, args.fail)


def verify_blocks(args):
    torrent = Torrent(args.torrent)
    torrent.setBlocksPath(args.blocks)
    torrent.setBlockPattern(args.pattern)

    n_pieces_in_block = int(args.block_size/torrent.pieceLength)


    torrent.setNPiecesInBlock(n_pieces_in_block)
    progress.verify_blocks_progress(torrent)

def merge_blocks(args):
    torrent = Torrent(args.torrent)
    torrent.setBlocksPath(args.blocks)
    torrent.setBlockPattern(args.pattern)

    n_pieces_in_block = int(args.block_size/torrent.pieceLength)


    torrent.setNPiecesInBlock(n_pieces_in_block)
    progress.merge_blocks_progress(torrent, args.output)

