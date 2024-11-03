from argparse import ArgumentParser
import argparse

from . import cli

# from chatGPT
def parse_size(size_str):
    """Parse a file size string with optional suffix (K, M, G, T) and return size in bytes."""
    suffixes = {'K': 1024, 'M': 1024**2, 'G': 1024**3, 'T': 1024**4}
    
    # Check if the last character is a recognized suffix
    if size_str[-1].upper() in suffixes:
        # Separate the numeric part and the suffix, then perform the multiplication
        try:
            number = float(size_str[:-1])  # The numeric part
            return int(number * suffixes[size_str[-1].upper()])
        except ValueError:
            raise argparse.ArgumentTypeError(f"Invalid size: '{size_str}'")
    else:
        # No suffix, assume it's in bytes
        try:
            return int(size_str)
        except ValueError:
            raise argparse.ArgumentTypeError(f"Invalid size: '{size_str}'")

parser = ArgumentParser(prog="torkatana", description="A CLI tool for managing torrents.", fromfile_prefix_chars='@')

parser.add_argument("torrent", help="The path to the torrent file.")

parser.add_argument("--physical", help="The path to the physical files.", default=None)

parser.add_argument("--blocks", help="The path to the blocks.", default=None)

parser.add_argument("--blocks-pattern", help="The pattern for the blocks.", default=None, dest="pattern")

parser.add_argument("--block-size", help="The size of the blocks.", type=parse_size, default=None)

subparsers = parser.add_subparsers(dest="command", required=True)


torrent_verify_parser = subparsers.add_parser("tverify", help="Verify the torrent.")
torrent_verify_parser.add_argument("--fail", help="Fail on the first error.", action="store_true")


blocks_verify_parser = subparsers.add_parser("bverify", help="Verify the blocks.")


merge_parser = subparsers.add_parser("merge", help="Merge the blocks.")
merge_parser.add_argument("output", help="The output directory.")

args = parser.parse_args()

match args.command:
    case "verify":
        cli.verify_torrent(args)
    case "bverify":
        cli.verify_blocks(args)
    case "merge":
        cli.merge_blocks(args)