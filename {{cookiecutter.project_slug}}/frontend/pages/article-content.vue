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
export default class ArticleContent extends Vue {
  async asyncData({ $content }) {
    const page = await $content("article-content").fetch()
    return {
      page,
    }
  }
}
</script>
