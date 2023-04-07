import os
import re

DEPLOY_CONFIG = './config/deploy.yaml'
DEPLOY_TEMPLATE = './deploy/template'


def poor_yaml_read(file):
    """
    Poor implementation to load yaml without pyyaml dependency, but with re

    Args:
        file (str):

    Returns:
        dict:
    """
    if not os.path.exists(file):
        return {}

    data = {}
    regex = re.compile(r'^(.*?):(.*?)$')
    with open(file, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip('\n\r\t ').replace('\\', '/')
            if line.startswith('#'):
                continue
            result = re.match(regex, line)
            if result:
                k, v = result.group(1), result.group(2).strip('\n\r\t\' ')
                if v:
                    if v.lower() == 'null':
                        v = None
                    elif v.lower() == 'false':
                        v = False
                    elif v.lower() == 'true':
                        v = True
                    elif v.isdigit():
                        v = int(v)
                    data[k] = v

    return data


def poor_yaml_write(data, file, template_file=DEPLOY_TEMPLATE):
    """
    Args:
        data (dict):
        file (str):
        template_file (str):
    """
    with open(template_file, 'r', encoding='utf-8') as f:
        text = f.read().replace('\\', '/')

    for key, value in data.items():
        if value is None:
            value = 'null'
        elif value is True:
            value = "true"
        elif value is False:
            value = "false"
        text = re.sub(f'{key}:.*?\n', f'{key}: {value}\n', text)

    with open(file, 'w', encoding='utf-8', newline='') as f:
        f.write(text)
