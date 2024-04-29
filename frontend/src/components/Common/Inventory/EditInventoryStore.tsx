import {
    Button,
    FormControl,
    FormErrorMessage,
    FormLabel,
    Input,
    Modal,
    ModalBody,
    ModalCloseButton,
    ModalContent,
    ModalFooter,
    ModalHeader,
    ModalOverlay,
  } from "@chakra-ui/react"
  import { useMutation, useQueryClient } from "@tanstack/react-query"
  import { type SubmitHandler, useForm } from "react-hook-form"
  
  import {
    type ApiError,
    type ItemPublic,
    type ItemUpdate,
    ItemsService,
    StoresService,
  } from "../../../client"
  import useCustomToast from "../../../hooks/useCustomToast"
import { useParams } from "@tanstack/react-router"
  
  interface EditItemProps {
    item: ItemPublic
    isOpen: boolean
    onClose: () => void
  }
  
  const EditStoreInventory = ({ item, isOpen, onClose }: EditItemProps) => {
    const queryClient = useQueryClient()
    const showToast = useCustomToast()

    const {storeId} = useParams({
        from: "/_layout/store/$storeId/inventory"
    })
    
    const {
      register,
      handleSubmit,
      reset,
      formState: { isSubmitting, errors, isDirty },
    } = useForm<ItemPublic>({
      mode: "onBlur",
      criteriaMode: "all",
      defaultValues: item,
    })
  
    console.log(item)
    const mutation = useMutation({
      mutationFn: (data: ItemPublic) =>
        StoresService.updateStoreInventory({ 
            id: Number(storeId),
            requestBody: {
                "store_id": Number(storeId),
                "item_id": item.id,
                "stock_unit": Number(data.units),
            }}),
      onSuccess: () => {
        showToast("Success!", "Item updated successfully.", "success")
        onClose()
      },
      onError: (err: ApiError) => {
        const errDetail = (err.body as any)?.detail
        showToast("Something went wrong.", `${errDetail}`, "error")
      },
      onSettled: () => {
        queryClient.invalidateQueries({ queryKey: ["items"] })
      },
    })
  
    const onSubmit: SubmitHandler<ItemPublic> = async (data) => {
      mutation.mutate(data)
    }
  
    const onCancel = () => {
      reset()
      onClose()
    }
  
    return (
      <>
        <Modal
          isOpen={isOpen}
          onClose={onClose}
          size={{ base: "sm", md: "md" }}
          isCentered
        >
          <ModalOverlay />
          <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
            <ModalHeader>Edit Quantity</ModalHeader>
            <ModalCloseButton />
            <ModalBody pb={6}>
              <FormControl mt={4}>
                <FormLabel htmlFor="units">Units</FormLabel>
                <Input
                  id="units"
                  {...register("units")}
                  placeholder="Units"
                  type="text"
                />
              </FormControl>
            </ModalBody>
            <ModalFooter gap={3}>
              <Button
                variant="primary"
                type="submit"
                isLoading={isSubmitting}
                isDisabled={!isDirty}
              >
                Save
              </Button>
              <Button onClick={onCancel}>Cancel</Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </>
    )
  }
  
  export default EditStoreInventory
  