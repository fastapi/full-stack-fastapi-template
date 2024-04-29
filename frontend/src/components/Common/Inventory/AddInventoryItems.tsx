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
  Select,
} from "@chakra-ui/react";
import {
  useMutation,
  useQuery,
  useQueryClient,
  useSuspenseQuery,
} from "@tanstack/react-query";
import { type SubmitHandler, useForm } from "react-hook-form";

import {
  type ApiError,
  type StoreCreate,
  StoresService,
  ItemsService,
  TDataUpdateStoreInventory,
  StoreInventoryUpdate,
} from "../../../client";
import useCustomToast from "../../../hooks/useCustomToast";
import { useParams } from "@tanstack/react-router";

interface AddStoreProps {
  isOpen: boolean;
  onClose: () => void;
}

const AddStoreInventory = ({ isOpen, onClose }: AddStoreProps) => {
  const queryClient = useQueryClient();
  const showToast = useCustomToast();

  const { data: items } = useQuery({
    queryKey: ["items"],
    queryFn: () => ItemsService.readItems({}),
  });

  const {storeId} = useParams({
    from: "/_layout/store/$storeId/inventory"
})

  const {
    register,
    handleSubmit,
    reset,
    getValues,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<StoreInventoryUpdate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      item_id: 0,
      stock_unit: 0,
      store_id: Number(storeId)
    },
  })

  const mutation = useMutation({
    mutationFn: (data: StoreInventoryUpdate) =>
      StoresService.updateStoreInventory({ 
        id: Number(storeId),
        requestBody: {
            "store_id": Number(storeId),
            "item_id":  Number(data.item_id),
            "stock_unit": Number(data.stock_unit),
        }}),
    onSuccess: () => {
      showToast("Success!", "Item created successfully.", "success")
      reset()
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

  const onSubmit: SubmitHandler<StoreInventoryUpdate> = (data) => {
     mutation.mutate(data)
  };

  return (
    <>
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        size={{ base: "sm", md: "md" }}
        isCentered
      >
        <ModalOverlay />
        <ModalContent as="form"  onSubmit={handleSubmit(onSubmit)}>
          <ModalHeader>Add Item</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <FormControl isRequired>
              <FormLabel htmlFor="title">Item</FormLabel>
              <Select
               {...register("item_id")}
               id="item_id" placeholder="Select an option">
                {items?.data.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.title}
                  </option>
                ))
                }
              </Select>
            </FormControl>
            <FormControl isRequired isInvalid={!!errors.item_id}>
              <FormLabel htmlFor="stock_unit">Title</FormLabel>
              <Input
                id="stock_units"
                {...register("stock_unit", {
                  required: "Units is required.",
                  max: items?.data.filter(i => i.id === getValues("stock_unit")).at(0)?.units
                })}
                placeholder="Units(s)"
                type="text"
                         />
              {errors.stock_unit && (
                <FormErrorMessage>{errors.stock_unit.message}</FormErrorMessage>
              )}
            </FormControl>
          </ModalBody>

          <ModalFooter gap={3}>
            <Button variant="primary" type="submit" >
              Save
            </Button>
            <Button onClick={onClose}>Cancel</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

export default AddStoreInventory;
