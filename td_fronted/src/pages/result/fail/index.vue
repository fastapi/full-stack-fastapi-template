<template>
  <div class="result-success">
    <t-icon class="result-success-icon" name="error-circle" />
    <div class="result-success-title">{{ t('pages.result.fail.title') }}</div>
    <div class="result-success-describe">{{ t('pages.result.fail.subtitle') }}</div>
    <div>
      <t-button theme="default" @click="() => $router.push('/dashboard/base')">{{
        t('pages.result.fail.back')
      }}</t-button>
      <t-button @click="() => $router.push('/form/base')">{{ t('pages.result.fail.modify') }} </t-button>
    </div>
  </div>
</template>
<script lang="ts">
export default {
  name: 'ResultFail',
};
</script>

<script lang="ts" setup>
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
    color: var(--td-text-color-secondary);
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
