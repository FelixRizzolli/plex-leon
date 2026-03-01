<template>
  <div class="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
    <h1 class="text-2xl font-bold tracking-tight">{{ t('utility.episode-check.title') }}</h1>
  </div>
</template>

<script setup lang="ts">
  import { useI18n } from 'vue-i18n';

  const { t } = useI18n();
</script>
