<template>
  <t-row :gutter="[24, 24]">
    <t-col :flex="3">
      <div class="user-left-greeting">
        <div>
          Hi，Image
          <span class="regular"> {{ t('pages.user.markDay') }}</span>
        </div>
        <img src="@/assets/assets-tencent-logo.png" class="logo" />
      </div>

      <t-card class="user-info-list" :title="t('pages.user.personalInfo.title')" :bordered="false">
        <template #actions>
          <t-button theme="default" shape="square" variant="text">
            <t-icon name="ellipsis" />
          </t-button>
        </template>
        <t-descriptions :column="4" item-layout="vertical">
          <t-descriptions-item v-for="(item, index) in USER_INFO_LIST" :key="index" :label="t(item.title)">
            {{ item.content }}
          </t-descriptions-item>
        </t-descriptions>
      </t-card>

      <t-card class="content-container" :bordered="false">
        <t-tabs value="second">
          <t-tab-panel value="first" :label="t('pages.user.contentList')">
            <p>{{ t('pages.user.contentList') }}</p>
          </t-tab-panel>
          <t-tab-panel value="second" :label="t('pages.user.contentList')">
            <t-card :bordered="false" class="card-padding-no" :title="t('pages.user.visitData')" describe="（次）">
              <template #actions>
                <t-date-range-picker
                  class="card-date-picker-container"
                  :default-value="LAST_7_DAYS"
                  theme="primary"
                  mode="date"
                  @change="onLineChange"
                />
              </template>
              <div id="lineContainer" style="width: 100%; height: 328px" />
            </t-card>
          </t-tab-panel>
          <t-tab-panel value="third" :label="t('pages.user.contentList')">
            <p>{{ t('pages.user.contentList') }}</p>
          </t-tab-panel>
        </t-tabs>
      </t-card>
    </t-col>

    <t-col :flex="1">
      <t-card class="user-intro" :bordered="false">
        <t-avatar size="80px">T</t-avatar>
        <div class="name">My Account</div>
        <div class="position">{{ t('pages.user.personalInfo.position') }}</div>
      </t-card>

      <t-card :title="t('pages.user.teamMember')" class="user-team" :bordered="false">
        <template #actions>
          <t-button theme="default" shape="square" variant="text">
            <t-icon name="ellipsis" />
          </t-button>
        </template>
        <t-list :split="false">
          <t-list-item v-for="(item, index) in TEAM_MEMBERS" :key="index">
            <t-list-item-meta :image="item.avatar" :title="item.title" :description="item.description" />
          </t-list-item>
        </t-list>
      </t-card>

      <t-card :title="t('pages.user.serviceProduction')" class="product-container" :bordered="false">
        <template #actions>
          <t-button theme="default" shape="square" variant="text">
            <t-icon name="ellipsis" />
          </t-button>
        </template>
        <t-row class="content" :getters="16">
          <t-col v-for="(item, index) in PRODUCT_LIST" :key="index" :span="3">
            <component :is="getIcon(item)"></component>
          </t-col>
        </t-row>
      </t-card>
    </t-col>
  </t-row>
</template>
<script lang="ts">
export default {
  name: 'UserIndex',
};
</script>
<script setup lang="ts">
import { LineChart } from 'echarts/charts';
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components';
import * as echarts from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import type { DateRangeValue } from 'tdesign-vue-next';
import { computed, nextTick, onMounted, onUnmounted, watch } from 'vue';

import ProductAIcon from '@/assets/assets-product-1.svg';
import ProductBIcon from '@/assets/assets-product-2.svg';
import ProductCIcon from '@/assets/assets-product-3.svg';
import ProductDIcon from '@/assets/assets-product-4.svg';
import { t } from '@/locales';
import { useSettingStore } from '@/store';
import { changeChartsTheme } from '@/utils/color';
import { LAST_7_DAYS } from '@/utils/date';

import { PRODUCT_LIST, TEAM_MEMBERS, USER_INFO_LIST } from './constants';
import { getFolderLineDataSet } from './index';

echarts.use([GridComponent, TooltipComponent, LineChart, CanvasRenderer, LegendComponent]);

let lineContainer: HTMLElement;
let lineChart: echarts.ECharts;
const store = useSettingStore();
const chartColors = computed(() => store.chartColors);

const onLineChange = (value: DateRangeValue) => {
  lineChart.setOption(
    getFolderLineDataSet({
      dateTime: value as string[],
      ...chartColors.value,
    }),
  );
};

const initChart = () => {
  lineContainer = document.getElementById('lineContainer');
  lineChart = echarts.init(lineContainer);
  lineChart.setOption({
    grid: {
      x: 30, // 默认是80px
      y: 30, // 默认是60px
      x2: 10, // 默认80px
      y2: 30, // 默认60px
    },
    ...getFolderLineDataSet({ ...chartColors.value }),
  });
};

const updateContainer = () => {
  lineChart?.resize({
    width: lineContainer.clientWidth,
    height: lineContainer.clientHeight,
  });
};

onMounted(() => {
  nextTick(() => {
    initChart();
  });
  window.addEventListener('resize', updateContainer, false);
});

onUnmounted(() => {
  window.removeEventListener('resize', updateContainer);
});

const getIcon = (type: string) => {
  switch (type) {
    case 'a':
      return ProductAIcon;
    case 'b':
      return ProductBIcon;
    case 'c':
      return ProductCIcon;
    case 'd':
      return ProductDIcon;
    default:
      return ProductAIcon;
  }
};

watch(
  () => store.brandTheme,
  () => {
    changeChartsTheme([lineChart]);
  },
);
</script>

<style lang="less" scoped>
@import './index.less';

.t-descriptions {
  margin-top: 24px;
}
</style>
