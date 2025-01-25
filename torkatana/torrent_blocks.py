from .types import PathLike, Path
from .blocker import getBlockNamerAndParser

class TorrentBlocks:
    def __init__(self, blocks_path: PathLike, blocks_pattern: str):
        self.__blocks_path = Path(blocks_path).absolute()
        self.__blocks_pattern = blocks_pattern
        self.__namer, self.__parser = getBlockNamerAndParser(blocks_pattern)

    @property
    def blocksPath(self) -> Path:
        return self.__blocks_path
    
    @property
    def blockPattern(self) -> str:
        return self.__blocks_pattern
    
    def getBlockName(self, block_index: int):
        return self.__namer(block_index)
    
    def parseBlockName(self, block_name: str):
        return self.__parser(block_name)
    
    def absPathToBlock(self, block_index: int) -> Path:
        return self.blocksPath / self.getBlockName(block_index)