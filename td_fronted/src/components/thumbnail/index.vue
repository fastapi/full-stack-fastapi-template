<template>
  <img :class="className" :src="url" />
</template>
<script setup lang="ts">
import { computed } from 'vue';

const { type } = defineProps({
  url: String,
  type: {
    type: String,
    default: 'layout',
  },
});

const className = computed(() => {
  return [
    'thumbnail-container',
    {
      'thumbnail-circle': type === 'circle',
      'thumbnail-layout': type === 'layout',
    },
  ];
});
</script>
<style lang="less" scoped>
@import '@/style/index.less';

.thumbnail {
  &-container {
    display: inline-block;
  }

  &-circle {
    border-radius: var(--td-radius-circle);
  }

  &-layout {
    width: 88px;
    height: 48px;
  }
}
</style>
