import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Button,
  DialogActionTrigger,
  DialogTitle,
  Text,
  VStack,
  Box,
  Icon,
} from "@chakra-ui/react";
import { FaPlus } from "react-icons/fa";
import { LuUpload } from "react-icons/lu";

import { FileUpload } from "@chakra-ui/react";
import { DocumentsService } from "@/client";
import type { ApiError } from "@/client/core/ApiError";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTrigger,
} from "../ui/dialog";

const AddDocument = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const queryClient = useQueryClient();
  const { showSuccessToast } = useCustomToast();

  const onFileChange = (files: File[]) => {
    setFiles(files);
  };

  const mutation = useMutation({
    mutationFn: async (file: File) => {
      return DocumentsService.createDocument({
        formData: { file },
      });
    },
    onSuccess: () => {
      showSuccessToast("Document uploaded successfully.");
      setFiles([]);
      setIsOpen(false);
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
    onError: (err: ApiError) => {
      handleError(err);
    },
  });

  const handleUpload = () => {
    if (files.length > 0) {
      mutation.mutate(files[0]);
    }
  };

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button value="add-document" my={4}>
          <FaPlus fontSize="16px" />
          Add Document
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Upload Document</DialogTitle>
        </DialogHeader>

        <DialogBody>
          <Text mb={4}>Upload a PDF document (max 5MB).</Text>
          <VStack gap={6}>
            <FileUpload.Root
              maxW="xl"
              alignItems="stretch"
              maxFiles={1}
              accept=".pdf"
              onFileChange={({ acceptedFiles }) => onFileChange(acceptedFiles)}
            >
              <FileUpload.HiddenInput />
              <FileUpload.Dropzone>
                <Icon as={LuUpload} boxSize="6" color="fg.muted" />
                <FileUpload.DropzoneContent>
                  <Box>Drag and drop files here</Box>
                  <Box color="fg.muted">.pdf up to 5MB</Box>
                </FileUpload.DropzoneContent>
              </FileUpload.Dropzone>
            </FileUpload.Root>
          </VStack>
        </DialogBody>

        <DialogFooter gap={2}>
          <DialogActionTrigger asChild>
            <Button
              variant="subtle"
              colorPalette="gray"
              disabled={mutation.isPending}
            >
              Cancel
            </Button>
          </DialogActionTrigger>
          <Button
            variant="solid"
            onClick={handleUpload}
            disabled={files.length === 0}
            loading={mutation.isPending}
          >
            Upload
          </Button>
        </DialogFooter>

        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  );
};

export default AddDocument;
