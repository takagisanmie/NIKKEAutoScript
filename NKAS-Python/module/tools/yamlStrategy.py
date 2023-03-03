import yaml


def read(path):
    with open(path, 'r', encoding="utf-8") as file:
        data = file.read()
        result = yaml.load(data, Loader=yaml.FullLoader)
        return result


def get(key, data, split=True):
    if split:
        if '.' in key:
            keyList = key.split('.')
        else:
            keyList = key.split('_')
    else:
        keyList = [key]

    for index, key in enumerate(keyList):
        if isinstance(data, dict):
            data = getValue(key, data)

    return data


def getValue(key, data):
    if key in data.keys():
        return data[key]
    else:
        return None


def update(key, value, data, path):
    if '.' in key:
        keyList = key.split('.')
    else:
        keyList = key.split('_')

    result = deepUpdate(data, keyList, value)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(result, f, allow_unicode=True)


def deepUpdate(root, key, value):
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
                result = deepUpdate(root[root_key], key, value)
                root[root_key] = result

    return root
