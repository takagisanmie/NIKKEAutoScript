from datetime import datetime, timedelta

from module.config.config_generated import GeneratedConfig
from module.config.config_updater import ConfigUpdater
from module.config.manual_config import ManualConfig
from module.config.utils import deep_get, DEFAULT_TIME, deep_set, filepath_config, path_to_arg, dict_to_kv
from module.logger import logger


class Function:
    def __init__(self, data):
        self.enable = deep_get(data, keys="Scheduler.Enable", default=False)
        self.command = deep_get(data, keys="Scheduler.Command", default="Unknown")
        self.next_run = deep_get(data, keys="Scheduler.NextRun", default=DEFAULT_TIME)

    def __str__(self):
        enable = "Enable" if self.enable else "Disable"
        return f"{self.command} ({enable}, {str(self.next_run)})"

    __repr__ = __str__

    def __eq__(self, other):
        if not isinstance(other, Function):
            return False

        if self.command == other.command and self.next_run == other.next_run:
            return True
        else:
            return False


def name_to_function(name):
    """
    Args:
        name (str):

    Returns:
        Function:
    """
    function = Function({})
    function.command = name
    function.enable = True
    return function


class NikkeConfig(ConfigUpdater, ManualConfig, GeneratedConfig):
    def __init__(self, config_name, task=None):
        self.config_name = config_name
        self.data = {}
        self.modified = {}
        self.bound = {}
        self.overridden = {}
        self.pending_task = []
        self.waiting_task = []
        self.task: Function
        self.is_template_config = config_name == "template"

        if self.is_template_config:
            logger.info("Using template config, which is read only")
            self.auto_update = False
            self.task = name_to_function("template")
        else:
            self.load()

            if task is None:
                # Bind `Alas` by default which includes emulator settings.
                task = name_to_function("NKAS")
            else:
                # Bind a specific task for debug purpose.
                task = name_to_function(task)

            logger.info(f'task: {task.__str__()}')

            self.bind(task)
            self.task = task
            self.save()

        # logger.attr("Server", self.SERVER)
        logger.attr("Server", 'intl' if 'proximabeta' in self.Emulator_PackageName else 'tw')

    def load(self):
        self.data = self.read_file(self.config_name)
        self.config_override()

        for path, value in self.modified.items():
            deep_set(self.data, keys=path, value=value)

    def bind(self, func, func_set=None):
        """
        Args:
            func (str, Function): Function to run
            func_set (set): Set of tasks to be bound
        """
        if func_set is None:
            func_set = {"General", "NKAS"}

        if isinstance(func, Function):
            func = func.command

        func_set.add(func)

        logger.info(f"Bind task {func_set}")

        # Bind arguments
        visited = set()
        self.bound.clear()
        for func in func_set:
            func_data = self.data.get(func, {})
            for group, group_data in func_data.items():
                for arg, value in group_data.items():
                    path = f"{group}.{arg}"
                    if path in visited:
                        continue
                    """
                        将 func_set 任务组 / 选项组 的 属性覆盖到 GeneratedConfig 的类变量
                    """
                    arg = path_to_arg(path)
                    super().__setattr__(arg, value)
                    self.bound[arg] = f"{func}.{path}"
                    visited.add(path)

        # Override arguments
        for arg, value in self.overridden.items():
            super().__setattr__(arg, value)

    def save(self, mod_name='nkas'):
        if not self.modified:
            return False

        for path, value in self.modified.items():
            deep_set(self.data, keys=path, value=value)

        logger.info(
            f"Save config {filepath_config(self.config_name, mod_name)}, {dict_to_kv(self.modified)}"
        )
        # Don't use self.modified = {}, that will create a new object.
        self.modified.clear()
        self.write_file(self.config_name, data=self.data)

    def config_override(self):
        now = datetime.now().replace(microsecond=0)
        limited = set()

        def limit_next_run(tasks, limit):
            for task in tasks:
                if task in limited:
                    continue
                limited.add(task)
                next_run = deep_get(
                    self.data, keys=f"{task}.Scheduler.NextRun", default=None
                )
                if isinstance(next_run, datetime) and next_run > limit:
                    deep_set(self.data, keys=f"{task}.Scheduler.NextRun", value=now)

        for task in ["Reward"]:
            if not self.is_task_enabled(task):
                self.modified[f"{task}.Scheduler.Enable"] = True
        force_enable = list

        force_enable(
            [
                "Reward",
            ]
        )
        limit_next_run(["Reward"], limit=now + timedelta(hours=12, seconds=-1))
        limit_next_run(self.args.keys(), limit=now + timedelta(hours=24, seconds=-1))

    def get_next_task(self):
        pending = []
        waiting = []
        error = []
        now = datetime.now()
        for func in self.data.values():

            func = Function(func)
            '''
                跳过Scheduler.Enable为False的任务
            '''
            if not func.enable:
                continue
            '''
                从配置中获取的运行时间格式错误
            '''
            if not isinstance(func.next_run, datetime):
                error.append(func)

            elif func.next_run < now:
                '''
                    当前时间 > 该任务的下次运行时间
                '''
                pending.append(func)
            else:
                waiting.append(func)

        if error:
            pending = error + pending

        self.pending_task = pending
        self.waiting_task = waiting

    def is_task_enabled(self, task):
        return bool(self.cross_get(keys=[task, 'Scheduler', 'Enable'], default=False))

    def cross_get(self, keys, default=None):
        """
        Get configs from other tasks.

        Args:
            keys (str, list[str]): Such as `{task}.Scheduler.Enable`
            default:

        Returns:
            Any:
        """
        return deep_get(self.data, keys=keys, default=default)

    def override(self, **kwargs):
        """
        Override anything you want.
        Variables stall remain overridden even config is reloaded from yaml file.
        Note that this method is irreversible.
        """
        for arg, value in kwargs.items():
            self.overridden[arg] = value
            super().__setattr__(arg, value)
