<template>
  <t-card :bordered="false">
    <t-row>
      <t-col :xs="12" :xl="9">
        <t-card
          :bordered="false"
          :title="t('pages.dashboardBase.outputOverview.title')"
          :subtitle="t('pages.dashboardBase.outputOverview.subtitle')"
          :class="{ 'dashboard-overview-card': true, 'overview-panel': true }"
        >
          <template #actions>
            <t-date-range-picker
              class="card-date-picker-container"
              theme="primary"
              mode="date"
              :default-value="LAST_7_DAYS"
              @change="(value) => onStokeDataChange(value as string[])"
            />
          </template>
          <div id="stokeContainer" style="width: 100%; height: 351px" class="dashboard-chart-container"></div>
        </t-card>
      </t-col>
      <t-col :xs="12" :xl="3">
        <t-card :bordered="false" :class="{ 'dashboard-overview-card': true, 'export-panel': true }">
          <template #actions>
            <t-button>{{ t('pages.dashboardBase.outputOverview.export') }}</t-button>
          </template>
          <t-row>
            <t-col :xs="6" :xl="12">
              <t-card
                :bordered="false"
                :subtitle="t('pages.dashboardBase.outputOverview.month.input')"
                class="inner-card"
              >
                <div class="inner-card__content">
                  <div class="inner-card__content-title">1726</div>
                  <div class="inner-card__content-footer">
                    {{ t('pages.dashboardBase.outputOverview.since') }}
                    <trend class="trend-tag" type="down" :is-reverse-color="false" describe="20.3%" />
                  </div>
                </div>
              </t-card>
            </t-col>
            <t-col :xs="6" :xl="12">
              <t-card
                :bordered="false"
                :subtitle="t('pages.dashboardBase.outputOverview.month.output')"
                class="inner-card"
              >
                <div class="inner-card__content">
                  <div class="inner-card__content-title">226</div>
                  <div class="inner-card__content-footer">
                    {{ t('pages.dashboardBase.outputOverview.since') }}
                    <trend class="trend-tag" type="down" :is-reverse-color="false" describe="20.3%" />
                  </div>
                </div>
              </t-card>
            </t-col>
          </t-row>
        </t-card>
      </t-col>
    </t-row>
  </t-card>
</template>

<script lang="ts">
export default {
  name: 'DashboardBase',
};
</script>

<script setup lang="ts">
import { useWindowSize } from '@vueuse/core';
import { LineChart } from 'echarts/charts';
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components';
import * as echarts from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { computed, nextTick, onMounted, ref, watch } from 'vue';

// 导入样式
import Trend from '@/components/trend/index.vue';
import { t } from '@/locales';
import { useSettingStore } from '@/store';
import { changeChartsTheme } from '@/utils/color';
import { LAST_7_DAYS } from '@/utils/date';

import { constructInitDataset } from '../index';

echarts.use([TooltipComponent, LegendComponent, GridComponent, LineChart, CanvasRenderer]);

const store = useSettingStore();
const resizeTime = ref(1);

const chartColors = computed(() => store.chartColors);

// stokeCharts
let stokeContainer: HTMLElement;
let stokeChart: echarts.ECharts;
const renderStokeChart = () => {
  if (!stokeContainer) {
    stokeContainer = document.getElementById('stokeContainer');
  }
  stokeChart = echarts.init(stokeContainer);
  stokeChart.setOption(constructInitDataset({ dateTime: LAST_7_DAYS, ...chartColors.value }));
};

const renderCharts = () => {
  renderStokeChart();
};

// chartSize update
const updateContainer = () => {
  if (document.documentElement.clientWidth >= 1400 && document.documentElement.clientWidth < 1920) {
    resizeTime.value = Number((document.documentElement.clientWidth / 2080).toFixed(2));
  } else if (document.documentElement.clientWidth < 1080) {
    resizeTime.value = Number((document.documentElement.clientWidth / 1080).toFixed(2));
  } else {
    resizeTime.value = 1;
  }

  stokeChart.resize({
    width: stokeContainer.clientWidth,
    height: stokeContainer.clientHeight,
  });
};

onMounted(() => {
  renderCharts();
  nextTick(() => {
    updateContainer();
  });
});

const { width, height } = useWindowSize();
watch([width, height], () => {
  updateContainer();
});

watch(
  () => store.brandTheme,
  () => {
    changeChartsTheme([stokeChart]);
  },
);

watch(
  () => store.mode,
  () => {
    [stokeChart].forEach((item) => {
      item.dispose();
    });

    renderCharts();
  },
);

const onStokeDataChange = (checkedValues: string[]) => {
  stokeChart.setOption(constructInitDataset({ dateTime: checkedValues, ...chartColors.value }));
};
</script>

<style lang="less" scoped>
:deep(.t-card__body) {
  padding: var(--td-comp-paddingTB-xxl) var(--td-comp-paddingLR-xxl);
}

.dashboard-overview-card {
  :deep(.t-card__header) {
    padding: 0;
  }

  :deep(.t-card__title) {
    font: var(--td-font-title-large);
    font-weight: 400;
  }

  :deep(.t-card__body) {
    margin-top: var(--td-comp-margin-xxl);
    padding: 0;
  }

  &.overview-panel {
    border-right: none;
  }

  &.export-panel {
    border-left: none;
    margin-left: calc(var(--td-comp-margin-xxxl) + var(--td-comp-margin-xxxl));
  }
}

.inner-card {
  margin-top: var(--td-comp-margin-s);
  margin-bottom: var(--td-comp-margin-xxxxl);

  :deep(.t-card__header) {
    padding-bottom: 0;
  }

  :deep(.t-card__body) {
    margin-top: var(--td-comp-margin-s);
  }

  &__content {
    &-title {
      font-size: var(--td-font-size-headline-medium);
      line-height: var(--td-line-height-headline-medium);
    }

    &-footer {
      display: flex;
      align-items: center;
      color: var(--td-text-color-placeholder);
      margin-top: var(--td-comp-margin-xxl);

      .trend-tag {
        margin-left: var(--td-comp-margin-s);
      }
    }
  }
}
</style>
