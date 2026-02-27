// ─── Shared application-wide TypeScript types ─────────────────────────────────

// Re-export the IPC bridge interface from the preload declaration
export type { IElectronAPI } from '../../electron/preload/index.d'

// ── Generic utility types ────────────────────────────────────────────────────

export type Nullable<T> = T | null
export type Optional<T> = T | undefined
export type MaybeRef<T> = T | Ref<T>

// ── Domain types ─────────────────────────────────────────────────────────────

export interface AppInfo {
  name: string
  version: string
}

export interface NavItem {
  label: string
  icon?: string
  route: string
}

// ── API / async state ─────────────────────────────────────────────────────────

export type AsyncStatus = 'idle' | 'loading' | 'success' | 'error'

export interface AsyncState<T> {
  data: Nullable<T>
  status: AsyncStatus
  error: Nullable<string>
}

import type { Ref } from 'vue'
