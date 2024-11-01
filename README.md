# TorKatana

**inspired by [librorrent](https://www.libtorrent.org/)**

This tool can be used to seperate downloaded (or partially downloaded) torrents into fixed sized block and reconnect them later.

> _Slice torrents like a samurai_

Personally used to download large games as blocks in cloud VMs and join them later in the PC.

## Features 🌃

- Access basic information about the torrent.
  - Name
  - Number of Files
  - Seperate file into
  - Number of Pieces
  - Piece checksums
  - Total size
- Generate and parse block file names for given pattern
- Map Block (Identify a byterange in the torrent from files) `[from libtorrent]`
- Map File (Identify a file or a file slice in the torrent) `[from libtorrent]`
- Verify the torrent integrity
- Read a piece by index

## Usage

> for the purpose of demonstrating I will use [Death's Door by FitGirl Repacks](https://fitgirl-repacks.site/deaths-door/)

### Basic Setup

```python
from torkatana import Torrent

torrent_path = "Death's Door [FitGirl Repack].torrent"

tor = Torrent(torrent_path)
```

### Access Basic Info

```python
tor.path # path to torrent file
tor.name  # Death's Door [FitGirl Repack]
tor.numFiles # 10
tor.numPieces # 1117
tor.pieceLength # 524288 (in bytes) = 512 kB
tor.pieceSize(1116) # 300357 (same as pieceLength except for the last piece)
tor.pieceRange # range(0, 1117)
tor.totalSize # 585405765 (in bytes) = 558.2 MB

tor.files
# (File(index=0, path='fg-01.bin', size=298029043, offset=0), ...)
tor.fileRange # range(0, 10)
tor.getFile(0) # get a specific file
# File(index=0, path='fg-01.bin', size=298029043, offset=0)

tor.hashes # SHA-1 checksums of each piece of the torrent as a string tuple
# ('9c6fd4ef4bcdcb8c38af3917253883e2f2c3b69e', '374bb5b90420f543d8e5aaaa2e59cd4baad302fd', ... )
```

### `mapFile(file_index, file_offset, size)`

> this function was extracted from libtorrent

```python
# file_index := required
# file_offset := defaults to 0
# file_size := defaults to file size

# can be used to to map a file in the torrent

tor.mapFile(2)
# TorrentSlice(first_index=957, first_offset=141401, first_size=382887, jumps=121, last_size=118065)

# first_index := index of the piece that the files begins
# first_offset := file begining position relative to the begining of the piece
# first_size := amount of file content in the first piece
# jupms := number of whole pieces occupied by the file after the first piece
# last_size := amount of file content in the last piece of the range
```

### `mapBlock(piece_index, piece_offset, size, dynamic_size: bool)`

> this function was extracted from libtorrent

```python
# piece_index := required
# piece_offset := defaults to 0
# size := defaults to the pieceLength, can be set to a larget value
# dynamic_size := if set true, when offset + size > totalSize, the size variable is modified such that about conditions is true, if dynamic size is false in such situation programe will raise an error

# can be used to map a piece range to a file range

tor.mapBlock(568) # for this torrey piece 568 is special. it's the piece that contains the last part of the file 0 and the starting part of the file 1. as shown below

# (FileSlice(file_index=0, offset=297795584, size=233459), FileSlice(file_index=1, offset=0, size=290829))
```

### Secondary Setup

This is requred to acces the extended features of the module

#### Physical Path

```python
physical_path = "Downloads/Death's Door [FitGirl Repack]" # this is where downloaded files are stored
tor.setPhysicalPath(physical Path)

# now following options are available

tor.physicalPath
tor.absPathToFile(1)

# setting physical path is essential for beging able to access the actual torrent data in the disk
```

#### Block Details

```python
from torkatana.blocker import MB

blocks_path = "Downloads/bocks"
blocks_pattern = "deaths-door.{index}.fit-girl"
# index will we replaced with the block index and padded with zeros depending on the number of blocks

block_size = MB(100)
n_pieces_in_block = int(block_size/tor.pieceLength)
tor.setNPiecesInBlock(n_pieces_in_block)

# now following options are available

```
