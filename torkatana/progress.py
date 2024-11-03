from tqdm import tqdm

from .torrent import Torrent
from .types import PieceState

from .experimental import blockReader, verifyBlocks, mergeBlocks

def verify_progress(torrent: 'Torrent', fail_on_error=False, /, **tqdm_kwargs):
    faluty_pieces = list()
    with torrent.reader() as reader:
        for index, state in tqdm(enumerate(torrent.verify(reader)), desc="Verifying", total=torrent.numPieces, unit="pcs", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{remaining}]", **tqdm_kwargs):
            if state != PieceState.OK:
                faluty_pieces.append((index, state))
                if fail_on_error:
                    break
        if len(faluty_pieces) == 0:
            print('All OK!')
        for i, state in faluty_pieces:
            print(f"piece {i} has state {state}")

def verify_blocks_progress(torrent: 'Torrent', /, **tqdm_kwargs):
    with blockReader(torrent) as block_reader:
        for i, state in tqdm(enumerate(verifyBlocks(torrent, block_reader)), desc="Verifying Blocks", total=torrent.numPieces, unit="pcs", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{remaining}]", **tqdm_kwargs):
            if state != PieceState.OK:
                print(i, state)


def merge_blocks_progress(torrent: 'Torrent', output_dir,/, **tqdm_kwqrgs):
    with tqdm(total=torrent.totalSize, unit='B', unit_scale=True,unit_divisor=1024, desc="Merging", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{remaining}]", **tqdm_kwqrgs) as progress_bar:
        for written in mergeBlocks(torrent, output_dir):
            progress_bar.update(written)