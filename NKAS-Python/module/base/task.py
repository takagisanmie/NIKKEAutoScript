import glo
from common.enum.enum import *
from module.tools._time import *


class Task:

    @staticmethod
    def isActivated(config, name):
        return config.get('Task.' + name + '.activate', config.Task_Dict)

    @staticmethod
    def getNextExecutionTime(config, name):
        return config.get('Task.' + name + '.nextExecutionTime', config.Task_Dict)

    @staticmethod
    def finish(config, name):
        key = 'Task.' + name + '.nextExecutionTime'
        config.update(key, getTaskResetTime(), config.Task_Dict, Path.TASK)
        glo.getSocket().emitSingleParameter('checkAllTaskStates', 'data', config.Task_Dict)
