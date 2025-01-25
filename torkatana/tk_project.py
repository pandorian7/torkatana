from torkatana import physical
from torkatana.blocks_span import BlockSpan
from torkatana.torrent_info import TorrentInfo
from .types import FilePath, Path
from .torrent import TorKatana
from .priority_span import PrioritySpan
from typing import TypedDict
import os.path
import json

from glob import glob

class TorKatanaOptions(TypedDict):
    physical_path: str
    block_pattern: str


class TorKatanaProject:
    def __init__(self, project_folder: FilePath, options: TorKatanaOptions = dict()):
        self.__project_folder = Path(project_folder)


        res = list(glob("*.torrent", root_dir=project_folder))
        if len(res) == 0:
            raise FileNotFoundError(f"No torrent file found in {project_folder}")
        if len(res) > 1:
            raise ValueError(f"Multiple torrent files found in {project_folder}")
        
        torrent_path = self.__project_folder / res[0]

        info = TorrentInfo(torrent_path)
        physical_path = options.get("physical_path") or self.__project_folder.parent / info.name
        block_pattern = options.get("block_pattern", None)
        blocks_path = self.__project_folder
        
        self.__torkatana = TorKatana(
            torrent_path,
            physical_path,
            blocks_path,
            block_pattern
        )

    @classmethod
    def loadProject(cls, project_folder: FilePath):
        res = list(glob("*.katana.json", root_dir=project_folder))
        
        if len(res) == 0:
            raise FileNotFoundError(f"No Project Config file found in {project_folder}")
        if len(res) > 1:
            raise ValueError(f"Multiple Project Config files found in {project_folder}")
    
        project_config_file = os.path.join(project_folder, res[0])

        with open(project_config_file, "r") as file:
            data = json.load(file)

        proj = cls(project_folder, {
            "block_pattern": data["block_pattern"]
        })

        bs_data = data['blockspan']
        bs = BlockSpan(proj.katana.torrent)

        for block in bs_data:
            bs.addBlock()
            for piece in block:
                bs.addPieceToBlock(-1, piece)
        proj.katana.blockSpan = bs
        return proj

    @property
    def projectFolder(self):
        return self.__project_folder

    @property
    def katana(self):
        return self.__torkatana
    
    def emptyPrioritySpan(self):
        return PrioritySpan.Paused(self.katana.torrent)

    def save(self):
        config_json_fp = f"{self.katana.torrent.name}.katana.json"
        data = {
            "blockspan": self.katana.blockSpan.toArray(),
            "block_pattern": self.katana.blocks.blockPattern
        }
        with open(self.__project_folder / config_json_fp, "w") as file:
            json.dump(data, file)