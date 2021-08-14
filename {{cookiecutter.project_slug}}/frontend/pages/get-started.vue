<template>
  <div>
    <h1>{{ page.title }}</h1>
    <nuxt-content :document="page" />
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "nuxt-property-decorator"

@Component({
  layout: "content",
})
export default class GetStarted extends Vue {
  async asyncData({ $content }) {
    const page = await $content("get-started").fetch()
    return {
      page,
    }
  }
}
</script>
