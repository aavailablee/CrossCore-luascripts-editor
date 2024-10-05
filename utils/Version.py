import pickle
from typing import List, Dict

class ABVerData:
    def __init__(self, name: str, version: int, crc: int, size: int, sizeB: int, url: str, md5: str, isEncypt: bool, key: str):
        self.name = name
        self.version = version
        self.crc = crc
        self.size = size
        self.sizeB = sizeB
        self.url = url
        self.md5 = md5
        self.isEncypt = isEncypt
        self.key = key
        self.path = ""

class VerInfo:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self.abDataList: List[ABVerData] = []
        self.resourceContainer: Dict[str, ABVerData] = {}
        self.subABList: List[str] = []
        self._neededMoveContainer: Dict[str, ABVerData] = {}

class VerMgr:
    def __init__(self):
        self.netData = None

    def load_ver_info(self, path: str, dump_path: str):
        with open(path, 'rb') as f:
            self.netData = pickle.load(f)

        print(f"Dumping version info to {dump_path}...")
        with open(dump_path, 'w') as sw:
            for abVerData in self.netData.abDataList:
                sw.write(f"{abVerData.name}\n")

