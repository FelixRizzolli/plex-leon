<template>
  <div class="flex flex-1 flex-col gap-4 p-4">
    <Card>
      <CardHeader>
        <CardTitle>API Tokens</CardTitle>
        <CardDescription>Manage your API tokens</CardDescription>
      </CardHeader>
      <CardContent>
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
      </CardContent>
      <CardFooter>
        <form @submit.prevent="save">
          <div class="flex justify-end w-full">
            <Button type="submit">Save</Button>
          </div>
        </form>
      </CardFooter>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Media Libraries</CardTitle>
        <CardDescription>Manage your media libraries</CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead> ID </TableHead>
              <TableHead> Name </TableHead>
              <TableHead> Type </TableHead>
              <TableHead> Path </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="lib in libraries" :key="lib.id">
              <TableCell class="font-medium">{{ lib.id }}</TableCell>
              <TableCell>{{ lib.name }}</TableCell>
              <TableCell>{{ lib.type }}</TableCell>
              <TableCell>{{ lib.path }}</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </CardContent>
      <CardFooter>
        <Dialog>
          <form>
            <DialogTrigger as-child>
              <Button variant="outline"> Open Dialog </Button>
            </DialogTrigger>
            <DialogContent class="sm:max-w-106.25">
              <DialogHeader>
                <DialogTitle>Add Media Library</DialogTitle>
                <DialogDescription>
                  Add a new media library here. Click save when you're done.
                </DialogDescription>
              </DialogHeader>
              <div class="grid gap-4">
                <div class="grid gap-3">
                  <Label for="name">Name</Label>
                  <Input id="name" name="name" default-value="" />
                </div>
                <div class="grid gap-3">
                  <Label for="type">Type</Label>
                  <Input id="type" name="type" default-value="" />
                </div>
                <div class="grid gap-3">
                  <Label for="path">Path</Label>
                  <Input id="path" name="path" default-value="" />
                </div>
              </div>
              <DialogFooter>
                <DialogClose as-child>
                  <Button variant="outline"> Cancel </Button>
                </DialogClose>
                <Button type="submit"> Save changes </Button>
              </DialogFooter>
            </DialogContent>
          </form>
        </Dialog>
      </CardFooter>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { ref, onMounted } from 'vue';

  import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
  } from '@/components/ui/card';
  import {
    Table,
    TableBody,
    TableCaption,
    TableCell,
    TableFooter,
    TableHead,
    TableHeader,
    TableRow,
  } from '@/components/ui/table';
  import {
    Dialog,
    DialogClose,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
  } from '@/components/ui/dialog';
  import { Input } from '@/components/ui/input';
  import { Label } from '@/components/ui/label';
  import { Button } from '@/components/ui/button';

  import { useI18n } from 'vue-i18n';
  const { t } = useI18n();

  const tvdb = ref<string>('');
  const tmdb = ref<string>('');

  type Library = {
    id: string;
    name: string;
    type: string;
    path: string;
  };

  const libraries = ref<Array<Library>>([]);

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
