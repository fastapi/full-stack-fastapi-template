<template>
  <div class="detail-deploy">
    <t-row :gutter="16">
      <t-col :lg="6" :xs="12">
        <t-card :title="t('pages.detailDeploy.deployTrend.title')" :bordered="false">
          <div class="deploy-panel-left">
            <div id="monitorContainer" style="width: 100%; height: 265px" />
          </div>
        </t-card>
      </t-col>
      <t-col :lg="6" :xs="12">
        <t-card :title="t('pages.detailDeploy.deployTrend.warning')" :bordered="false">
          <template #actions>
            <t-radio-group default-value="dateVal" @change="onAlertChange">
              <t-radio-button value="dateVal"> {{ t('pages.detailDeploy.deployTrend.thisWeek') }} </t-radio-button>
              <t-radio-button value="monthVal"> {{ t('pages.detailDeploy.deployTrend.thisMonth') }} </t-radio-button>
            </t-radio-group>
          </template>
          <div id="dataContainer" style="width: 100%; height: 265px" />
        </t-card>
      </t-col>
    </t-row>

    <!-- 项目列表 -->
    <t-card :title="t('pages.detailDeploy.projectList.title')" class="container-base-margin-top" :bordered="false">
      <t-table
        :columns="columns"
        :data="data"
        :pagination="pagination"
        :hover="true"
        :stripe="true"
        row-key="index"
        @sort-change="sortChange"
        @change="rehandleChange"
      >
        <template #adminName="{ row }">
          <span>
            {{ row.adminName }}
            <t-tag v-if="row.adminPhone" size="small">{{ row.adminPhone }}</t-tag>
          </span>
        </template>
        <template #op="slotProps">
          <t-space>
            <t-link theme="primary" @click="listClick()">{{ t('pages.detailDeploy.projectList.table.manage') }}</t-link>
            <t-link theme="danger" @click="deleteClickOp(slotProps)">{{
              t('pages.detailDeploy.projectList.table.delete')
            }}</t-link>
          </t-space>
        </template>
        <template #op-column>
          <t-icon name="descending-order" />
        </template>
      </t-table>
    </t-card>

    <t-dialog v-model:visible="visible" :header="t('pages.detailDeploy.projectList.dialog.title')" @confirm="onConfirm">
      <template #body>
        <div class="dialog-info-block">
          <div class="dialog-info-block">
            <div v-for="(item, index) in BASE_INFO_DATA" :key="index" class="info-item">
              <h1>{{ item.name }}</h1>
              <span
                :class="{
                  ['green']: item.type && item.type.value === 'green',
                  ['blue']: item.type && item.type.value === 'blue',
                }"
                >{{ item.value }}</span
              >
            </div>
          </div>
        </div>
      </template>
    </t-dialog>
  </div>
</template>

<script lang="ts">
export default {
  name: 'DetailDeploy',
};
</script>

<script setup lang="ts">
import { BarChart, LineChart } from 'echarts/charts';
import { GridComponent, LegendComponent, TitleComponent, ToolboxComponent, TooltipComponent } from 'echarts/components';
import * as echarts from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';

import { getProjectList } from '@/api/detail';
import { t } from '@/locales';
import { useSettingStore } from '@/store';
import { changeChartsTheme } from '@/utils/color';

import { BASE_INFO_DATA } from './constants';
import { get2ColBarChartDataSet, getSmoothLineDataSet } from './index';

const columns = [
  {
    width: '280',
    ellipsis: true,
    colKey: 'name',
    title: t('pages.detailDeploy.projectList.table.name'),
    sorter: (a: any, b: any) => a.name.substr(10) - b.name.substr(10),
  },
  {
    width: '280',
    ellipsis: true,
    title: t('pages.detailDeploy.projectList.table.admin'),
    colKey: 'adminName',
  },
  {
    width: '280',
    className: 'test',
    ellipsis: true,
    colKey: 'updateTime',
    title: t('pages.detailDeploy.projectList.table.createTime'),
    sorter: (a: any, b: any) => Date.parse(a.updateTime) - Date.parse(b.updateTime),
  },
  {
    align: 'left' as const,
    width: '200',
    className: 'test2',
    ellipsis: true,
    colKey: 'op',
    fixed: 'right' as const,
    title: t('pages.detailDeploy.projectList.table.operation'),
  },
];

echarts.use([
  TitleComponent,
  ToolboxComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  BarChart,
  LineChart,
  CanvasRenderer,
]);

const store = useSettingStore();

const chartColors = computed(() => store.chartColors);
const data = ref([]);
const pagination = ref({
  defaultPageSize: 10,
  total: 100,
  defaultCurrent: 1,
});

const fetchData = async () => {
  try {
    const { list } = await getProjectList();
    data.value = list;
    pagination.value = {
      ...pagination.value,
      total: list.length,
    };
  } catch (e) {
    console.log(e);
  }
};
const visible = ref(false);

// monitorChart logic
let monitorContainer: HTMLElement;
let monitorChart: echarts.ECharts;
onMounted(() => {
  monitorContainer = document.getElementById('monitorContainer');
  monitorChart = echarts.init(monitorContainer);
  monitorChart.setOption(getSmoothLineDataSet({ ...chartColors.value }));
  setInterval(() => {
    monitorChart.setOption(getSmoothLineDataSet({ ...chartColors.value }));
  }, 3000);
});

// dataChart logic
let dataContainer: HTMLElement;
let dataChart: echarts.ECharts;
onMounted(() => {
  dataContainer = document.getElementById('dataContainer');
  dataChart = echarts.init(dataContainer);
  dataChart.setOption(get2ColBarChartDataSet({ ...chartColors.value }));
});

/// / chartSize update
const updateContainer = () => {
  monitorChart.resize({
    width: monitorContainer.clientWidth,
    height: monitorContainer.clientHeight,
  });
  dataChart.resize({
    width: dataContainer.clientWidth,
    height: dataContainer.clientHeight,
  });
};

onUnmounted(() => {
  window.removeEventListener('resize', updateContainer);
});

const onAlertChange = () => {
  dataChart.setOption(get2ColBarChartDataSet({ ...chartColors.value }));
};

onMounted(() => {
  fetchData();
  window.addEventListener('resize', updateContainer, false);
});

watch(
  () => store.brandTheme,
  () => {
    changeChartsTheme([monitorChart, dataChart]);
  },
);

const sortChange = (val: unknown) => {
  console.log(val);
};
const rehandleChange = (changeParams: unknown, triggerAndData: unknown) => {
  console.log('统一Change', changeParams, triggerAndData);
};
const listClick = () => {
  visible.value = true;
};
const onConfirm = () => {
  visible.value = false;
};
const deleteClickOp = (e: { rowIndex: number }) => {
  data.value.splice(e.rowIndex, 1);
};
</script>

<style lang="less" scoped>
@import '../base/index.less';

.detail-deploy {
  :deep(.t-card) {
    padding: var(--td-comp-paddingTB-xxl) var(--td-comp-paddingLR-xxl);
  }

  :deep(.t-card__header) {
    padding: 0;
  }

  :deep(.t-card__body) {
    padding: 0;
    margin-top: var(--td-comp-margin-xxl);
  }

  :deep(.t-card__title) {
    font: var(--td-font-title-large);
    font-weight: 400;
  }

  :deep(.t-text-ellipsis) {
    width: auto;
  }
}
</style>
