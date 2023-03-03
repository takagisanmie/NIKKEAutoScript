const {app, BrowserWindow, ipcMain} = require('electron')

ipcMain.handle('WindowToMin', async (e) => {
    //主窗口ID
    BrowserWindow.fromId(1).minimize()
})

ipcMain.handle('WindowToFullScreen', async (e) => {
    let win = BrowserWindow.fromId(1)
    win.setFullScreen(win.isFullScreen() ? false : true)

})
ipcMain.handle('WindowToClose', async (e) => {
    app.quit()
})