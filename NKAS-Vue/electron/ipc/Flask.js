const {ipcMain} = require('electron')
const axios = require('axios'); //request请求库

ipcMain.handle('testFlask', async (e, options) => {
    const response = await axios(options)
    return response.data.result
})

