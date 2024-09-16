<script setup lang="ts">

const { getItem } = useApi();

const { data, error } = await getItem('31')
</script>

<template>
  <h1 class="text-3xl font-bold underline">
    Hello world!
    {{data}} {{error}}
  </h1>
</template>

<style scoped>

</style>
