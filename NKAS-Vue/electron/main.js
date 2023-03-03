const {app, BrowserWindow} = require('electron');
const path = require('path');
const WinState = require('electron-win-state').default

require('./ipc/WindowStrategy')
require('./ipc/Flask')

let win = null;
const winState = new WinState({
    defaultWidth: 1280,
    defaultHeight: 720
})

function createWindow() {
    // 创建浏览器窗口
    win = new BrowserWindow({
        ...winState.winOptions,
        show: false,
        //边框
        frame: false,
        titleBarStyle: 'hiddenInset',
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            //在渲染进程使用node
            // nodeIntegration: true,
            // contextIsolation: false,
            //跨域
            webSecurity: false
        }
    })
    if (app.isPackaged) {
        win.loadFile('./dist/index.html')
        // win.webContents.openDevTools()

    } else {
        win.loadURL('http://localhost:5173/')
        win.webContents.openDevTools()
    }
    win.on('ready-to-show', () => {
        win.show()
    })
    winState.manage(win)

}

app.whenReady().then(() => {
    createWindow();
    app.on('activate', function () {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') app.quit();
})
