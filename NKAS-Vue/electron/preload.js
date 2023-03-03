const {contextBridge, ipcRenderer} = require('electron')
//WindowStrategyAPI
contextBridge.exposeInMainWorld('WindowStrategyAPI',
    {
        WindowToMin: async () => {
            await ipcRenderer.invoke('WindowToMin')
        },
        WindowToFullScreen: async () => {
            await ipcRenderer.invoke('WindowToFullScreen')
        },
        WindowToClose: async () => {
            await ipcRenderer.invoke('WindowToClose')
        },
    })

//FlaskAPI
contextBridge.exposeInMainWorld('FlaskAPI',
    {
        testFlask: async (options) => {
            const result = await ipcRenderer.invoke('testFlask',options)
            return result
        }
    })


