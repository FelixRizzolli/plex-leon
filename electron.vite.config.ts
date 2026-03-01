import tailwindcss from '@tailwindcss/vite';
import vue from '@vitejs/plugin-vue';
import { defineConfig, externalizeDepsPlugin } from 'electron-vite';
import { resolve } from 'path';

export default defineConfig({
  // ─── Main Process ────────────────────────────────────────────────────────────
  main: {
    plugins: [externalizeDepsPlugin()],
    resolve: {
      alias: {
        '@main': resolve(__dirname, 'electron/main'),
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
        '@preload': resolve(__dirname, 'electron/preload'),
      },
    },
    build: {
      rollupOptions: {
        external: ['electron'],
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
        '@': resolve(__dirname, './src'),
        '@components': resolve(__dirname, './src/components'),
        '@stores': resolve(__dirname, './src/stores'),
        '@views': resolve(__dirname, './src/views'),
        '@composables': resolve(__dirname, './src/composables'),
        '@assets': resolve(__dirname, './src/assets'),
      },
    },
    plugins: [vue(), tailwindcss()],
  },
});
