import os
from common.enum.enum import *
from module.tools.yamlStrategy import *


class GeneralConfig:
    Version: str = ''
    New_Version: str = ''

    config_dict: dict = {}
    task_dict: dict = {}
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

    exception = ['Version', 'Accelerators', 'historyEvent']

    def __init__(self):
        self.initConfig()

    def initConfig(self):
        self.config_temp_dict = read(Path.CONFIG_TEMPLATE)
        if os.path.exists(Path.CONFIG):
            self.config_dict = read(Path.CONFIG)
            self.find_difference(self.config_temp_dict, self.config_dict)
        else:
            self.config_dict = self.config_temp_dict

        self.task_temp_dict = read(Path.TASK_TEMPLATE)
        if os.path.exists(Path.TASK):
            self.task_dict = read(Path.TASK)
            self.find_difference(self.task_temp_dict, self.task_dict)
        else:
            self.task_dict = self.task_temp_dict

        with open(Path.CONFIG, "w", encoding="utf-8") as f:
            yaml.dump(self.config_dict, f, allow_unicode=True)
            f.close()

        with open(Path.TASK, "w", encoding="utf-8") as f:
            yaml.dump(self.task_dict, f, allow_unicode=True)
            f.close()

        self.config_dict['already_check_version'] = False
        self.initDict()

    def initDict(self):
        for varName in self.__class__.__dict__:
            if result := get(varName, self.config_dict):
                self.__dict__[varName] = result

    def get(self, key=None, data=None):
        if not data:
            data = self.task_dict

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

    def find_difference(self, ct, c):
        # 共有的键
        common_keys = set(ct.keys()) & set(c.keys())
        # 新增的键
        new_keys = set(ct.keys()) - set(c.keys())

        for key in common_keys:
            # 如果是该键是另一个键值对，就进行递归
            if isinstance(ct.get(key), dict) and isinstance(c.get(key), dict):
                self.find_difference(ct.get(key), c.get(key))

            elif key in self.exception:
                c[key] = ct.get(key)

        # 将新增的键值对添加进已有配置中
        for key in new_keys:
            c[key] = ct.get(key)
