from module.log.log import Log


class BaseModule(Log):
    def __init__(self, config=None, device=None, socket=None):
        self.config = config
        self.device = device
        self.socket = socket

    def appear_then_click(self, button, then, screenshot=False, *args, **kwargs):
        if screenshot:
            self.device.screenshot()

        if self.device.isVisible(button):
            self.device.click(button, then, *args, **kwargs)
            return True

    def INFO(self, *args, **kwargs):
        super(BaseModule, self).INFO(self.socket, *args, **kwargs)

    def ERROR(self, *args, **kwargs):
        super(BaseModule, self).ERROR(self.socket, *args, **kwargs)

    def LINE(self, *args, **kwargs):
        super(BaseModule, self).LINE(self.socket, *args, **kwargs)

    @staticmethod
    def hideWindow():
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    @staticmethod
    def showWindow():
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 1)

    @staticmethod
    def changeWindow():
        import glo
        isHidden = glo.getNKAS().config.get('Socket.HideWindow', glo.getNKAS().config.dict)
        if isHidden:
            BaseModule.hideWindow()
        else:
            BaseModule.showWindow()

    @staticmethod
    def getErrorInfo():
        import glo
        import traceback
        socket = glo.getSocket()
        tb = traceback.format_exc().split('File')
        for index, i in enumerate(tb):
            e = i.split('\\')
            for index2, x in enumerate(e):
                if '.py' in x:
                    file = x.split('",')[0]
                    line = x.split('",')[1].split('\n')[0].split(',')[0]
                    func = x.split('",')[1].split('\n')[1].lstrip()
                    print(f'in {file}{line}')
                    socket.emit('insertLog', {'type': 'ERROR', 'text': f'in {file}{line}'})
                    print(f'function: {func}')
                    socket.emit('insertLog', {'type': 'ERROR', 'text': f'code or function: {func}'})
                    if index == len(tb) - 1:
                        error = x.split('",')[1].split('\n')[2]
                        print(f'error: {error}')
                        socket.emit('insertLog', {'type': 'ERROR', 'text': f'{error}'})
