import glo
from common.enum.enum import *
from module.tools.timer import *


class Task:

    @staticmethod
    def isActivated(config, name):
        return config.get('Task.' + name + '.activate', config.task_dict)

    @staticmethod
    def getNextExecutionTime(config, name):
        return config.get('Task.' + name + '.nextExecutionTime', config.task_dict)

    @staticmethod
    def finish(config, name, second=0):
        key = 'Task.' + name + '.nextExecutionTime'
        config.update(key, getTaskResetTime() + second, config.task_dict, Path.TASK)
        # glo.getSocket().emitSingleParameter('checkAllTaskStates', 'data', config.Task_Dict)
        glo.getSocket().getAllTaskStates()

    @staticmethod
    def when(config, name, second):
        key = 'Task.' + name + '.nextExecutionTime'
        config.update(key, after(second), config.task_dict, Path.TASK)
        # glo.getSocket().emitSingleParameter('checkAllTaskStates', 'data', config.Task_Dict)
        glo.getSocket().getAllTaskStates()
