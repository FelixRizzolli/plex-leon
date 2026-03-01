<template>
  <Sidebar collapsible="offcanvas">
    <SidebarHeader>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton as-child class="data-[slot=sidebar-menu-button]:p-1.5!">
            <RouterLink to="/" class="flex items-center gap-2">
              <IconBoltFilled class="size-5!" />
              <span class="text-base font-semibold">Leon v4</span>
            </RouterLink>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarHeader>
    <SidebarContent>
      <NavSection :items="data.navMain" />
      <NavSection :title="'Utilities'" :items="data.utilities" />
      <NavSection :items="data.navSecondary" class="mt-auto" />
    </SidebarContent>
    <SidebarFooter> </SidebarFooter>
  </Sidebar>
</template>

<script setup lang="ts">
  import { useI18n } from 'vue-i18n';
  const { t } = useI18n();

  import {
    IconDashboard,
    IconHelp,
    IconBoltFilled,
    IconSettings,
    IconClipboardList,
    IconArrowsJoin,
    IconZoomCheck,
  } from '@tabler/icons-vue';

  import { RouterLink } from 'vue-router';
  import NavSection from '@/components/NavSection.vue';
  import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
  } from '@/components/ui/sidebar';

  const data = {
    user: {
      name: 'shadcn',
      email: 'm@example.com',
      avatar: '/avatars/shadcn.jpg',
    },
    navMain: [
      {
        title: t('dashboard.title'),
        url: '/',
        icon: IconDashboard,
      },
    ],
    utilities: [
      {
        title: t('utility.prepare.title'),
        url: '/utility/prepare',
        icon: IconClipboardList,
      },
      {
        title: t('utility.migrate.title'),
        url: '/utility/migrate',
        icon: IconArrowsJoin,
      },
      {
        title: t('utility.episodeCheck.title'),
        url: '/utility/episode-check',
        icon: IconZoomCheck,
      },
    ],
    navSecondary: [
      {
        title: t('settings.title'),
        url: '/settings',
        icon: IconSettings,
      },
      {
        title: t('help.title'),
        url: '/help',
        icon: IconHelp,
      },
    ],
  };
</script>
