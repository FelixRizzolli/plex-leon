import { resolve } from 'path'
import { defineConfig, externalizeDepsPlugin } from 'electron-vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  // ─── Main Process ────────────────────────────────────────────────────────────
  main: {
    plugins: [externalizeDepsPlugin()],
    resolve: {
      alias: {
        '@main': resolve('electron/main'),
      },
    },
    build: {
      rollupOptions: {
        input: {
          index: resolve(__dirname, 'electron/main/index.ts'),
        },
        external: ['electron'],
        output: {
          // Vite 8 defaults to ESM (.mjs); electron-vite expects .js (CJS)
          format: 'cjs',
          entryFileNames: '[name].js',
        },
      },
    },
  },

  // ─── Preload Script ──────────────────────────────────────────────────────────
  preload: {
    plugins: [externalizeDepsPlugin()],
    resolve: {
      alias: {
        '@preload': resolve('electron/preload'),
      },
    },
    build: {
      rollupOptions: {
        input: {
          index: resolve(__dirname, 'electron/preload/index.ts'),
        },
        output: {
          // Same as main: force CJS .js output
          format: 'cjs',
          entryFileNames: '[name].js',
        },
      },
    },
  },

  // ─── Renderer (Vue App) ──────────────────────────────────────────────────────
  renderer: {
    root: '.',
    build: {
      rollupOptions: {
        input: {
          index: resolve(__dirname, 'index.html'),
        },
      },
    },
    resolve: {
      alias: {
        '@': resolve('src'),
        '@components': resolve('src/components'),
        '@stores': resolve('src/stores'),
        '@views': resolve('src/views'),
        '@composables': resolve('src/composables'),
        '@assets': resolve('src/assets'),
      },
    },
    plugins: [
      vue({
        // Enable Vue 3.6 Vapor mode compiler options
        // Per-component opt-in: add `vapor` attribute to <script vapor setup>
        // or use compilerOptions here for global defaults
        features: {
          // Opt-in Vapor compilation globally or let components self-declare
          optionAPI: false,
        },
      }),
    ],
  },
})
