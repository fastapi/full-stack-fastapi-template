import { Button, DialogTitle, Text } from "@chakra-ui/react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { FiTrash2 } from "react-icons/fi";

import { DocumentsService } from "@/client";
import {
  DialogActionTrigger,
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTrigger,
} from "@/components/ui/dialog";
import useCustomToast from "@/hooks/useCustomToast";

const DeleteDocument = ({ id }: { id: string }) => {
  const [isOpen, setIsOpen] = useState(false);
  const queryClient = useQueryClient();
  const { showSuccessToast, showErrorToast } = useCustomToast();
  const {
    handleSubmit,
    formState: { isSubmitting },
  } = useForm();

  const deleteDocument = async (id: string) => {
    await DocumentsService.deleteDocument({ id: id });
  };

  const mutation = useMutation({
    mutationFn: deleteDocument,
    onSuccess: () => {
      showSuccessToast("The document was deleted successfully");
      setIsOpen(false);
    },
    onError: () => {
      showErrorToast("An error occurred while deleting the document");
    },
    onSettled: () => {
      queryClient.invalidateQueries();
    },
  });

  const onSubmit = async () => {
    mutation.mutate(id);
  };

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      role="alertdialog"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" colorPalette="red">
          <FiTrash2 fontSize="16px" />
          Delete Document
        </Button>
      </DialogTrigger>

      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogCloseTrigger />
          <DialogHeader>
            <DialogTitle>Delete Document</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>
              This document will be permanently deleted. Are you sure? You will
              not be able to undo this action.
            </Text>
          </DialogBody>

          <DialogFooter gap={2}>
            <DialogActionTrigger asChild>
              <Button
                variant="subtle"
                colorPalette="gray"
                disabled={isSubmitting}
              >
                Cancel
              </Button>
            </DialogActionTrigger>
            <Button
              variant="solid"
              colorPalette="red"
              type="submit"
              loading={isSubmitting}
            >
              Delete
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </DialogRoot>
  );
};

export default DeleteDocument;
