from common.enum.enum import *
from module.tools.yamlStrategy import *


class GeneralConfig:
    Version: str = ''
    New_Version: str = ''

    dict: dict = {}
    Task_Dict: dict = {}
    Simulator_Serial: str = ''
    Simulator_Accelerator: str = ''
    Emulator_JP_PackageName: str = 'com.proximabeta.nikke'
    Emulator_TW_PackageName: str = 'com.gamamobi.nikke'

    Task_List: tuple = ['Reward', 'Destroy', 'FreeStore', 'Commission', 'Conversation',
                        'RookieArena', 'TribeTower', 'SimulationRoom', 'Event', 'Daily']

    # Task_List: tuple = ['Reward', 'Destroy', 'FreeStore', 'Commission', 'Conversation',
    #                     'RookieArena','SimulationRoom']

    # Socket:
    Socket_NameSpace: str = '/nkas'
    Socket_Port: int = 5000
    Socket_HideWindow: bool = False

    # Server:
    Server: int = 1

    # DroidCast
    Droid_Cast_APK_Path = './apk/DroidCast-debug-1.1.0.apk'

    # Droid_Cast_APK_Path = './DroidCastS-release-1.1.5.apk'

    def __init__(self):
        self.initConfig()
        pass

    def initConfig(self):
        self.dict = read(Path.CONFIG)
        self.Task_Dict = read(Path.TASK)
        self.initDict()

    def initDict(self):
        for varName in self.__class__.__dict__:
            if result := get(varName, self.dict):
                self.__dict__[varName] = result

    def get(self, key=None, data=None):
        if not data:
            data = self.Task_Dict

        keyList = key.split('.')
        for index, key in enumerate(keyList):
            if isinstance(data, dict):
                data = self.getValue(key, data)

        return data

    def getValue(self, key, data):
        if key in data.keys():
            return data[key]
        else:
            return None

    def update(self, key, value, data, path):
        result = self.deepUpdate(data, key.split('.'), value)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(result, f, allow_unicode=True)
            f.close()

        if path is Path.CONFIG:
            self.initDict()

        # self.initConfig()

    def deepUpdate(self, root, key, value):
        # 递归遍历嵌套字典
        for root_key, root_value in root.items():
            # 没有子节点
            if len(key) == 1:
                if key[0] == root_key:
                    root[root_key] = value

            # 循环下一个字节点
            elif root_key == key[0]:
                key = key[1:len(key)]
                if isinstance(root[root_key], dict):
                    result = self.deepUpdate(root[root_key], key, value)
                    root[root_key] = result

        return root
