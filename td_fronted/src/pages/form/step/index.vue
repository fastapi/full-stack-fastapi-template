<template>
  <div>
    <div class="form-step-container">
      <!-- 简单步骤条 -->
      <t-card :bordered="false">
        <t-steps class="step-container" :current="1" status="process">
          <t-step-item :title="t('pages.formStep.step1.title')" :content="t('pages.formStep.step1.subtitle')" />
          <t-step-item :title="t('pages.formStep.step2.title')" :content="t('pages.formStep.step2.subtitle')" />
          <t-step-item :title="t('pages.formStep.step3.title')" :content="t('pages.formStep.step3.subtitle')" />
          <t-step-item :title="t('pages.formStep.step4.title')" :content="t('pages.formStep.step4.subtitle')" />
        </t-steps>
      </t-card>

      <!-- 分步表单1 -->
      <div v-show="activeForm === 0" class="rule-tips">
        <t-alert theme="info" :title="t('pages.formStep.step1.rules')" :close="true">
          <template #message>
            <p>
              {{ t('pages.formStep.step1.rule1') }}
            </p>
            <p>{{ t('pages.formStep.step1.rule2') }}</p>
            <p>{{ t('pages.formStep.step1.rule3') }}</p>
          </template>
        </t-alert>
      </div>
      <t-form
        v-show="activeForm === 0"
        class="step-form"
        :data="formData1"
        :rules="FORM_RULES"
        label-align="right"
        @submit="(result: SubmitContext) => onSubmit(result, 1)"
      >
        <t-form-item :label="t('pages.formStep.step1.contractName')" name="name">
          <t-select v-model="formData1.name" :style="{ width: '480px' }" class="demo-select-base" clearable>
            <t-option v-for="(item, index) in NAME_OPTIONS" :key="index" :value="item.value" :label="item.label">
              {{ item.label }}
            </t-option>
          </t-select>
        </t-form-item>
        <t-form-item :label="t('pages.formStep.step1.invoiceType')" name="type">
          <t-select v-model="formData1.type" :style="{ width: '480px' }" class="demo-select-base" clearable>
            <t-option v-for="(item, index) in TYPE_OPTIONS" :key="index" :value="item.value" :label="item.label">
              {{ item.label }}
            </t-option>
          </t-select>
        </t-form-item>
        <t-form-item :label="t('pages.formStep.step1.amount')"> ¥ {{ amount }} </t-form-item>
        <t-form-item>
          <t-button theme="primary" type="submit"> {{ t('pages.formStep.step1.submit') }} </t-button>
        </t-form-item>
      </t-form>

      <!-- 分步表单2 -->
      <t-form
        v-show="activeForm === 1"
        class="step-form"
        :data="formData2"
        :rules="FORM_RULES"
        label-align="left"
        @reset="onReset(0)"
        @submit="(result: SubmitContext) => onSubmit(result, 2)"
      >
        <t-form-item :label="t('pages.formStep.step2.invoiceTitle')" name="title">
          <t-input
            v-model="formData2.title"
            :style="{ width: '480px' }"
            :placeholder="t('pages.formStep.step2.invoiceTitlePlaceholder')"
          />
        </t-form-item>
        <t-form-item :label="t('pages.formStep.step2.taxNum')" name="taxNum">
          <t-input
            v-model="formData2.taxNum"
            :style="{ width: '480px' }"
            :placeholder="t('pages.formStep.step2.taxNumPlaceholder')"
          />
        </t-form-item>
        <t-form-item :label="t('pages.formStep.step2.address')" name="address">
          <t-input
            v-model="formData2.address"
            :style="{ width: '480px' }"
            :placeholder="t('pages.formStep.step2.addressPlaceholder')"
          />
        </t-form-item>
        <t-form-item :label="t('pages.formStep.step2.bank')" name="bank">
          <t-input
            v-model="formData2.bank"
            :style="{ width: '480px' }"
            :placeholder="t('pages.formStep.step2.bankPlaceholder')"
          />
        </t-form-item>
        <t-form-item :label="t('pages.formStep.step2.bankAccount')" name="bankAccount">
          <t-input
            v-model="formData2.bankAccount"
            :style="{ width: '480px' }"
            :placeholder="t('pages.formStep.step2.bankAccountPlaceholder')"
          />
        </t-form-item>
        <t-form-item :label="t('pages.formStep.step2.email')" name="email">
          <t-input
            v-model="formData2.email"
            :style="{ width: '480px' }"
            :placeholder="t('pages.formStep.step2.emailPlaceholder')"
          />
        </t-form-item>
        <t-form-item :label="t('pages.formStep.step2.tel')" name="tel">
          <t-input
            v-model="formData2.tel"
            :style="{ width: '480px' }"
            :placeholder="t('pages.formStep.step2.telPlaceholder')"
          />
        </t-form-item>
        <t-form-item>
          <t-button type="reset" theme="default" variant="base"> {{ t('pages.formStep.preStep') }} </t-button>
          <t-button theme="primary" type="submit"> {{ t('pages.formStep.nextStep') }} </t-button>
        </t-form-item>
      </t-form>

      <!-- 分步表单3 -->
      <t-form
        v-show="activeForm === 2"
        class="step-form"
        :data="formData3"
        :rules="FORM_RULES"
        label-align="left"
        @reset="onReset(1)"
        @submit="(result: SubmitContext) => onSubmit(result, 6)"
      >
        <t-form-item :label="t('pages.formStep.step3.consignee')" name="consignee">
          <t-input v-model="formData3.consignee" :style="{ width: '480px' }" />
        </t-form-item>
        <t-form-item :label="t('pages.formStep.step3.mobileNum')" name="mobileNum">
          <t-input v-model="formData3.mobileNum" :style="{ width: '480px' }" />
        </t-form-item>
        <t-form-item :label="t('pages.formStep.step3.deliveryAddress')" name="deliveryAddress">
          <t-select v-model="formData3.deliveryAddress" :style="{ width: '480px' }" class="demo-select-base" clearable>
            <t-option v-for="(item, index) in ADDRESS_OPTIONS" :key="index" :value="item.value" :label="item.label">
              {{ item.label }}
            </t-option>
          </t-select>
        </t-form-item>
        <t-form-item :label="t('pages.formStep.step3.fullAddress')" name="fullAddress">
          <t-textarea v-model="formData3.fullAddress" :style="{ width: '480px' }" />
        </t-form-item>
        <t-form-item>
          <t-button type="reset" theme="default" variant="base"> {{ t('pages.formStep.preStep') }} </t-button>
          <t-button theme="primary" type="submit"> {{ t('pages.formStep.nextStep') }} </t-button>
        </t-form-item>
      </t-form>

      <!-- 分步表单4 -->
      <div v-show="activeForm === 6" class="step-form-4">
        <t-space direction="vertical" style="align-items: center">
          <t-icon name="check-circle-filled" style="color: green" size="52px" />
          <p class="text">{{ t('pages.formStep.step4.finishTitle') }}</p>
          <p class="tips">{{ t('pages.formStep.step4.finishTips') }}</p>
          <div class="button-group">
            <t-button theme="primary" @click="onReset(0)"> {{ t('pages.formStep.step4.reapply') }} </t-button>
            <t-button variant="base" theme="default" @click="complete">
              {{ t('pages.formStep.step4.check') }}
            </t-button>
          </div>
        </t-space>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
export default {
  name: 'FormStep',
};
</script>

<script setup lang="ts">
import { SubmitContext } from 'tdesign-vue-next';
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';

import { t } from '@/locales';

import {
  ADDRESS_OPTIONS,
  FORM_RULES,
  INITIAL_DATA1,
  INITIAL_DATA2,
  INITIAL_DATA3,
  NAME_OPTIONS,
  TYPE_OPTIONS,
} from './constants';

const formData1 = ref({ ...INITIAL_DATA1 });
const formData2 = ref({ ...INITIAL_DATA2 });
const formData3 = ref({ ...INITIAL_DATA3 });
const activeForm = ref(0);

const amount = computed(() => {
  if (formData1.value.name === '1') {
    return '565421';
  }
  if (formData1.value.name === '2') {
    return '278821';
  }
  if (formData1.value.name === '3') {
    return '109824';
  }
  return '--';
});

const onSubmit = (result: SubmitContext, val: number) => {
  if (result.validateResult === true) {
    activeForm.value = val;
  }
};
const onReset = (val: number) => {
  activeForm.value = val;
};
const complete = () => {
  const router = useRouter();
  router.replace({ path: '/detail/advanced' });
};
</script>

<style lang="less" scoped>
@import './index.less';
</style>
