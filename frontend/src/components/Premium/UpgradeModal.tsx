/**
 * Upgrade Modal Component
 *
 * Displays when a free user hits the item limit. Shows upgrade benefits
 * and provides a button to initiate Stripe checkout.
 */

import {
  Button,
  DialogTitle,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useMutation } from "@tanstack/react-query"
import { FaStar } from "react-icons/fa"

import { StripeService } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
} from "../ui/dialog"

interface UpgradeModalProps {
  isOpen: boolean
  onClose: () => void
}

const UpgradeModal = ({ isOpen, onClose }: UpgradeModalProps) => {
  const { showSuccessToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: () => StripeService.createCheckoutSession(),
    onSuccess: (data) => {
      showSuccessToast("Redirecting to checkout...")
      window.location.href = data.checkout_url
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
  })

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => !open && onClose()}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Upgrade to Premium</DialogTitle>
        </DialogHeader>
        <DialogBody>
          <VStack gap={4} align="start">
            <Text>
              You've reached the free tier limit of 2 items.
            </Text>
            <Text>
              Upgrade to Premium for just $1 to unlock:
            </Text>
            <VStack align="start" pl={4} gap={1}>
              <Text>- Unlimited items</Text>
              <Text>- Premium star badge</Text>
            </VStack>
          </VStack>
        </DialogBody>
        <DialogFooter gap={2}>
          <Button
            variant="subtle"
            colorPalette="gray"
            onClick={onClose}
            disabled={mutation.isPending}
          >
            Cancel
          </Button>
          <Button
            colorPalette="yellow"
            onClick={() => mutation.mutate()}
            loading={mutation.isPending}
          >
            <FaStar />
            Upgrade Now - $1
          </Button>
        </DialogFooter>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default UpgradeModal
