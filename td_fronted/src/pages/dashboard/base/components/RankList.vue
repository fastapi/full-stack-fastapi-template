<template>
  <t-row :gutter="16" class="row-container">
    <t-col :xs="12" :xl="6">
      <t-card :title="t('pages.dashboardBase.rankList.title')" class="dashboard-rank-card" :bordered="false">
        <template #actions>
          <t-radio-group default-value="dateVal" variant="default-filled">
            <t-radio-button value="dateVal">{{ t('pages.dashboardBase.rankList.week') }}</t-radio-button>
            <t-radio-button value="monthVal">{{ t('pages.dashboardBase.rankList.month') }}</t-radio-button>
          </t-radio-group>
        </template>
        <t-table :data="SALE_TEND_LIST" :columns="SALE_COLUMNS" row-key="productName">
          <template #index="{ rowIndex }">
            <span :class="getRankClass(rowIndex)">
              {{ rowIndex + 1 }}
            </span>
          </template>
          <template #growUp="{ row }">
            <span>
              <trend :type="row.growUp > 0 ? 'up' : 'down'" :describe="Math.abs(row.growUp)" />
            </span>
          </template>
          <template #operation="slotProps">
            <t-link theme="primary" @click="rehandleClickOp(slotProps)">{{
              t('pages.dashboardBase.rankList.info')
            }}</t-link>
          </template>
        </t-table>
      </t-card>
    </t-col>
    <t-col :xs="12" :xl="6">
      <t-card :title="t('pages.dashboardBase.rankList.title')" class="dashboard-rank-card" :bordered="false">
        <template #actions>
          <t-radio-group default-value="dateVal" variant="default-filled">
            <t-radio-button value="dateVal">{{ t('pages.dashboardBase.rankList.week') }}</t-radio-button>
            <t-radio-button value="monthVal">{{ t('pages.dashboardBase.rankList.month') }}</t-radio-button>
          </t-radio-group>
        </template>
        <t-table :data="BUY_TEND_LIST" :columns="BUY_COLUMNS" row-key="productName">
          <template #index="{ rowIndex }">
            <span :class="getRankClass(rowIndex)">
              {{ rowIndex + 1 }}
            </span>
          </template>
          <template #growUp="{ row }">
            <trend :type="row.growUp > 0 ? 'up' : 'down'" :describe="Math.abs(row.growUp)" />
          </template>
          <template #operation="slotProps">
            <t-link theme="primary" @click="rehandleClickOp(slotProps)">{{
              t('pages.dashboardBase.rankList.info')
            }}</t-link>
          </template>
        </t-table>
      </t-card>
    </t-col>
  </t-row>
</template>

<script setup lang="ts">
import type { TdBaseTableProps } from 'tdesign-vue-next';

import Trend from '@/components/trend/index.vue';
import { t } from '@/locales';

import { BUY_TEND_LIST, SALE_TEND_LIST } from '../constants';

const SALE_COLUMNS: TdBaseTableProps['columns'] = [
  {
    align: 'center',
    colKey: 'index',
    title: t('pages.dashboardBase.saleColumns.index'),
    width: 70,
    fixed: 'left',
  },
  {
    align: 'left',
    ellipsis: true,
    colKey: 'productName',
    title: t('pages.dashboardBase.saleColumns.productName'),
    width: 150,
  },
  {
    align: 'center',
    colKey: 'growUp',
    width: 70,
    title: t('pages.dashboardBase.saleColumns.growUp'),
  },
  {
    align: 'center',
    colKey: 'count',
    title: t('pages.dashboardBase.saleColumns.count'),
    width: 70,
  },
  {
    align: 'center',
    colKey: 'operation',
    title: t('pages.dashboardBase.saleColumns.operation'),
    width: 70,
    fixed: 'right',
  },
];

const BUY_COLUMNS: TdBaseTableProps['columns'] = [
  {
    align: 'center',
    colKey: 'index',
    title: t('pages.dashboardBase.buyColumns.index'),
    width: 70,
    fixed: 'left',
  },
  {
    align: 'left',
    ellipsis: true,
    colKey: 'productName',
    width: 150,
    title: t('pages.dashboardBase.buyColumns.productName'),
  },
  {
    align: 'center',
    colKey: 'growUp',
    width: 70,
    title: t('pages.dashboardBase.buyColumns.growUp'),
  },
  {
    align: 'center',
    colKey: 'count',
    title: t('pages.dashboardBase.buyColumns.count'),
    width: 70,
  },
  {
    align: 'center',
    colKey: 'operation',
    title: t('pages.dashboardBase.buyColumns.operation'),
    width: 70,
    fixed: 'right',
  },
];

const rehandleClickOp = (val: MouseEvent) => {
  console.log(val);
};
const getRankClass = (index: number) => {
  return ['dashboard-rank', { 'dashboard-rank__top': index < 3 }];
};
</script>

<style lang="less" scoped>
.dashboard-rank-card {
  padding: var(--td-comp-paddingTB-xxl) var(--td-comp-paddingLR-xxl);

  :deep(.t-card__header) {
    padding: 0;
  }

  :deep(.t-card__title) {
    font: var(--td-font-title-large);
    font-weight: 400;
  }

  :deep(.t-card__body) {
    padding: 0;
    margin-top: var(--td-comp-margin-xxl);
  }
}

.dashboard-rank__cell {
  display: inline-flex;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  color: white;
  font-size: 14px;
  background-color: var(--td-gray-color-5);
  align-items: center;
  justify-content: center;
  font-weight: 700;

  &--top {
    background: var(--td-brand-color);
  }
}
</style>
