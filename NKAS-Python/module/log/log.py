class Log:
    def INFO(self, socket, data):
        socket.emit('insertLog', self.getLog('INFO', data))

    def WARNING(self, socket, data):
        socket.emit('insertLog', self.getLog('WARNING', data))

    def ERROR(self, socket, data):
        socket.emit('insertLog', self.getLog('ERROR', data))

    def LINE(self, socket, data):
        socket.emit('insertLog', self.getLog('LINE', data))

    def getLog(self, type, data):
        log = {
            'type': type,
            'text': data
        }
        return log
