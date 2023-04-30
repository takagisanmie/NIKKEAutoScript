// @ts-ignore
import path from 'path'
import {app, BrowserWindow} from 'electron'
import {PyShell} from '../src/config/pyshell';
import {webuiArgs} from '../src/config/config';
import './ipc/WindowStrategy'

export const nkas = new PyShell('gui.py', webuiArgs);

nkas.end(function (err: string) {
    console.log(err)
});

setTimeout(() => {
    const WinState = require('electron-win-state').default

    let win: BrowserWindow | null = null;

    const winState = new WinState({
        defaultWidth: 1280,
        defaultHeight: 720
    })

    function createWindow() {
        // 创建浏览器窗口
        win = new BrowserWindow({
            ...winState.winOptions,
            show: false,
            icon: path.join(__dirname, '../../dist/Helm.ico'),
            //边框
            frame: false,
            titleBarStyle: 'hiddenInset',
            webPreferences: {
                preload: path.join(__dirname, 'preload.js'),
                //在渲染进程使用node
                nodeIntegration: true,
                contextIsolation: false,
                //跨域
                webSecurity: false
            }
        })
        if (app.isPackaged) {
            win.loadFile(path.join(__dirname, '../../dist/index.html'))
            // win.webContents.openDevTools()

        } else {
            win.loadURL('http://localhost:5173/')
            win.webContents.openDevTools()
        }
        win.on('ready-to-show', () => {
            win?.show();
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
}, 8000)