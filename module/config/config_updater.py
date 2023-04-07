from copy import deepcopy
from datetime import datetime
from functools import cached_property

from module.config.utils import read_file, filepath_config, deep_get, parse_value, filepath_args, deep_set, deep_iter, \
    write_file, filepath_argument, data_to_type, path_to_arg, filepath_code, deep_default

CONFIG_IMPORT = '''
import datetime

# This file was automatically generated by module/config/config_updater.py.
# Don't modify it manually.


class GeneratedConfig:
    """
    Auto generated configuration
    """
'''.strip().split('\n')


class ConfigGenerator:
    @cached_property
    def argument(self):
        """
        Load argument.yaml, and standardise its structure.

        <group>:
            <argument>:
                type: checkbox|select|textarea|input
                value:
                option (Optional): Options, if argument has any options.
                validate (Optional): datetime
        """
        data = {}
        raw = read_file(filepath_argument('argument'))
        for path, value in deep_iter(raw, depth=2):
            arg = {
                'type': 'input',
                'value': '',
                # option
            }
            if not isinstance(value, dict):
                value = {'value': value}
            arg['type'] = data_to_type(value, arg=path[1])
            if isinstance(value['value'], datetime):
                arg['type'] = 'datetime'
                arg['validate'] = 'datetime'
            # Manual definition has the highest priority
            arg.update(value)
            deep_set(data, keys=path, value=arg)

        # Define storage group
        arg = {
            'type': 'storage',
            'value': {},
            'valuetype': 'ignore',
            'display': 'disabled',
        }
        deep_set(data, keys=['Storage', 'Storage'], value=arg)
        return data

    @cached_property
    def default(self):
        """
        <task>:
            <group>:
                <argument>: value
        """
        return read_file(filepath_argument('default'))

    @cached_property
    def task(self):
        """
        <task>:
            - <group>
        """
        return read_file(filepath_argument('task'))

    @cached_property
    def override(self):
        """
        <task>:
            <group>:
                <argument>: value
        """
        return read_file(filepath_argument('override'))

    @cached_property
    def args(self):
        """
        Merge definitions into standardised json.

            task.yaml ---+
        argument.yaml ---+-----> args.json
        override.yaml ---+
         default.yaml ---+

        """
        # Construct args

        data = {}
        for task, groups in self.task.items():
            # Add storage to all task
            groups.append('Storage')
            for group in groups:
                if group not in self.argument:
                    print(f'`{task}.{group}` is not related to any argument group')
                    continue
                deep_set(data, keys=[task, group], value=deepcopy(self.argument[group]))

        def check_override(path, value):
            # Check existence
            old = deep_get(data, keys=path, default=None)
            if old is None:
                print(f'`{".".join(path)}` is not a existing argument')
                return False
            # Check type
            # But allow `Interval` to be different
            old_value = old.get('value', None) if isinstance(old, dict) else old
            value = old.get('value', None) if isinstance(value, dict) else value
            if type(value) != type(old_value) \
                    and old_value is not None \
                    and path[2] not in ['SuccessInterval', 'FailureInterval']:
                print(
                    f'`{value}` ({type(value)}) and `{".".join(path)}` ({type(old_value)}) are in different types')
                return False
            # Check option
            if isinstance(old, dict) and 'option' in old:
                if value not in old['option']:
                    print(f'`{value}` is not an option of argument `{".".join(path)}`')
                    return False
            return True

        # Set defaults
        for p, v in deep_iter(self.default, depth=3):
            if not check_override(p, v):
                continue
            deep_set(data, keys=p + ['value'], value=v)

        # Override non-modifiable arguments
        for p, v in deep_iter(self.override, depth=3):
            if not check_override(p, v):
                continue
            if isinstance(v, dict):
                if deep_get(v, keys='type') in ['lock']:
                    deep_default(v, keys='display', value="disabled")
                elif deep_get(v, keys='value') is not None:
                    deep_default(v, keys='display', value='hide')
                for arg_k, arg_v in v.items():
                    deep_set(data, keys=p + [arg_k], value=arg_v)
            else:
                deep_set(data, keys=p + ['value'], value=v)
                deep_set(data, keys=p + ['display'], value='hide')
        # Set command
        for task in self.task.keys():
            if deep_get(data, keys=f'{task}.Scheduler.Command'):
                deep_set(data, keys=f'{task}.Scheduler.Command.value', value=task)
                deep_set(data, keys=f'{task}.Scheduler.Command.display', value='hide')

        return data

    @cached_property
    def menu(self):
        """
        Generate menu definitions

        task.yaml --> menu.json

        """
        data = {}

        # Task menu
        group = ''
        tasks = []
        with open(filepath_argument('task'), 'r', encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip('\n')
                if '=====' in line:
                    if tasks:
                        deep_set(data, keys=f'Task.{group}', value=tasks)
                    group = line.strip('#=- ')
                    tasks = []
                if group:
                    if line.endswith(':'):
                        tasks.append(line.strip('\n=-#: '))
        if tasks:
            deep_set(data, keys=f'Task.{group}', value=tasks)

        return data

    def generate_code(self):
        """
        Generate python code.

        args.json ---> config_generated.py

        """
        visited_group = set()
        visited_path = set()

        lines = CONFIG_IMPORT
        for path, data in deep_iter(self.argument, depth=2):
            group, arg = path
            if group not in visited_group:
                lines.append('')
                lines.append(f'    # Group `{group}`')
                visited_group.add(group)

            option = ''
            if 'option' in data and data['option']:
                option = '  # ' + ', '.join([str(opt) for opt in data['option']])
            path = '.'.join(path)
            lines.append(f'    {path_to_arg(path)} = {repr(parse_value(data["value"], data=data))}{option}')
            visited_path.add(path)

        with open(filepath_code(), 'w', encoding='utf-8', newline='') as f:
            for text in lines:
                f.write(text + '\n')

    def generate(self):
        write_file(filepath_args(), self.args)
        write_file(filepath_args('menu'), self.menu)
        self.generate_code()


class ConfigUpdater:
    def read_file(self, config_name, is_template=False):
        """
        Read and update config file.

        Args:
            config_name (str): ./config/{file}.json
            is_template (bool):

        Returns:
            dict:
        """
        old = read_file(filepath_config(config_name))
        new = self.config_update(old, is_template=is_template)
        # The updated config did not write into file, although it doesn't matters.
        # Commented for performance issue
        # self.write_file(config_name, new)
        return new

    def config_update(self, old, is_template):
        new = {}

        def deep_load(keys):
            data = deep_get(self.args, keys=keys, default={})
            value = deep_get(old, keys=keys, default=data['value'])
            if is_template or value is None or value == '' or data['type'] == 'lock' or data.get('display') == 'hide':
                value = data['value']
            value = parse_value(value, data=data)
            deep_set(new, keys=keys, value=value)

        for path, _ in deep_iter(self.args, depth=3):
            deep_load(path)

        return new

    @cached_property
    def args(self):
        return read_file(filepath_args())

    @staticmethod
    def write_file(config_name, data, mod_name='nkas'):
        """
        Write config file.

        Args:
            config_name (str): ./config/{file}.json
            data (dict):
            mod_name (str):
        """
        write_file(filepath_config(config_name, mod_name), data)

    def update_file(self, config_name, is_template=False):
        """
        Read, update and write config file.

        Args:
            config_name (str): ./config/{file}.json
            is_template (bool):

        Returns:
            dict:
        """
        data = self.read_file(config_name, is_template=is_template)
        self.write_file(config_name, data)
        return data


if __name__ == '__main__':
    import os

    os.chdir(os.path.join(os.path.dirname(__file__), '../../'))

    """
        task.yaml 定义了最基本的结构
         
            在task.yaml中定义的 ====== ~ ====== 为一个任务组，'~' 是该 任务组/选项组 的名字，是生成menu.json时的标识
            task.yaml中每个字段都为一个任务，其值为一个数组，定义了该任务的选项组(属性)，其值为argument.yaml中的一级字段
        
        argument.yaml 定义了每个任务的属性的详细结构
        
            在argument.yaml中每个字段的第一级都为一个选项组
            只要某个字段的第一级(键)的在task.yaml某个字段的值(数组)中，在生成时这个任务就会拥有这个字段的值(选项组)
            
            argument.yaml定义的任务属性一共有四种
            当某个二级字段拥有 value 字段时 或者 值为 字符串/数字/时间，该字段为input选项
            当某个二级字段拥有 value && option 字段时，该字段为select选项
            当某个二级字段的键 带有 'Filter' 时，该字段为textarea选项
            当某个二级字段的值为 ture / false 时，该字段为checkbox选项
            
            argument.yaml中每个二级字段都有可选的字段，【display】【valuetype】【validate】
            如果定义了display字段，那么该属性的结构应为:
            
            Reward:
                CollectOil: 
                    value: true
                    display: hide
            
            并且该属性不会渲染到web中
        
        default.yaml 定义了每个任务属性的默认值
        
        override.yaml 和 default.yaml 相似，定义了每个任务属性值
        
            override.yaml可以为每个任务添加type字段
            如果定义了type字段，那么type的字段的值只能为lock
            在生成时，会生成type字段，其值为lock，并且会生成display字段，其值为disabled
            如果不定义，在生成时，会生成type字段，其值为该属性原来的任务属性【input】【select】【checkbox】【textarea】
        
        ConfigGenerator().generate()
        生成config_generated.py，args.json，menu.json
        
            config_generated.py 的内容为 argument.yaml 每个任务属性的默认值
            每个属性为生成类GeneratedConfig的类变量，以'_'衔接
            
            args.json 为每个任务的属性信息，由 task.yaml，argument.yaml，default.yaml，override.yaml，组合而成
            
            menu.json 为 任务组/选项组，由 task.yaml 生成
            
            template.json 为 args.json的简化，每个任务属性只保留了值
        
        ConfigUpdater().update_file('template', is_template=True)
        会将args.json的值覆盖到template.json

    """

    ConfigGenerator().generate()
    ConfigUpdater().update_file('template', is_template=True)