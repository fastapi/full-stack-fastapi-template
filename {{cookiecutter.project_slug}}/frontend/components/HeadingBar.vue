<template>
  <header v-if="headingTitle" class="bg-white shadow">
    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <h1 class="text-3xl font-bold text-gray-900">{{ headingTitle }}</h1>
    </div>
  </header>
</template>

<script lang="ts">
import { Component, Vue } from "nuxt-property-decorator"
import { mapGetters } from "vuex"

@Component({
  computed: {
    ...mapGetters({
      headingTitle: "helpers/headingTitle",
    }),
  },
})
export default class HeadingBar extends Vue {}
</script>
