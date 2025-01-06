import {
  PaginationItems,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "@/components/ui/pagination"
import { Flex, HStack } from "@chakra-ui/react"

type PaginationFooterProps = {
  page: number
  pageSize: number
  count: number
  setPage: (page: number) => void
}

export function PaginationFooter({
  page,
  count,
  pageSize,
  setPage,
}: PaginationFooterProps) {
  return (
    <Flex mt={4} justifyContent="flex-end">
      <PaginationRoot
        page={page}
        count={count}
        pageSize={pageSize}
        onPageChange={(e) => setPage(e.page)}
      >
        <HStack>
          <PaginationPrevTrigger />
          <PaginationItems />
          <PaginationNextTrigger />
        </HStack>
      </PaginationRoot>
    </Flex>
  )
}
