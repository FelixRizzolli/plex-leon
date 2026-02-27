<script setup lang="ts">
import { computed } from 'vue'

// ─── Props ────────────────────────────────────────────────────────────────────

interface Props {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const classes = computed(() => [
  'app-btn',
  `app-btn--${props.variant}`,
  `app-btn--${props.size}`,
  { 'app-btn--loading': props.loading },
])

function handleClick(e: MouseEvent): void {
  if (!props.disabled && !props.loading) emit('click', e)
}
</script>

<template>
  <button
    :class="classes"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="spinner" aria-hidden="true" />
    <slot />
  </button>
</template>

<style scoped>
.app-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: background var(--transition-fast), opacity var(--transition-fast);
  white-space: nowrap;
  user-select: none;
}

/* sizes */
.app-btn--sm  { padding: 4px 10px;  font-size: 12px; }
.app-btn--md  { padding: 8px 16px;  font-size: 13px; }
.app-btn--lg  { padding: 12px 22px; font-size: 15px; }

/* variants */
.app-btn--primary {
  background: var(--color-accent);
  color: #1a1a2e;
}
.app-btn--primary:hover { background: var(--color-accent-hover); }

.app-btn--secondary {
  background: var(--color-surface);
  border-color: var(--color-border);
  color: var(--color-text);
}
.app-btn--secondary:hover { background: var(--color-surface-hover); }

.app-btn--ghost {
  background: transparent;
  color: var(--color-text-muted);
}
.app-btn--ghost:hover { background: var(--color-surface-hover); color: var(--color-text); }

.app-btn--danger {
  background: var(--color-error);
  color: #fff;
}
.app-btn--danger:hover { opacity: 0.85; }

.app-btn:disabled { opacity: 0.45; cursor: not-allowed; }

/* spinner */
.spinner {
  width: 12px; height: 12px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
