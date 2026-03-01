// ─── Augment the global Window interface with our IPC bridge ──────────────────

export interface IElectronAPI {
  getAppVersion: () => Promise<string>;
  getAppName: () => Promise<string>;
  minimizeWindow: () => void;
  toggleMaximize: () => void;
  closeWindow: () => void;
  openFile: (filters?: Electron.FileFilter[]) => Promise<string | null>;
  saveFile: (defaultPath?: string) => Promise<string | null>;
  openDirectory: () => Promise<string | null>;
  settings: {
    get: (key: string) => Promise<unknown>;
    set: (key: string, value: unknown) => Promise<boolean>;
  };
}

declare global {
  interface Window {
    api: IElectronAPI;
  }
}

export {};
