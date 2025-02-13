<template>
  <div class="list-common-table">
    <t-form ref="form" :data="formData" :label-width="80" colon @reset="onReset" @submit="onSubmit">
      <t-row>
        <t-col :span="10">
          <t-row :gutter="[24, 24]">
            <t-col :span="4">
              <t-form-item :label="t('components.commonTable.contractName')" name="name">
                <t-input
                  v-model="formData.name"
                  class="form-item-content"
                  type="search"
                  :placeholder="t('components.commonTable.contractNamePlaceholder')"
                  :style="{ minWidth: '134px' }"
                />
              </t-form-item>
            </t-col>
            <t-col :span="4">
              <t-form-item :label="t('components.commonTable.contractStatus')" name="status">
                <t-select
                  v-model="formData.status"
                  class="form-item-content"
                  :options="CONTRACT_STATUS_OPTIONS"
                  :placeholder="t('components.commonTable.contractStatusPlaceholder')"
                  clearable
                />
              </t-form-item>
            </t-col>
            <t-col :span="4">
              <t-form-item :label="t('components.commonTable.contractNum')" name="no">
                <t-input
                  v-model="formData.no"
                  class="form-item-content"
                  :placeholder="t('components.commonTable.contractNumPlaceholder')"
                  :style="{ minWidth: '134px' }"
                />
              </t-form-item>
            </t-col>
            <t-col :span="4">
              <t-form-item :label="t('components.commonTable.contractType')" name="type">
                <t-select
                  v-model="formData.type"
                  style="display: inline-block"
                  class="form-item-content"
                  :options="CONTRACT_TYPE_OPTIONS"
                  :placeholder="t('components.commonTable.contractTypePlaceholder')"
                  clearable
                />
              </t-form-item>
            </t-col>
          </t-row>
        </t-col>

        <t-col :span="2" class="operation-container">
          <t-button theme="primary" type="submit" :style="{ marginLeft: 'var(--td-comp-margin-s)' }">
            {{ t('components.commonTable.query') }}
          </t-button>
          <t-button type="reset" variant="base" theme="default"> {{ t('components.commonTable.reset') }} </t-button>
        </t-col>
      </t-row>
    </t-form>

    <div class="table-container">
      <t-table
        :data="data"
        :columns="COLUMNS"
        :row-key="rowKey"
        :vertical-align="verticalAlign"
        :hover="hover"
        :pagination="pagination"
        :loading="dataLoading"
        :header-affixed-top="headerAffixedTop"
        @page-change="rehandlePageChange"
        @change="rehandleChange"
      >
        <template #status="{ row }">
          <t-tag v-if="row.status === CONTRACT_STATUS.FAIL" theme="danger" variant="light">
            {{ t('components.commonTable.contractStatusEnum.fail') }}
          </t-tag>
          <t-tag v-if="row.status === CONTRACT_STATUS.AUDIT_PENDING" theme="warning" variant="light">
            {{ t('components.commonTable.contractStatusEnum.audit') }}
          </t-tag>
          <t-tag v-if="row.status === CONTRACT_STATUS.EXEC_PENDING" theme="warning" variant="light">
            {{ t('components.commonTable.contractStatusEnum.pending') }}
          </t-tag>
          <t-tag v-if="row.status === CONTRACT_STATUS.EXECUTING" theme="success" variant="light">
            {{ t('components.commonTable.contractStatusEnum.executing') }}
          </t-tag>
          <t-tag v-if="row.status === CONTRACT_STATUS.FINISH" theme="success" variant="light">
            {{ t('components.commonTable.contractStatusEnum.finish') }}
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
      <t-dialog
        v-model:visible="confirmVisible"
        header="确认删除当前所选合同？"
        :body="confirmBody"
        :on-cancel="onCancel"
        @confirm="onConfirmDelete"
      />
    </div>
  </div>
</template>
<script setup lang="ts">
import { MessagePlugin, PageInfo, PrimaryTableCol, TableRowData } from 'tdesign-vue-next';
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';

import { getList } from '@/api/list';
import Trend from '@/components/trend/index.vue';
import { prefix } from '@/config/global';
import { CONTRACT_PAYMENT_TYPES, CONTRACT_STATUS, CONTRACT_TYPES } from '@/constants';
import { t } from '@/locales';
import { useSettingStore } from '@/store';

interface FormData {
  name: string;
  no: string;
  status?: number;
  type: string;
}

const store = useSettingStore();
const router = useRouter();

const CONTRACT_STATUS_OPTIONS = [
  { value: CONTRACT_STATUS.FAIL, label: t('components.commonTable.contractStatusEnum.fail') },
  { value: CONTRACT_STATUS.AUDIT_PENDING, label: t('components.commonTable.contractStatusEnum.audit') },
  { value: CONTRACT_STATUS.EXEC_PENDING, label: t('components.commonTable.contractStatusEnum.pending') },
  { value: CONTRACT_STATUS.EXECUTING, label: t('components.commonTable.contractStatusEnum.executing') },
  { value: CONTRACT_STATUS.FINISH, label: t('components.commonTable.contractStatusEnum.finish') },
];

const CONTRACT_TYPE_OPTIONS = [
  { value: CONTRACT_TYPES.MAIN, label: t('components.commonTable.contractTypeEnum.main') },
  { value: CONTRACT_TYPES.SUB, label: t('components.commonTable.contractTypeEnum.sub') },
  { value: CONTRACT_TYPES.SUPPLEMENT, label: t('components.commonTable.contractTypeEnum.supplement') },
];
const COLUMNS: PrimaryTableCol[] = [
  {
    title: t('components.commonTable.contractName'),
    fixed: 'left',
    width: 280,
    ellipsis: true,
    align: 'left',
    colKey: 'name',
  },
  { title: t('components.commonTable.contractStatus'), colKey: 'status', width: 160 },
  {
    title: t('components.commonTable.contractNum'),
    width: 160,
    ellipsis: true,
    colKey: 'no',
  },
  {
    title: t('components.commonTable.contractType'),
    width: 160,
    ellipsis: true,
    colKey: 'contractType',
  },
  {
    title: t('components.commonTable.contractPayType'),
    width: 160,
    ellipsis: true,
    colKey: 'paymentType',
  },
  {
    title: t('components.commonTable.contractAmount'),
    width: 160,
    ellipsis: true,
    colKey: 'amount',
  },
  {
    align: 'left',
    fixed: 'right',
    width: 160,
    colKey: 'op',
    title: t('components.commonTable.operation'),
  },
];

const searchForm = {
  name: '',
  no: '',
  type: '',
};

const formData = ref<FormData>({ ...searchForm });
const rowKey = 'index';
const verticalAlign = 'top' as const;
const hover = true;

const pagination = ref({
  defaultPageSize: 20,
  total: 100,
  defaultCurrent: 1,
});
const confirmVisible = ref(false);

const data = ref([]);

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

const resetIdx = () => {
  deleteIdx.value = -1;
};

const onConfirmDelete = () => {
  // 真实业务请发起请求
  data.value.splice(deleteIdx.value, 1);
  pagination.value.total = data.value.length;
  confirmVisible.value = false;
  MessagePlugin.success('删除成功');
  resetIdx();
};

const onCancel = () => {
  resetIdx();
};

onMounted(() => {
  fetchData();
});

const handleClickDelete = (slot: { row: { rowIndex: number } }) => {
  deleteIdx.value = slot.row.rowIndex;
  confirmVisible.value = true;
};
const onReset = (val: unknown) => {
  console.log(val);
};

const handleClickDetail = () => {
  router.push('/detail/base');
};
const onSubmit = (val: unknown) => {
  console.log(val);
  console.log(formData.value);
};
const rehandlePageChange = (pageInfo: PageInfo, newDataSource: TableRowData[]) => {
  console.log('分页变化', pageInfo, newDataSource);
};
const rehandleChange = (changeParams: unknown, triggerAndData: unknown) => {
  console.log('统一Change', changeParams, triggerAndData);
};

const headerAffixedTop = computed(
  () =>
    ({
      offsetTop: store.isUseTabsRouter ? 48 : 0,
      container: `.${prefix}-layout`,
    }) as any, // TO BE FIXED
);
</script>

<style lang="less" scoped>
.list-common-table {
  background-color: var(--td-bg-color-container);
  padding: var(--td-comp-paddingTB-xxl) var(--td-comp-paddingLR-xxl);
  border-radius: var(--td-radius-medium);

  .table-container {
    margin-top: var(--td-comp-margin-xxl);
  }
}

.form-item-content {
  width: 100%;
}

.operation-container {
  display: flex;
  justify-content: flex-end;
  align-items: center;

  .expand {
    .t-button__text {
      display: flex;
      align-items: center;
    }
  }
}

.payment-col {
  display: flex;

  .trend-container {
    display: flex;
    align-items: center;
    margin-left: var(--td-comp-margin-s);
  }
}
</style>
