<template>
  <div :style="style" class="color-container" />
</template>
<script setup lang="ts">
import { computed } from 'vue';

import { DEFAULT_COLOR_OPTIONS } from '@/config/color';

const panelColor =
  'conic-gradient(from 90deg at 50% 50%, #FF0000 -19.41deg, #FF0000 18.76deg, #FF8A00 59.32deg, #FFE600 99.87deg, #14FF00 141.65deg, #00A3FF 177.72deg, #0500FF 220.23deg, #AD00FF 260.13deg, #FF00C7 300.69deg, #FF0000 340.59deg, #FF0000 378.76deg)';

const { value } = defineProps({
  value: {
    type: String,
  },
});

const style = computed(() => {
  return {
    background: DEFAULT_COLOR_OPTIONS.indexOf(value) > -1 ? value : panelColor,
  };
});
</script>

<style lang="less" scoped>
.color-container {
  width: 24px;
  height: 24px;
  border-radius: var(--td-radius-circle);
  display: inline-block;
}
</style>
