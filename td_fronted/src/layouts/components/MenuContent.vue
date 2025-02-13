<template>
  <div>
    <template v-for="item in list" :key="item.path">
      <template v-if="!item.children || !item.children.length || item.meta?.single">
        <t-menu-item v-if="getHref(item)" :name="item.path" :value="getPath(item)" @click="openHref(getHref(item)[0])">
          <template #icon>
            <component :is="menuIcon(item)" class="t-icon"></component>
          </template>
          {{ renderMenuTitle(item.title) }}
        </t-menu-item>
        <t-menu-item v-else :name="item.path" :value="getPath(item)" :to="item.path">
          <template #icon>
            <component :is="menuIcon(item)" class="t-icon"></component>
          </template>
          {{ renderMenuTitle(item.title) }}
        </t-menu-item>
      </template>
      <t-submenu v-else :name="item.path" :value="item.path" :title="renderMenuTitle(item.title)">
        <template #icon>
          <component :is="menuIcon(item)" class="t-icon"></component>
        </template>
        <menu-content v-if="item.children" :nav-data="item.children" />
      </t-submenu>
    </template>
  </div>
</template>
<script setup lang="tsx">
import type { PropType } from 'vue';
import { computed } from 'vue';

import { useLocale } from '@/locales/useLocale';
import { getActive } from '@/router';
import type { MenuRoute } from '@/types/interface';

type ListItemType = MenuRoute & { icon?: string };

const { navData } = defineProps({
  navData: {
    type: Array as PropType<MenuRoute[]>,
    default: () => [],
  },
});

const active = computed(() => getActive());

const { locale } = useLocale();
const list = computed(() => {
  return getMenuList(navData);
});

const menuIcon = (item: ListItemType) => {
  if (typeof item.icon === 'string') return <t-icon name={item.icon} />;
  const RenderIcon = item.icon;
  return RenderIcon;
};

const renderMenuTitle = (title: string | Record<string, string>) => {
  if (typeof title === 'string') return title;
  return title[locale.value];
};

const getMenuList = (list: MenuRoute[], basePath?: string): ListItemType[] => {
  if (!list || list.length === 0) {
    return [];
  }
  // 如果meta中有orderNo则按照从小到大排序
  list.sort((a, b) => {
    return (a.meta?.orderNo || 0) - (b.meta?.orderNo || 0);
  });
  return list
    .map((item) => {
      const path = basePath && !item.path.includes(basePath) ? `${basePath}/${item.path}` : item.path;

      return {
        path,
        title: item.meta?.title,
        icon: item.meta?.icon,
        children: getMenuList(item.children, path),
        meta: item.meta,
        redirect: item.redirect,
      };
    })
    .filter((item) => item.meta && item.meta.hidden !== true);
};

const getHref = (item: MenuRoute) => {
  const { frameSrc, frameBlank } = item.meta;
  if (frameSrc && frameBlank) {
    return frameSrc.match(/(http|https):\/\/([\w.]+\/?)\S*/);
  }
  return null;
};

const getPath = (item: ListItemType) => {
  const activeLevel = active.value.split('/').length;
  const pathLevel = item.path.split('/').length;
  if (activeLevel > pathLevel && active.value.startsWith(item.path)) {
    return active.value;
  }

  if (active.value === item.path) {
    return active.value;
  }

  return item.meta?.single ? item.redirect : item.path;
};

const openHref = (url: string) => {
  window.open(url);
};
</script>
