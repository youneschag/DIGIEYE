const { app, BrowserWindow, ipcMain, screen } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const url = require('url');
const fs = require('fs');
const net = require('net');


let mainWindow;

function createWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;
  mainWindow = new BrowserWindow({
    width: width,
    height: height,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true,
    },
  });

  mainWindow.webContents.on('did-finish-load', () => {
    mainWindow.webContents.executeJavaScript(`
      require('${path.join(__dirname, 'src', 'renderer.js')}');
      window.cancelClicked = () => {
        mainWindow.webContents.send('cancelClicked');
      };
      window.sendClicked = () => {
        mainWindow.webContents.send('sendClicked');
      };
    `);
  });

  // Load the index.html file.
  const startUrl = isDev
    ? 'http://localhost:3000' // Development server URL
    : url.format({
        pathname: path.join(__dirname, '..', 'public', 'index.html'), // Path to the built HTML file
        protocol: 'file:',
        slashes: true,
      });

  mainWindow.loadFile(path.join(__dirname, '..', 'public', 'index.html'));

  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }

  // Open the DevTools.
  if (isDev) {
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  }
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });

  ipcMain.on('cancelClicked', () => {
    mainWindow.webContents.executeJavaScript(`
      cancelClicked();
    `);
  });

  ipcMain.on('sendClicked', (event, password) => {
    mainWindow.webContents.executeJavaScript(`
      sendClicked();
    `);
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});