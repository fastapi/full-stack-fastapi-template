<template>
  <result :title="t('pages.result.networkError.title')" :tip="t('pages.result.networkError.subtitle')" type="wifi">
    <div>
      <t-button theme="default" @click="() => $router.push('/')">{{ t('pages.result.networkError.back') }}</t-button>
      <t-button @click="() => $router.push('/')">{{ t('pages.result.networkError.reload') }}</t-button>
    </div>
  </result>
</template>

<script lang="ts">
export default {
  name: 'ResultNetworkError',
};
</script>
<script setup lang="ts">
import Result from '@/components/result/index.vue';
import { t } from '@/locales';
</script>
