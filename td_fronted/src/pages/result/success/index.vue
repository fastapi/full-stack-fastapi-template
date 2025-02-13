<template>
  <div class="result-success">
    <t-icon class="result-success-icon" name="check-circle" />
    <div class="result-success-title">{{ t('pages.result.success.title') }}</div>
    <div class="result-success-describe">{{ t('pages.result.success.subtitle') }}</div>
    <div>
      <t-button theme="default" @click="() => $router.push('/detail/advanced')">
        {{ t('pages.result.success.progress') }}
      </t-button>
      <t-button @click="() => $router.push('/dashboard/base')"> {{ t('pages.result.success.back') }} </t-button>
    </div>
  </div>
</template>
<script lang="ts">
export default {
  name: 'ResultSuccess',
};
</script>

<script setup lang="ts">
import { t } from '@/locales';
</script>

<style lang="less" scoped>
.result-success {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 75vh;

  &-icon {
    font-size: var(--td-comp-size-xxxxl);
    color: var(--td-success-color);
  }

  &-title {
    margin-top: var(--td-comp-margin-xxl);
    font: var(--td-font-title-large);
    color: var(--td-text-color-primary);
    text-align: center;
  }

  &-describe {
    margin: var(--td-comp-margin-s) 0 var(--td-comp-margin-xxxl);
    font: var(--td-font-body-medium);
    color: var(--td-text-color-secondary);
  }
}
</style>
