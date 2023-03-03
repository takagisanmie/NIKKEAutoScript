import {io} from "socket.io-client";

const socket = io("http://localhost:5000/nkas")

socket.on('connect_error', (err) => {
    console.log(err)
})

export default class Socket {
    static getSocket() {
        return socket
    }

    static updateConfigByKey(keys, values, type, callback) {
        socket.emit('updateConfigByKey', {
            'keys': keys,
            'values': values,
            'type': type,
            'callback': callback,
        })
    }
    static getConfigByKey(keys, type, callback) {
        socket.emit('getConfigByKey', {
            'keys': keys,
            'type': type,
            'callback': callback,
        })
    }
}


