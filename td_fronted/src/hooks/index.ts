import * as echarts from 'echarts/core';
import { onMounted, onUnmounted, Ref, ref, ShallowRef, shallowRef } from 'vue';

/**
 * eChart hook
 * @param domId
 */
export const useChart = (domId: string): ShallowRef<echarts.ECharts> => {
  let chartContainer: HTMLCanvasElement;
  const selfChart = shallowRef<echarts.ECharts | any>();
  const updateContainer = () => {
    selfChart.value.resize({
      width: chartContainer.clientWidth,
      height: chartContainer.clientHeight,
    });
  };

  onMounted(() => {
    if (!chartContainer) {
      chartContainer = document.getElementById(domId) as HTMLCanvasElement;
    }
    selfChart.value = echarts.init(chartContainer);
  });

  window.addEventListener('resize', updateContainer, false);

  onUnmounted(() => {
    window.removeEventListener('resize', updateContainer);
  });

  return selfChart;
};

/**
 * counter utils
 * @param duration
 * @returns
 */
export const useCounter = (duration = 60): [Ref<number>, () => void] => {
  let intervalTimer: ReturnType<typeof setInterval>;
  onUnmounted(() => {
    clearInterval(intervalTimer);
  });
  const countDown = ref(0);

  return [
    countDown,
    () => {
      countDown.value = duration;
      intervalTimer = setInterval(() => {
        if (countDown.value > 0) {
          countDown.value -= 1;
        } else {
          clearInterval(intervalTimer);
          countDown.value = 0;
        }
      }, 1000);
    },
  ];
};
