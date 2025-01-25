from pathlib import Path

from .torrent_info import TorrentInfo
from .types import PathLike
from .physical import reader, writer

class TorrentPhysical:
    def __init__(self, torrent: TorrentInfo, physics_path: PathLike):
        self.__ti = torrent
        self.__physical_path = Path(physics_path).absolute()
        self.__physical_files = tuple(map(lambda f: self.__physical_path / f.path, torrent.files))

    @property
    def torrent(self) -> TorrentInfo:
        return self.__ti
    
    @property
    def physicsPath(self) -> Path:
        return self.__physical_path
    
    @property
    def files(self) -> tuple[Path, ...]:
        return self.__physical_files
    
    def exists(self) -> list[bool]:
        """
        Check if each file in the list of files exists.

        Returns:
            list[bool]: A list of boolean values indicating the existence of each file.
        """
        return list(map(lambda f: f.exists(), self.files))
    
    def reader(self):
        return reader(self.files.__getitem__)

    def writer(self, create=False):
        return writer(self.files.__getitem__, create)