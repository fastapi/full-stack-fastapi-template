<template>
  <result title="403 Forbidden" :tip="t('pages.result.403.tips')">
    <t-button @click="() => $router.push('/')">{{ t('pages.result.403.back') }}</t-button>
  </result>
</template>
<script lang="ts">
export default {
  name: 'Result403',
};
</script>
<script setup lang="ts">
import Result from '@/components/result/index.vue';
import { t } from '@/locales';
</script>
