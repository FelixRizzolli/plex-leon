import { contextBridge, ipcRenderer } from 'electron';

// ─── Typed IPC bridge exposed to the renderer ─────────────────────────────────
// No third-party toolkit – just the built-in Electron contextBridge API.

const api = {
  // App info
  getAppVersion: (): Promise<string> => ipcRenderer.invoke('app:get-version'),
  getAppName: (): Promise<string> => ipcRenderer.invoke('app:get-name'),

  // Window controls
  minimizeWindow: (): void => ipcRenderer.send('window:minimize'),
  toggleMaximize: (): void => ipcRenderer.send('window:maximize-toggle'),
  closeWindow: (): void => ipcRenderer.send('window:close'),

  // Dialogs
  openFile: (filters?: Electron.FileFilter[]): Promise<string | null> =>
    ipcRenderer.invoke('dialog:open-file', filters),
  saveFile: (defaultPath?: string): Promise<string | null> =>
    ipcRenderer.invoke('dialog:save-file', defaultPath),
  openDirectory: (): Promise<string | null> => ipcRenderer.invoke('dialog:open-directory'),
  // Settings
  settings: {
    get: (key: string): Promise<unknown> => ipcRenderer.invoke('settings:get', key),
    set: (key: string, value: unknown): Promise<boolean> =>
      ipcRenderer.invoke('settings:set', key, value),
  },
};

// Expose under `window.api` – contextIsolation keeps renderer sandboxed
contextBridge.exposeInMainWorld('api', api);
