<template>
  <div class="flex flex-1 flex-col gap-4 p-4">
    <Card>
      <CardHeader>
        <CardTitle>API Tokens</CardTitle>
        <CardDescription>Manage your API tokens</CardDescription>
      </CardHeader>
      <CardContent>
        <form @submit.prevent="save">
          <div class="grid w-full items-center gap-4">
            <div class="flex flex-col space-y-1.5">
              <Label for="tvdb">TVDB API Token</Label>
              <Input id="tvdb" v-model="tvdb" />
            </div>
            <div class="flex flex-col space-y-1.5">
              <Label for="tmdb">TMDB API Token</Label>
              <Input id="tmdb" v-model="tmdb" />
            </div>
          </div>
          <CardFooter>
            <div class="flex justify-end w-full">
              <Button type="submit">Save</Button>
            </div>
          </CardFooter>
        </form>
      </CardContent>
    </Card>
    <Card>
      <CardHeader>
        <CardTitle>Media Libraries</CardTitle>
        <CardDescription>Manage your media libraries</CardDescription>
      </CardHeader>
      <CardContent>
        <!-- TODO: implement media libraries management -->
      </CardContent>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
  } from '@/components/ui/card';
  import { Input } from '@/components/ui/input';
  import { Label } from '@/components/ui/label';

  import { useI18n } from 'vue-i18n';
  const { t } = useI18n();
  
  import { ref, onMounted } from 'vue';
  import { Button } from '@/components/ui/button';

  const tvdb = ref<string>('');
  const tmdb = ref<string>('');

  async function loadSettings() {
    try {
      const v1 = await window.api.settings.get('tvdb');
      const v2 = await window.api.settings.get('tmdb');
      if (typeof v1 === 'string') tvdb.value = v1;
      if (typeof v2 === 'string') tmdb.value = v2;
    } catch (e) {
      // ignore
    }
  }

  async function save() {
    await window.api.settings.set('tvdb', tvdb.value);
    await window.api.settings.set('tmdb', tmdb.value);
  }

  onMounted(() => {
    loadSettings();
  });
</script>
