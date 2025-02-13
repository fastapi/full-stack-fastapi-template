<template>
  <div class="detail-advanced">
    <t-card :bordered="false">
      <t-descriptions :title="t('pages.detailCard.baseInfo.title')">
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

    <!-- 发票进度 -->
    <t-card :title="t('pages.detailCard.invoice.title')" class="container-base-margin-top" :bordered="false">
      <t-row justify="space-between">
        <t-steps :current="updateCurrent">
          <t-step-item
            :title="t('pages.detailCard.invoice.step1.title')"
            :content="t('pages.detailCard.invoice.step1.content')"
          />
          <t-step-item
            :title="t('pages.detailCard.invoice.step2.title')"
            :content="t('pages.detailCard.invoice.step2.content')"
          />
          <t-step-item
            :title="t('pages.detailCard.invoice.step3.title')"
            :content="t('pages.detailCard.invoice.step3.content')"
          />
          <t-step-item :title="t('pages.detailCard.invoice.step4.title')" />
        </t-steps>
      </t-row>
    </t-card>

    <!-- 产品目录 -->
    <t-card :title="t('pages.detailCard.product.title')" class="container-base-margin-top" :bordered="false">
      <template #actions>
        <t-radio-group default-value="dateVal">
          <t-radio-button value="dateVal"> {{ t('pages.detailCard.product.quarter') }} </t-radio-button>
          <t-radio-button value="monthVal"> {{ t('pages.detailCard.product.month') }} </t-radio-button>
        </t-radio-group>
      </template>
      <t-row :gutter="16" class="product-block-container">
        <t-col :xl="4">
          <div class="product-add">
            <div class="product-sub">
              <t-icon name="add" class="product-sub-icon" />
              <span>{{ t('pages.detailCard.product.add') }}</span>
            </div>
          </div>
        </t-col>
        <t-col v-for="(item, index) in PRODUCT_LIST" :key="index" :xl="4">
          <product :data="item" />
        </t-col>
      </t-row>
    </t-card>

    <!-- 产品采购明细 -->
    <t-card :title="t('pages.detailCard.detail.title')" class="container-base-margin-top" :bordered="false">
      <t-table
        :columns="columns"
        :data="data"
        :pagination="pagination"
        :hover="true"
        :stripe="true"
        row-key="index"
        size="large"
        @sort-change="sortChange"
        @change="rehandleChange"
      >
        <template #pdName="{ row }">
          <span>
            {{ row.pdName }}
            <t-tag v-if="row.pdType" size="medium" style="margin-left: var(--td-comp-margin-s)">{{ row.pdType }}</t-tag>
          </span>
        </template>

        <template #purchaseNum="{ row }">
          <span>
            {{ row.purchaseNum }}
            <t-tag
              v-if="row.purchaseNum > 50"
              theme="danger"
              variant="light"
              size="medium"
              style="margin-left: var(--td-comp-margin-s)"
              >超预算</t-tag
            >
          </span>
        </template>

        <template #op="slotProps">
          <t-space>
            <t-link theme="primary" @click="listClick()">{{ t('pages.detailCard.detail.form.manage') }}</t-link>
            <t-link theme="danger" @click="deleteClickOp(slotProps)">{{
              t('pages.detailCard.detail.form.delete')
            }}</t-link>
          </t-space>
        </template>

        <template #op-column>
          <t-icon name="descending-order" />
        </template>
      </t-table>
    </t-card>

    <t-dialog v-model:visible="visible" :header="t('pages.detailCard.baseInfo.title')" @confirm="onConfirm">
      <template #body>
        <div class="dialog-info-block">
          <t-descriptions :column="1">
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
        </div>
      </template>
    </t-dialog>
  </div>
</template>

<script lang="ts">
export default {
  name: 'DetailAdvanced',
};
</script>

<script setup lang="ts">
import { onMounted, ref } from 'vue';

import { getPurchaseList } from '@/api/detail';
import { t } from '@/locales';

import Product from './components/Product.vue';
import { BASE_INFO_DATA, PRODUCT_LIST } from './constants';

const columns = [
  {
    width: 280,
    ellipsis: true,
    colKey: 'index',
    title: t('pages.detailCard.detail.form.applyNo'),
    sorter: (a: any, b: any) => a.index.substr(3) - b.index.substr(3),
  },
  {
    width: 200,
    ellipsis: true,
    colKey: 'pdName',
    title: t('pages.detailCard.detail.form.product'),
    sorter: (a: any, b: any) => a.pdName.length - b.pdName.length,
  },
  {
    width: 200,
    ellipsis: true,
    colKey: 'pdNum',
    title: t('pages.detailCard.detail.form.productNo'),
  },
  {
    width: 160,
    ellipsis: true,
    colKey: 'purchaseNum',
    title: t('pages.detailCard.detail.form.num'),
    sorter: (a: any, b: any) => a.purchaseNum - b.purchaseNum,
  },
  {
    width: 160,
    ellipsis: true,
    colKey: 'adminName',
    title: t('pages.detailCard.detail.form.department'),
  },
  {
    width: 200,
    ellipsis: true,
    colKey: 'updateTime',
    title: t('pages.detailCard.detail.form.createTime'),
    sorter: (a: any, b: any) => Date.parse(a.updateTime) - Date.parse(b.updateTime),
  },
  {
    align: 'left' as const,
    fixed: 'right' as const,
    width: 200,
    className: 'test2',
    colKey: 'op',
    title: t('pages.detailCard.detail.form.operation'),
  },
];

const data = ref([]);
const pagination = ref({
  defaultPageSize: 10,
  total: 100,
  defaultCurrent: 1,
});

const updateCurrent = ref(0);

const stepUpdate = () => {
  setInterval(() => {
    if (updateCurrent.value > 5) {
      updateCurrent.value = -1;
    }
    updateCurrent.value += 1;
  }, 2000);
};

const fetchData = async () => {
  try {
    const { list } = await getPurchaseList();
    data.value = list;
    pagination.value = {
      ...pagination.value,
      total: list.length,
    };
  } catch (e) {
    console.log(e);
  }
};

onMounted(() => {
  stepUpdate();
  fetchData();
});

const visible = ref(false);
const sortChange = (val: unknown) => {
  console.log(val);
};
const rehandleChange = (changeParams: unknown, triggerAndData: unknown) => {
  console.log('统一Change', changeParams, triggerAndData);
};
const listClick = () => {
  visible.value = true;
};
const deleteClickOp = (columns: { rowIndex: number }) => {
  data.value.splice(columns.rowIndex, 1);
};
const onConfirm = () => {
  visible.value = false;
};
</script>

<style lang="less" scoped>
@import './index.less';
</style>
