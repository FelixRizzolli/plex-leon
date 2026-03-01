<template>
  <Sidebar collapsible="offcanvas">
    <SidebarHeader>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton as-child class="data-[slot=sidebar-menu-button]:p-1.5!">
            <a href="#">
              <IconBoltFilled class="size-5!" />
              <span class="text-base font-semibold">Leon v4</span>
            </a>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarHeader>
    <SidebarContent>
      <NavSection :items="data.navMain" />
      <NavSection :title="'Utilities'" :items="data.utilities" />
      <NavSection :items="data.navSecondary" class="mt-auto" />
    </SidebarContent>
    <SidebarFooter>
    </SidebarFooter>
  </Sidebar>
</template>

<script setup lang="ts">
  import {
    IconDashboard,
    IconHelp,
    IconBoltFilled,
    IconSettings,
    IconClipboardList,
    IconArrowsJoin,
    IconZoomCheck,
  } from '@tabler/icons-vue';

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
        title: 'Dashboard',
        url: '#',
        icon: IconDashboard,
      },
    ],
    utilities: [
      {
        title: 'Prepare',
        url: '#',
        icon: IconClipboardList,
      },
      {
        title: 'Migrate',
        url: '#',
        icon: IconArrowsJoin,
      },
      {
        title: 'Episode Check',
        url: '#',
        icon: IconZoomCheck,
      },
    ],
    navSecondary: [
      {
        title: 'Settings',
        url: '#',
        icon: IconSettings,
      },
      {
        title: 'Get Help',
        url: '#',
        icon: IconHelp,
      },
    ],
  };
</script>