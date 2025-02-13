<template>
  <div class="operator-block operator-gap">
    <div class="operator-content">
      <div class="operator-title">
        <t-icon name="cart" class="operator-title-icon" />
        <h1>{{ data.name }}</h1>
        <div class="operator-title-subtitle">
          {{ data.subtitle }}
        </div>
        <div class="operator-title-tags">
          <t-tag class="operator-title-tag" theme="success" size="medium">
            {{ data.size }}
          </t-tag>
          <t-tag class="operator-title-tag" size="medium">
            {{ data.cpu }}
          </t-tag>
          <t-tag class="operator-title-tag" size="medium">
            {{ data.memory }}
          </t-tag>
        </div>
      </div>
      <div class="operator-item">
        <span class="operator-item-info">{{ data.info }}</span>
        <t-icon class="operator-item-icon" name="chevron-right" size="small" style="color: rgb(0 0 0 / 26%)" />
      </div>
    </div>
    <div class="operator-footer">
      <span class="operator-footer-percentage">{{ data.use }} / {{ data.stock }}（台）</span>
      <t-progress
        class="operator-progress"
        theme="line"
        :percentage="(data.use / data.stock) * 100"
        :label="false"
        :color="data.use / data.stock < 0.5 ? '#E24D59' : ''"
        :track-color="data.use / data.stock < 0.5 ? '#FCD4D4' : '#D4E3FC'"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  props: {
    data: {
      type: Object,
      default: () => {
        return {};
      },
    },
  },
});
</script>

<style lang="less" scoped>
.operator-block {
  position: relative;
  background-color: var(--td-bg-color-container);
  border: 1px solid var(--td-component-border);
  border-radius: var(--td-radius-medium);

  .operator-content {
    padding: var(--td-comp-paddingTB-xl) var(--td-comp-paddingLR-xl);
    height: 240px;

    .operator-title-icon {
      background: var(--td-brand-color-light);
      color: var(--td-brand-color);
      font-size: var(--td-comp-size-xxxl);
      padding: calc(var(--td-comp-size-xxxl) - var(--td-comp-size-xl));
      border-radius: 100%;
      position: absolute;
      top: 0;
      right: 0;
    }

    .operator-title {
      margin-bottom: var(--td-comp-margin-xxl);
      position: relative;

      h1 {
        display: inline-block;
        font: var(--td-font-title-large);
        color: var(--td-text-color-primary);
      }

      &-subtitle {
        display: block;
        font: var(--td-font-body-medium);
        color: var(--td-text-color-placeholder);
      }

      &-tag {
        margin-right: var(--td-comp-margin-s);
        margin-top: var(--td-comp-margin-l);
        margin-left: unset;
        border: unset;
      }

      svg {
        circle {
          fill: var(--td-brand-color-focus);
        }

        path {
          fill: var(--td-brand-color);
        }
      }
    }

    .operator-item {
      position: relative;
      padding-bottom: var(--td-comp-margin-xxl);
      display: flex;
      align-items: center;
      justify-content: space-between;

      &-info {
        display: inline-block;
        width: 80%;
        text-align: left;
        font: var(--td-font-body-medium);
        color: var(--td-text-color-placeholder);
      }

      &-icon {
        font-size: var(--td-comp-size-xxxs);
      }
    }
  }

  .operator-footer {
    position: absolute;
    width: 100%;
    bottom: 0;
    left: 0;

    .t-progress--thin {
      display: unset;

      :deep(.t-progress__info) {
        margin-left: 0;
      }
    }

    &-percentage {
      position: absolute;
      bottom: var(--td-comp-margin-l);
      right: var(--td-comp-paddingLR-xl);
      color: var(--td-text-color-placeholder);
    }

    .operator-progress {
      display: unset;

      :deep(.t-progress__bar) {
        border-radius: 0 0 var(--td-radius-medium) var(--td-radius-medium);
      }

      :deep(.t-progress__inner) {
        border-radius: 0 0 0 var(--td-radius-medium);
      }

      :deep(.t-progress__info) {
        margin-left: 0;
      }
    }
  }
}
</style>
