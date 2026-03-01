import { app, BrowserWindow, dialog } from 'electron';
import { ipcMain } from 'electron';
import Store from 'electron-store';

// ─────────────────────────────────────────────────────────────────────────────
// All IPC main-process handlers are registered here.
// Keep handlers thin – business logic belongs in dedicated service modules.
// ─────────────────────────────────────────────────────────────────────────────

export function registerIpcHandlers(): void {
  // ── App info ───────────────────────────────────────────────────────────────
  ipcMain.handle('app:get-version', () => app.getVersion());
  ipcMain.handle('app:get-name', () => app.getName());

  // ── Window controls ────────────────────────────────────────────────────────
  ipcMain.on('window:minimize', () => {
    BrowserWindow.getFocusedWindow()?.minimize();
  });

  ipcMain.on('window:maximize-toggle', () => {
    const win = BrowserWindow.getFocusedWindow();
    if (!win) return;
    win.isMaximized() ? win.unmaximize() : win.maximize();
  });

  ipcMain.on('window:close', () => {
    BrowserWindow.getFocusedWindow()?.close();
  });

  // ── Open/Save dialogs ──────────────────────────────────────────────────────
  ipcMain.handle('dialog:open-file', async (_event, filters?: Electron.FileFilter[]) => {
    const { canceled, filePaths } = await dialog.showOpenDialog({
      properties: ['openFile'],
      filters: filters ?? [{ name: 'All Files', extensions: ['*'] }],
    });
    return canceled ? null : filePaths[0];
  });

  ipcMain.handle('dialog:save-file', async (_event, defaultPath?: string) => {
    const { canceled, filePath } = await dialog.showSaveDialog({
      defaultPath,
    });
    return canceled ? null : filePath;
  });

  // ── Settings (persistent store) ─────────────────────────────────────────
  const store = new Store({ name: 'settings' });

  ipcMain.handle('settings:get', (_event, key: string) => {
    return store.get(key);
  });

  ipcMain.handle('settings:set', (_event, key: string, value: unknown) => {
    store.set(key, value);
    return true;
  });
}
