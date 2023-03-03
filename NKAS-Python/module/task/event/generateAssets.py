import os
import struct

import cv2
import numpy as np

TEMPLATE_FOLDER = None
ASSETS_FILE = './module/task/event/event_assets.py'

dirList = []

TYPE_DICT = {
    '89504E47': 'png',
}
max_len = len(max(TYPE_DICT, key=len)) // 2


def generateAssets(ASSETS_FILE='./module/task/event/event_assets.py', assets=None):
    with open(ASSETS_FILE, 'w', newline='') as f:
        for dirName in dirList:
            for file in os.listdir(dirName):
                if not os.path.isdir(os.path.join(dirName, file)):
                    if getFileType(file, dirName):
                        template = cv2.imread(os.path.join(dirName, file), 0)
                        name, ext = os.path.splitext(file)
                        name, sub = os.path.splitext(name)
                        if sub == '':
                            # print(name)
                            x = np.where(np.max(template, axis=0) > 0)[0]
                            y = np.where(np.max(template, axis=1) > 0)[0]
                            position = (x[0], y[0], x[-1], y[-1])
                            for varName in assets.__class__.__dict__:
                                if str(varName) == name:
                                    assets.__dict__[varName] = generateExpression(name, position, dirName)
                            # f.write(generateExpression(name, position, dirName) + '\n')


def getFileType(file, dirName):
    # 读取二进制文件开头一定的长度
    # print(os.path.join(dirName, file))

    with open(os.path.join(dirName, file), 'rb') as f:
        byte = f.read(max_len)
    # 解析为元组
    byte_list = struct.unpack('B' * max_len, byte)
    # 转为16进制
    code = ''.join([('%X' % each).zfill(2) for each in byte_list])
    # 根据标识符筛选判断文件格式
    result = list(filter(lambda x: code.startswith(x), TYPE_DICT))
    if result:
        return TYPE_DICT[result[0]]
    else:
        return 'unknown'


def generateExpression(name, position, dirName):
    dn = (dirName[1:len(dirName)]).replace('\\', '/')
    dn = dn.replace('../', '')
    # template = '\'.' + dn + '/' + name + '.png\''
    template = '.' + dn + '/' + name + '.png'
    # template = '\'' + './module/task/event' + dn + '/' + name + '.png\''
    # id = '\'' + name + '\''
    id = name
    # return '%s = { \'area\' : %s , \'path\' : %s , \'id\' : %s }' % (name, position, template, id)
    return {'area': position, 'path': template, 'id': id}


def generateTemplate(TEMPLATE_FOLDER):
    # p = './module/task/event/templates/e1'
    # TEMPLATE_FOLDER = p

    for dirpath, dirnames, filenames in os.walk(TEMPLATE_FOLDER):
        for dirname in dirnames:
            dirList.append(os.path.join(dirpath, dirname))

    # print(dirList)


if __name__ == '__main__':
    # p = './module/task/event/templates/e1'
    p = './templates/e1'
    generateTemplate(p)
    generateAssets('event_assets.py')
