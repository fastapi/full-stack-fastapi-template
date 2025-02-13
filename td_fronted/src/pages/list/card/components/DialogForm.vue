<template>
  <t-dialog v-model:visible="formVisible" :header="t('pages.listCard.create')" :width="680" :footer="false">
    <template #body>
      <!-- 表单内容 -->
      <t-form ref="form" :data="formData" :rules="rules" :label-width="100" @submit="onSubmit">
        <t-form-item :label="t('pages.listCard.productName')" name="name">
          <t-input v-model="formData.name" :style="{ width: '480px' }" />
        </t-form-item>
        <t-form-item :label="t('pages.listCard.productStatus')" name="status">
          <t-radio-group v-model="formData.status">
            <t-radio value="0">{{ t('pages.listCard.productStatusEnum.off') }}</t-radio>
            <t-radio value="1">{{ t('pages.listCard.productStatusEnum.on') }}</t-radio>
          </t-radio-group>
        </t-form-item>
        <t-form-item :label="t('pages.listCard.productDescription')" name="description">
          <t-input v-model="formData.description" :style="{ width: '480px' }" />
        </t-form-item>
        <t-form-item :label="t('pages.listCard.productType')" name="type">
          <t-select v-model="formData.type" clearable :style="{ width: '480px' }">
            <t-option v-for="(item, index) in SELECT_OPTIONS" :key="index" :value="item.value" :label="item.label">
              {{ item.label }}
            </t-option>
          </t-select>
        </t-form-item>
        <t-form-item :label="t('pages.listCard.productRemark')" name="mark">
          <t-textarea v-model="textareaValue" :style="{ width: '480px' }" name="description" />
        </t-form-item>
        <t-form-item style="float: right">
          <t-button variant="outline" @click="onClickCloseBtn">取消</t-button>
          <t-button theme="primary" type="submit">确定</t-button>
        </t-form-item>
      </t-form>
    </template>
  </t-dialog>
</template>

<script setup lang="ts">
import { FormRules, MessagePlugin, SubmitContext } from 'tdesign-vue-next';
import type { PropType } from 'vue';
import { ref, watch } from 'vue';

import { t } from '@/locales';

export interface FormData {
  name: string;
  status: string;
  description: string;
  type: string;
  mark: string;
  amount: number;
}

const INITIAL_DATA: FormData = {
  name: '',
  status: '',
  description: '',
  type: '',
  mark: '',
  amount: 0,
};

const SELECT_OPTIONS = [
  { label: '网关', value: '1' },
  { label: '人工智能', value: '2' },
  { label: 'CVM', value: '3' },
];

const { visible, data } = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  data: Object as PropType<FormData>,
});
const formVisible = ref(false);
const formData = ref({ ...INITIAL_DATA });
const textareaValue = ref('');

const onSubmit = ({ validateResult, firstError }: SubmitContext) => {
  if (!firstError) {
    MessagePlugin.success('提交成功');
    formVisible.value = false;
  } else {
    console.log('Errors: ', validateResult);
    MessagePlugin.warning(firstError);
  }
};

const onClickCloseBtn = () => {
  formVisible.value = false;
  formData.value = { ...INITIAL_DATA };
};

const emit = defineEmits(['update:visible']);
watch(
  () => formVisible.value,
  (val) => {
    emit('update:visible', val);
  },
);

watch(
  () => visible,
  (val) => {
    formVisible.value = val;
  },
);

watch(
  () => data,
  (val) => {
    formData.value = val;
  },
);

const rules: FormRules<FormData> = {
  name: [{ required: true, message: '请输入产品名称', type: 'error' }],
};
</script>
