import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useNavigate, useRouterState } from "@tanstack/react-router"
import { Flame } from "lucide-react"

import {
  type ApiError,
  type ArticlePublic,
  type ArticlesPublic,
  LikesService,
} from "@/client"
import { isLoggedIn } from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { cn } from "@/lib/utils"
import { handleError } from "@/utils"

function patchArticle(
  data: ArticlesPublic | undefined,
  articleId: number,
  liked: boolean,
  delta: number,
): ArticlesPublic | undefined {
  if (!data) return data
  return {
    ...data,
    data: data.data.map((a) =>
      a.id === articleId
        ? {
            ...a,
            liked_by_me: liked,
            like_count: Math.max(0, (a.like_count ?? 0) + delta),
          }
        : a,
    ),
  }
}

export function LikeButton({ article }: { article: ArticlePublic }) {
  const navigate = useNavigate()
  const routerState = useRouterState()
  const queryClient = useQueryClient()
  const { showErrorToast } = useCustomToast()

  const liked = article.liked_by_me ?? false
  const count = article.like_count ?? 0

  const mutation = useMutation({
    mutationFn: () =>
      liked
        ? LikesService.unlikeArticle({ articleId: article.id })
        : LikesService.likeArticle({ articleId: article.id }),
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: ["articles"] })
      await queryClient.cancelQueries({ queryKey: ["liked-articles"] })
      const previous = [
        ...queryClient.getQueriesData<ArticlesPublic>({
          queryKey: ["articles"],
        }),
        ...queryClient.getQueriesData<ArticlesPublic>({
          queryKey: ["liked-articles"],
        }),
      ]
      queryClient.setQueriesData<ArticlesPublic>(
        { queryKey: ["articles"] },
        (old) => patchArticle(old, article.id, !liked, liked ? -1 : 1),
      )
      if (liked) {
        queryClient.setQueriesData<ArticlesPublic>(
          { queryKey: ["liked-articles"] },
          (old) =>
            old
              ? {
                  ...old,
                  data: old.data.filter((a) => a.id !== article.id),
                  count: Math.max(0, old.count - 1),
                }
              : old,
        )
      }
      return { previous }
    },
    onError: (err, _vars, context) => {
      context?.previous?.forEach(([key, data]) => {
        queryClient.setQueryData(key, data)
      })
      handleError.call(showErrorToast, err as ApiError)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["articles"] })
      queryClient.invalidateQueries({ queryKey: ["liked-articles"] })
    },
  })

  function handleClick() {
    if (!isLoggedIn()) {
      const redirect =
        routerState.location.pathname + routerState.location.searchStr
      navigate({ to: "/login", search: { redirect } })
      return
    }
    mutation.mutate()
  }

  return (
    <button
      type="button"
      data-testid="like-button"
      data-liked={liked}
      onClick={handleClick}
      className={cn(
        "flex items-center gap-1 text-xs transition-colors",
        liked
          ? "text-orange-500"
          : "text-muted-foreground hover:text-orange-500",
      )}
    >
      <Flame className={cn("h-3.5 w-3.5", liked && "fill-orange-500")} />
      <span data-testid="like-count">{count}</span>
    </button>
  )
}
