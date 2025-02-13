<template>
  <t-card theme="poster2" :bordered="false">
    <template #avatar>
      <t-avatar size="56px">
        <template #icon>
          <shop-icon v-if="product.type === 1" />
          <calendar-icon v-if="product.type === 2" />
          <service-icon v-if="product.type === 3" />
          <user-avatar-icon v-if="product.type === 4" />
          <laptop-icon v-if="product.type === 5" />
        </template>
      </t-avatar>
    </template>
    <template #status>
      <t-tag :theme="product.isSetup ? 'success' : 'default'" :disabled="!product.isSetup">{{
        product.isSetup ? t('components.isSetup.on') : t('components.isSetup.off')
      }}</t-tag>
    </template>
    <template #content>
      <p class="list-card-item_detail--name">{{ product.name }}</p>
      <p class="list-card-item_detail--desc">{{ product.description }}</p>
    </template>
    <template #footer>
      <t-avatar-group cascading="left-up" :max="2">
        <t-avatar>{{ typeMap[product.type - 1] }}</t-avatar>
        <t-avatar
          ><template #icon>
            <add-icon />
          </template>
        </t-avatar>
      </t-avatar-group>
    </template>
    <template #actions>
      <t-dropdown
        :disabled="!product.isSetup"
        trigger="click"
        :options="[
          {
            content: t('components.manage'),
            value: 'manage',
            onClick: () => handleClickManage(product),
          },
          {
            content: t('components.delete'),
            value: 'delete',
            onClick: () => handleClickDelete(product),
          },
        ]"
      >
        <t-button theme="default" :disabled="!product.isSetup" shape="square" variant="text">
          <more-icon />
        </t-button>
      </t-dropdown>
    </template>
  </t-card>
</template>
<script setup lang="ts">
import {
  AddIcon,
  CalendarIcon,
  LaptopIcon,
  MoreIcon,
  ServiceIcon,
  ShopIcon,
  UserAvatarIcon,
} from 'tdesign-icons-vue-next';
import type { PropType } from 'vue';

import { t } from '@/locales';

export interface CardProductType {
  type: number;
  isSetup: boolean;
  description: string;
  name: string;
}

// eslint-disable-next-line
const props = defineProps({
  product: {
    type: Object as PropType<CardProductType>,
  },
});

const emit = defineEmits(['manage-product', 'delete-item']);

const typeMap = ['A', 'B', 'C', 'D', 'E'];

const handleClickManage = (product: CardProductType) => {
  emit('manage-product', product);
};

const handleClickDelete = (product: CardProductType) => {
  emit('delete-item', product);
};
</script>

<style lang="less" scoped>
.list-card-item {
  display: flex;
  flex-direction: column;
  cursor: pointer;

  &_detail {
    min-height: 140px;

    &--name {
      margin-bottom: var(--td-comp-margin-s);
      font: var(--td-font-title-medium);
      color: var(--td-text-color-primary);
    }

    &--desc {
      color: var(--td-text-color-secondary);
      font: var(--td-font-body-small);
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
    }
  }
}
</style>
