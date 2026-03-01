<template>
  <header
    class="flex h-(--header-height) shrink-0 items-center gap-2 border-b transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-(--header-height)"
  >
    <div class="flex w-full items-center gap-1 px-4 lg:gap-2 lg:px-6">
      <SidebarTrigger class="-ml-1" />
      <Separator orientation="vertical" class="mx-2 data-[orientation=vertical]:h-4" />
      <h1 class="text-base font-medium">Documents</h1>
      <div class="ml-auto flex items-center gap-2">
        <Button variant="ghost" size="icon" class="h-7 w-7" @click="appStore.toggleTheme()">
          <Sun v-if="appStore.isDark" class="size-4" />
          <Moon v-else class="size-4" />
          <span class="sr-only">Toggle theme</span>
        </Button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
  import { Moon, Sun } from 'lucide-vue-next';
  import { Button } from '@/components/ui/button';
  import { Separator } from '@/components/ui/separator';
  import { SidebarTrigger } from '@/components/ui/sidebar';
  import { useAppStore } from '@/stores/app';

  const appStore = useAppStore();
</script>