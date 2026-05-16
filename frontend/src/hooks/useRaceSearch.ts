import { useQuery } from "@tanstack/react-query"
import { OpenAPI } from "@/client/core/OpenAPI"
import { request as __request } from "@/client/core/request"
import type { RacePublic, DifficultyEnum, TerrainEnum } from "@/client"

export interface RaceSearchParams {
  q?: string
  terrain?: TerrainEnum | ""
  difficulty?: DifficultyEnum | ""
  distanceMin?: string
  distanceMax?: string
  provinceCode?: string
  sort?: "date" | "popularity"
  skip?: number
  limit?: number
}

export interface RacesSearchResult {
  data: RacePublic[]
  count: number
}

function buildQuery(params: RaceSearchParams): Record<string, string | number> {
  const q: Record<string, string | number> = {}
  if (params.q) q.q = params.q
  if (params.terrain) q.terrain = params.terrain
  if (params.difficulty) q.difficulty = params.difficulty
  if (params.distanceMin) q.distance_min_km = Number(params.distanceMin)
  if (params.distanceMax) q.distance_max_km = Number(params.distanceMax)
  if (params.provinceCode) q.province_code = params.provinceCode
  if (params.sort) q.sort = params.sort
  if (params.skip != null) q.skip = params.skip
  if (params.limit != null) q.limit = params.limit
  return q
}

async function searchRaces(params: RaceSearchParams): Promise<RacesSearchResult> {
  return __request(OpenAPI, {
    method: "GET",
    url: "/api/v1/races/search",
    query: buildQuery(params),
    errors: { 422: "Validation Error" },
  }) as Promise<RacesSearchResult>
}

export function useRaceSearch(params: RaceSearchParams) {
  return useQuery({
    queryKey: ["races", "search", params],
    queryFn: () => searchRaces(params),
    staleTime: 30_000,
    placeholderData: (prev) => prev,
  })
}
