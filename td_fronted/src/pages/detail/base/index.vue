<template>
  <div class="detail-base">
    <t-card :bordered="false">
      <t-descriptions :title="t('pages.detailBase.baseInfo.title')">
        <t-descriptions-item v-for="(item, index) in BASE_INFO_DATA" :key="index" :label="item.name">
          <span
            :class="{
              ['inProgress']: item.type && item.type.value === 'inProgress',
              ['pdf']: item.type && item.type.value === 'pdf',
            }"
          >
            <i v-if="item.type && item.type.key === 'contractStatus'" />
            {{ item.value }}
          </span>
        </t-descriptions-item>
      </t-descriptions>
    </t-card>

    <t-card :title="t('pages.detailBase.changelog.title')" class="container-base-margin-top" :bordered="false">
      <t-steps class="detail-base-info-steps" layout="vertical" theme="dot" :current="1">
        <t-step-item
          :title="t('pages.detailBase.changelog.step1.title')"
          :content="t('pages.detailBase.changelog.step1.subtitle')"
        />
        <t-step-item
          :title="t('pages.detailBase.changelog.step2.title')"
          :content="t('pages.detailBase.changelog.step2.subtitle')"
        />
        <t-step-item
          :title="t('pages.detailBase.changelog.step3.title')"
          :content="t('pages.detailBase.changelog.step3.desc')"
        />
      </t-steps>
    </t-card>
  </div>
</template>

<script lang="ts">
export default {
  name: 'DetailBase',
};
</script>

<script setup lang="ts">
import { t } from '@/locales';

const BASE_INFO_DATA = [
  {
    name: t('constants.contract.name'),
    value: '总部办公用品采购项目',
    type: null,
  },
  {
    name: t('constants.contract.status'),
    value: '履行中',
    type: {
      key: 'contractStatus',
      value: 'inProgress',
    },
  },
  {
    name: t('constants.contract.num'),
    value: 'BH00010',
    type: null,
  },
  {
    name: t('constants.contract.type'),
    value: t('constants.contract.typeOptions.main'),
    type: null,
  },
  {
    name: t('constants.contract.payType'),
    value: t('constants.contract.pay'),
    type: null,
  },
  {
    name: t('constants.contract.amount'),
    value: '¥ 5,000,000',
    type: null,
  },
  {
    name: t('constants.contract.company'),
    value: '腾讯科技（深圳）有限公司',
    type: null,
  },
  {
    name: t('constants.contract.employee'),
    value: '欧尚',
    type: null,
  },
  {
    name: t('constants.contract.signDate'),
    value: '2020-12-20',
    type: null,
  },
  {
    name: t('constants.contract.effectiveDate'),
    value: '2021-01-20',
    type: null,
  },
  {
    name: t('constants.contract.endDate'),
    value: '2022-12-20',
    type: null,
  },
  {
    name: t('constants.contract.attachment'),
    value: '总部办公用品采购项目合同.pdf',
    type: {
      key: 'contractAnnex',
      value: 'pdf',
    },
  },
  {
    name: t('constants.contract.createDate'),
    value: '2020-12-22 10:00:00',
    type: null,
  },
];
</script>

<style lang="less" scoped>
@import './index.less';
</style>
