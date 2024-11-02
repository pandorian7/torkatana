from tqdm import tqdm

from .torrent import Torrent
from .types import PieceState

def verify(torrent: 'Torrent', fail_on_error=False, /, **tqdm_kwargs):
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