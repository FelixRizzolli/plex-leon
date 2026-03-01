<template>
  <SidebarGroup class="group-data-[collapsible=icon]:hidden">
    <SidebarGroupLabel v-if="title">{{ title }}</SidebarGroupLabel>
    <SidebarMenu>
      <SidebarMenuItem v-for="item in items" :key="item.title">
        <SidebarMenuButton as-child>
          <a :href="item.url">
            <component :is="item.icon" v-if="item.icon" />
            {{ item.title }}
          </a>
        </SidebarMenuButton>
      </SidebarMenuItem>
    </SidebarMenu>
  </SidebarGroup>
</template>

<script setup lang="ts">
  import type { Component } from 'vue';

  import {
    SidebarGroup,
    SidebarGroupContent,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
  } from '@/components/ui/sidebar';

  interface NavItem {
    title: string;
    url: string;
    icon?: Component;
  }

  defineProps<{
    title: string;
    items: NavItem[];
  }>();
</script>