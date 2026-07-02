import { keepPreviousData, useQuery } from "@tanstack/react-query"
import { ArticlesService } from "@/client"
import { useFilters } from "@/context/filters"
import { cn } from "@/lib/utils"
import { ArticleRow } from "./ArticleRow"

const PUBLISHED_DAYS: Record<string, number> = { "3d": 3, "1w": 7, "1m": 30 }

function cutoffIso(days: number): string {
  const d = new Date()
  d.setDate(d.getDate() - days)
  return d.toISOString()
}

export function ArticlesList() {
  const { filters } = useFilters()
  const { search, dateRange, sort, category, kind } = filters

  const since = cutoffIso(PUBLISHED_DAYS[dateRange] ?? 7)

  const { data, isLoading, isFetching, isError } = useQuery({
    queryKey: ["articles", search, dateRange, sort, category, kind],
    queryFn: () => {
      if (search) {
        return ArticlesService.searchArticles({ q: search, limit: 50 })
      }
      return ArticlesService.readArticles({
        limit: 50,
        since,
        sort,
        category: category || undefined,
        kind: kind || undefined,
      })
    },
    placeholderData: keepPreviousData,
  })

  if (isLoading) {
    return null
  }

  if (isError || !data) {
    return (
      <div className="py-12 text-sm text-destructive">
        Failed to load articles.
      </div>
    )
  }

  const articles = data.data

  return (
    <div className="relative">
      {articles.length === 0 ? (
        <div
          data-testid="articles-empty"
          className="py-12 text-sm text-muted-foreground"
        >
          No articles found.
        </div>
      ) : (
        <ul
          data-testid="articles-list"
          className={cn(
            "divide-y divide-border/40 transition-opacity duration-200",
            isFetching && "opacity-50",
          )}
        >
          {articles.map((article) => (
            <ArticleRow key={article.id} article={article} />
          ))}
        </ul>
      )}

      {!isFetching && articles.length > 0 && (
        <p className="pt-4 text-xs text-muted-foreground">
          {articles.length} article{articles.length !== 1 ? "s" : ""}
        </p>
      )}
    </div>
  )
}
