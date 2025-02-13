<template>
  <div>
    <t-page-header>index.vue示例</t-page-header>
  </div>
</template>
<script setup>
import { onMounted, ref } from 'vue';

// 定义变量
const count = ref(0);

// 生命周期钩子
onMounted(() => {
  console.log(`The initial count is ${count.value}.`);
});
</script>
