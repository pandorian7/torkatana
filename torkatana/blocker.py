from typing import Callable
import re
import math


from torkatana.types import Path


def getNDigits(n_blocks: int):
    return max(math.ceil(math.log10(n_blocks)), 1)


def getNBlocks(total_size: int, block_size: int):
    return math.ceil(total_size/block_size)


# def getBlockNamerAndParser(pattern: str, n_digits: int) -> tuple[Callable[[int], str], Callable[[str], int]]:
#     placeholder = r"\d" * n_digits
#     index_range = range(10**n_digits)

#     def namer(index):
#         if index not in index_range:
#             raise ValueError("index out of valid range")
#         return pattern.format(index=format(index, f"0{n_digits}"))

#     def parser(name):
#         match = re.match(pattern.format(
#             index=f"(?P<index>{placeholder})"), name)
#         if not match:
#             raise ValueError("string does not parse into a valid index")
#         intstr = match.group('index')
#         return int(intstr)

#     return namer, parser
def getBlockNamerAndParser(pattern: str) -> tuple[Callable[[int], str], Callable[[str], int]]:

    def namer(index):
        return pattern.format(index=str(index))

    def parser(name):
        match = re.match(pattern.format(
            index=r"(?P<index>\d*)"), name)
        if not match:
            raise ValueError("string does not parse into a valid index")
        intstr = match.group('index')
        return int(intstr)

    return namer, parser


def absPathToBlock(blocks_path: Path, block_namer:  Callable[[int], str], block_index: int):
    return blocks_path / block_namer(block_index)


def MB(n_mb: int) -> int:
    return n_mb * 1024 * 1024


def touchBlocks(get_abs_path: Callable[[int], Path], block_range: range, create_dir=False):
    for i in block_range:
        abs_path = get_abs_path(i)
        if create_dir:
            abs_path.parent.mkdir(parents=True, exist_ok=True)
        abs_path.touch(exist_ok=True)


def locatePieceInBlock(piece_length: int, n_pieces_in_block: int, piece_index: int):
    block_index = math.floor(piece_index/n_pieces_in_block)
    offset_in_block = (piece_index % n_pieces_in_block) * piece_length
    return block_index, offset_in_block
