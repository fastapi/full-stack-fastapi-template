<template>
  <div>
    <t-card class="list-card-container" :bordered="false">
      <t-row justify="space-between">
        <div class="left-operation-container">
          <t-button @click="handleSetupContract"> {{ t('pages.listBase.create') }} </t-button>
          <t-button variant="base" theme="default" :disabled="!selectedRowKeys.length">
            {{ t('pages.listBase.export') }}</t-button
          >
          <p v-if="!!selectedRowKeys.length" class="selected-count">
            {{ t('pages.listBase.select') }} {{ selectedRowKeys.length }} {{ t('pages.listBase.items') }}
          </p>
        </div>
        <div class="search-input">
          <t-input v-model="searchValue" :placeholder="t('pages.listBase.placeholder')" clearable>
            <template #suffix-icon>
              <search-icon size="16px" />
            </template>
          </t-input>
        </div>
      </t-row>
      <t-table
        :data="data"
        :columns="COLUMNS"
        :row-key="rowKey"
        vertical-align="top"
        :hover="true"
        :pagination="pagination"
        :selected-row-keys="selectedRowKeys"
        :loading="dataLoading"
        :header-affixed-top="headerAffixedTop"
        @page-change="rehandlePageChange"
        @change="rehandleChange"
        @select-change="(value: number[]) => rehandleSelectChange(value)"
      >
        <template #status="{ row }">
          <t-tag v-if="row.status === CONTRACT_STATUS.FAIL" theme="danger" variant="light">
            {{ t('pages.listBase.contractStatusEnum.fail') }}</t-tag
          >
          <t-tag v-if="row.status === CONTRACT_STATUS.AUDIT_PENDING" theme="warning" variant="light">
            {{ t('pages.listBase.contractStatusEnum.audit') }}
          </t-tag>
          <t-tag v-if="row.status === CONTRACT_STATUS.EXEC_PENDING" theme="warning" variant="light">
            {{ t('pages.listBase.contractStatusEnum.pending') }}
          </t-tag>
          <t-tag v-if="row.status === CONTRACT_STATUS.EXECUTING" theme="success" variant="light">
            {{ t('pages.listBase.contractStatusEnum.executing') }}
          </t-tag>
          <t-tag v-if="row.status === CONTRACT_STATUS.FINISH" theme="success" variant="light">
            {{ t('pages.listBase.contractStatusEnum.finish') }}
          </t-tag>
        </template>
        <template #contractType="{ row }">
          <p v-if="row.contractType === CONTRACT_TYPES.MAIN">{{ t('pages.listBase.contractStatusEnum.fail') }}</p>
          <p v-if="row.contractType === CONTRACT_TYPES.SUB">{{ t('pages.listBase.contractStatusEnum.audit') }}</p>
          <p v-if="row.contractType === CONTRACT_TYPES.SUPPLEMENT">
            {{ t('pages.listBase.contractStatusEnum.pending') }}
          </p>
        </template>
        <template #paymentType="{ row }">
          <div v-if="row.paymentType === CONTRACT_PAYMENT_TYPES.PAYMENT" class="payment-col">
            {{ t('pages.listBase.pay') }}<trend class="dashboard-item-trend" type="up" />
          </div>
          <div v-if="row.paymentType === CONTRACT_PAYMENT_TYPES.RECEIPT" class="payment-col">
            {{ t('pages.listBase.receive') }}<trend class="dashboard-item-trend" type="down" />
          </div>
        </template>

        <template #op="slotProps">
          <t-space>
            <t-link theme="primary" @click="handleClickDetail()"> {{ t('pages.listBase.detail') }}</t-link>
            <t-link theme="danger" @click="handleClickDelete(slotProps)"> {{ t('pages.listBase.delete') }}</t-link>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <t-dialog
      v-model:visible="confirmVisible"
      header="确认删除当前所选合同？"
      :body="confirmBody"
      :on-cancel="onCancel"
      @confirm="onConfirmDelete"
    />
  </div>
</template>

<script lang="ts">
export default {
  name: 'ListBase',
};
</script>

<script setup lang="ts">
import { SearchIcon } from 'tdesign-icons-vue-next';
import { MessagePlugin, PrimaryTableCol, TableRowData } from 'tdesign-vue-next';
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';

import { getList } from '@/api/list';
import Trend from '@/components/trend/index.vue';
import { prefix } from '@/config/global';
import { CONTRACT_PAYMENT_TYPES, CONTRACT_STATUS, CONTRACT_TYPES } from '@/constants';
import { t } from '@/locales';
import { useSettingStore } from '@/store';

const store = useSettingStore();

const COLUMNS: PrimaryTableCol<TableRowData>[] = [
  { colKey: 'row-select', type: 'multiple', width: 64, fixed: 'left' },
  {
    title: t('pages.listBase.contractName'),
    align: 'left',
    width: 320,
    colKey: 'name',
    fixed: 'left',
  },
  { title: t('pages.listBase.contractStatus'), colKey: 'status', width: 160 },
  {
    title: t('pages.listBase.contractNum'),
    width: 160,
    ellipsis: true,
    colKey: 'no',
  },
  {
    title: t('pages.listBase.contractType'),
    width: 160,
    ellipsis: true,
    colKey: 'contractType',
  },
  {
    title: t('pages.listBase.contractPayType'),
    width: 160,
    ellipsis: true,
    colKey: 'paymentType',
  },
  {
    title: t('pages.listBase.contractAmount'),
    width: 160,
    ellipsis: true,
    colKey: 'amount',
  },
  {
    title: t('pages.listBase.operation'),
    align: 'left',
    fixed: 'right',
    width: 160,
    colKey: 'op',
  },
];

const data = ref([]);
const pagination = ref({
  defaultPageSize: 20,
  total: 100,
  defaultCurrent: 1,
});

const searchValue = ref('');

const dataLoading = ref(false);
const fetchData = async () => {
  dataLoading.value = true;
  try {
    const { list } = await getList();
    data.value = list;
    pagination.value = {
      ...pagination.value,
      total: list.length,
    };
  } catch (e) {
    console.log(e);
  } finally {
    dataLoading.value = false;
  }
};

const deleteIdx = ref(-1);
const confirmBody = computed(() => {
  if (deleteIdx.value > -1) {
    const { name } = data.value[deleteIdx.value];
    return `删除后，${name}的所有合同信息将被清空，且无法恢复`;
  }
  return '';
});

onMounted(() => {
  fetchData();
});

const confirmVisible = ref(false);

const selectedRowKeys = ref([1, 2]);

const router = useRouter();

const resetIdx = () => {
  deleteIdx.value = -1;
};

const onConfirmDelete = () => {
  // 真实业务请发起请求
  data.value.splice(deleteIdx.value, 1);
  pagination.value.total = data.value.length;
  const selectedIdx = selectedRowKeys.value.indexOf(deleteIdx.value);
  if (selectedIdx > -1) {
    selectedRowKeys.value.splice(selectedIdx, 1);
  }
  confirmVisible.value = false;
  MessagePlugin.success('删除成功');
  resetIdx();
};

const onCancel = () => {
  resetIdx();
};

const rowKey = 'index';

const rehandleSelectChange = (val: number[]) => {
  selectedRowKeys.value = val;
};
const rehandlePageChange = (curr: unknown, pageInfo: unknown) => {
  console.log('分页变化', curr, pageInfo);
};
const rehandleChange = (changeParams: unknown, triggerAndData: unknown) => {
  console.log('统一Change', changeParams, triggerAndData);
};
const handleClickDetail = () => {
  router.push('/detail/base');
};
const handleSetupContract = () => {
  router.push('/form/base');
};
const handleClickDelete = (row: { rowIndex: any }) => {
  deleteIdx.value = row.rowIndex;
  confirmVisible.value = true;
};

const headerAffixedTop = computed(
  () =>
    ({
      offsetTop: store.isUseTabsRouter ? 48 : 0,
      container: `.${prefix}-layout`,
    }) as any,
);
</script>

<style lang="less" scoped>
.payment-col {
  display: flex;

  .trend-container {
    display: flex;
    align-items: center;
    margin-left: var(--td-comp-margin-s);
  }
}

.list-card-container {
  padding: var(--td-comp-paddingTB-xxl) var(--td-comp-paddingLR-xxl);

  :deep(.t-card__body) {
    padding: 0;
  }
}

.left-operation-container {
  display: flex;
  align-items: center;
  margin-bottom: var(--td-comp-margin-xxl);

  .selected-count {
    display: inline-block;
    margin-left: var(--td-comp-margin-l);
    color: var(--td-text-color-secondary);
  }
}

.search-input {
  width: 360px;
}
</style>
