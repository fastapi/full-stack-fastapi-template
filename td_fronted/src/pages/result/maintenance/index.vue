<template>
  <result :title="t('pages.result.maintenance.title')" :tip="t('pages.result.maintenance.subtitle')" type="maintenance">
    <t-button theme="primary" @click="() => $router.push('/')">{{ t('pages.result.maintenance.back') }}</t-button>
  </result>
</template>

<script lang="ts">
export default {
  name: 'ResultMaintenance',
};
</script>
<script setup lang="ts">
import Result from '@/components/result/index.vue';
import { t } from '@/locales';
</script>
