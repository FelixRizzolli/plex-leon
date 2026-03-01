import { setActivePinia } from 'pinia';
import { createPinia } from 'pinia';
import { beforeEach, vi } from 'vitest';

// ─── Global Vitest setup ──────────────────────────────────────────────────────

// Fresh Pinia instance for every test
beforeEach(() => {
  setActivePinia(createPinia());
});

// Mock the Electron API bridge so tests run in jsdom without Electron
vi.stubGlobal('api', {
  getAppVersion: vi.fn().mockResolvedValue('4.0.0'),
  getAppName: vi.fn().mockResolvedValue('plex-leon'),
  minimizeWindow: vi.fn(),
  toggleMaximize: vi.fn(),
  closeWindow: vi.fn(),
  openFile: vi.fn().mockResolvedValue(null),
  saveFile: vi.fn().mockResolvedValue(null),
});
