from flask import Flask
from flask_socketio import SocketIO

import glo
from common.enum.enum import Path
from module.base.base import BaseModule
from module.thread.thread import *


class Socket(BaseModule):
    app = Flask(__name__)
    # socketio = SocketIO(app, async_mode='threading')
    socketio = SocketIO(app)
    config = glo.getNKAS().config

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        glo.set_value('socket', self)

    def emit(self, event, data):
        self.socketio.emit(event, data, namespace=self.config.Socket_NameSpace)

    def emitSingleParameter(self, event, key, value):
        self.socketio.emit(event, {key: value}, namespace=self.config.Socket_NameSpace)

    def run(self):
        self.changeWindow()
        self.socketio.run(self.app, port=self.config.Socket_Port, allow_unsafe_werkzeug=True)

    @staticmethod
    @socketio.on('connect', namespace=config.Socket_NameSpace)
    def connect():
        pass

    @staticmethod
    @socketio.on('disconnect', namespace=config.Socket_NameSpace)
    def disconnect():
        pass

    @staticmethod
    @socketio.on('startScheduler', namespace=config.Socket_NameSpace)
    def startScheduler():
        futures.run(glo.getNKAS().loop)

    @staticmethod
    @socketio.on('stopScheduler', namespace=config.Socket_NameSpace)
    def stopScheduler():
        glo.getNKAS().state = False
        for thread in threading.enumerate():
            if 'NKAS' in thread.name:
                threadManager.stopThread(thread)
                continue

    @staticmethod
    @socketio.on('stopNKAS', namespace=config.Socket_NameSpace)
    def stopNKAS():
        import os
        import signal

        print('stop NKAS')
        # os._exit(0)
        pid = os.getpid()
        os.kill(pid, signal.SIGTERM)
        os.system('taskkill /PID %d /F' % pid)

    @staticmethod
    @socketio.on('checkSchedulerState', namespace=config.Socket_NameSpace)
    def checkSchedulerStare():
        glo.getSocket().emitSingleParameter('checkSchedulerState', 'state', glo.getNKAS().state)

    @staticmethod
    @socketio.on('checkAllTaskStates', namespace=config.Socket_NameSpace)
    def getAllTaskStates():

        all_task = Socket.config.get('Task')
        task_list = [Socket.config.get('Task.' + x) for x in all_task if Socket.config.get('Task.' + x)['activate']]
        task_list.sort(key=lambda x: x['nextExecutionTime'])

        glo.getSocket().emitSingleParameter('checkAllTaskStates', 'data', {'Task': task_list})

    @staticmethod
    @socketio.on('updateConfigByKey', namespace=config.Socket_NameSpace)
    def updateConfigByKey(data):
        type = data['type']
        callback = data['callback']
        for index, key in enumerate(data['keys']):
            if type == 'task':
                Socket.config.update(key, data['values'][index], Socket.config.Task_Dict, Path.TASK)
            elif type == 'config':
                Socket.config.update(key, data['values'][index], Socket.config.dict, Path.CONFIG)

        glo.getSocket().emit(callback, None)

    @staticmethod
    @socketio.on('getConfigByKey', namespace=config.Socket_NameSpace)
    def getConfigByKey(data):
        type = data['type']
        callback = data['callback']
        result = []
        for index, key in enumerate(data['keys']):
            if type == 'task':
                result.append({'key': key,
                               'value': Socket.config.get(key, Socket.config.Task_Dict)})
            elif type == 'config':
                result.append({'key': key,
                               'value': Socket.config.get(key, Socket.config.dict)})

        glo.getSocket().emit(callback, {'result': result})

    # Setting-General
    @staticmethod
    @socketio.on('hideWindow', namespace=config.Socket_NameSpace)
    def _hideWindow():
        isHidden = Socket.config.get('Socket.HideWindow', Socket.config.dict)
        if isHidden:
            Socket.hideWindow()
        else:
            Socket.showWindow()

    # Setting-Conversation
    @staticmethod
    @socketio.on('getConfigByKeyInConversation', namespace=config.Socket_NameSpace)
    def getConfigByKeyInConversation(data):
        from _conversation import Nikke_list
        for k in data['keys']:
            # 在所有可选的nikke中过滤出已选的
            if k['key'] == 'Task.Conversation.nikkeList':
                k['Nikke_list'] = Nikke_list
                k['Nikke_list_selected'] = Socket.config.get(k['key'], Socket.config.Task_Dict)

        glo.getSocket().emitSingleParameter('getConfigByKeyInConversation', 'data', data)

    # Setting-Simulator
    @staticmethod
    @socketio.on('changeSerial', namespace=config.Socket_NameSpace)
    def changeSerial():
        from module.base.decorator import del_cached_property
        del_cached_property(glo.getNKAS().device, 'u2')
        del_cached_property(glo.getNKAS().device, 'adb')

    # Setting-General
    @staticmethod
    @socketio.on('notification_test', namespace=config.Socket_NameSpace)
    def notification_test():
        from winotify import Notification
        from win10toast import ToastNotifier

        notification = Socket.config.get('Notification', Socket.config.dict)

        if notification == 1:
            toast = ToastNotifier()
            toast.show_toast(title="NKAS", msg="我是样式一",
                             icon_path=r"./common/ico/Helm-Circle.ico", duration=10)

        elif notification == 2:
            ico_path = __file__
            ico_path = ico_path.replace('module\\socket\\socket.py', '')
            toast = Notification(app_id="NKAS",
                                 title="NKAS",
                                 msg="我是样式二",
                                 icon=f'{ico_path}common\ico\Helm-Circle.ico', duration='long')

            toast.show()

    @staticmethod
    @socketio.on('checkVersion', namespace=config.Socket_NameSpace)
    def checkVersion():
        import requests
        import json
        from module.tools.yamlStrategy import get

        latest = 'https://api.github.com/repos/takagisanmie/NIKKEAutoScript/releases/latest'
        session = requests.Session()
        request = session.get(latest)
        code = request.status_code
        if code == 200:
            content = json.loads(request.content.decode())
            version = get('tag_name', content, False)

            version = version[1:].split('.')
            sum1 = 0
            for n in version:
                sum1 += int(n)

            version2 = Socket.config.Version[1:].split('.')
            sum2 = 0
            for n in version2:
                sum2 += int(n)

            if sum1 == sum2:
                glo.getSocket().emit('is_current_version', None)
            elif sum1 > sum2:
                Socket.config.New_Version = version
                glo.getSocket().emitSingleParameter('new_version_available', 'data', version)
                assets = get('assets', content)
                data = list(filter(lambda x: 'NKAS-Update-Vue' in x['name'], assets))
                if len(data) > 0:
                    glo.getSocket().emitSingleParameter('new_nkas_version_available', 'data', version)
            else:
                glo.getSocket().emit('is_current_version', None)


        else:
            glo.getSocket().emit('check_version_failed', None)

    @staticmethod
    @socketio.on('updateNKAS', namespace=config.Socket_NameSpace)
    def updateNKAS():
        import requests
        import io
        import zipfile

        session = requests.Session()
        latest = f'https://github.com/takagisanmie/NIKKEAutoScript/releases/download/{Socket.config.New_Version}/NKAS-Update.zip'
        response = session.get(latest)
        code = response.status_code
        if code == 200:
            zip_file = zipfile.ZipFile(io.BytesIO(response.content))
            for file in zip_file.namelist():
                if str(file) == 'NKAS-Vue':
                    # 需要手动更新
                    pass

                zip_file.extract(file, path='../')
        else:
            glo.getSocket().emit('check_version_failed', None)
            return

        glo.getSocket().emit('update_NKAS_success', None)
