import { useState } from "react";
import { Button, VStack, Box, Icon, FileUpload } from "@chakra-ui/react";
import { useMutation } from "@tanstack/react-query";
import { LuUpload } from "react-icons/lu";
import useCustomToast from "@/hooks/useCustomToast";
import { ApiError, DocumentsService } from "@/client";
import { handleError } from "@/utils";
// import { uploadDocument } from "@/api/documents"; // <-- you'll write this

const AddDocument = () => {
  const [files, setFiles] = useState<File[]>([]);
  const { showSuccessToast } = useCustomToast();

  const onFileChange = (files: File[]) => {
    setFiles(files);
  };

  const mutation = useMutation({
    mutationFn: async (file: File) => {
      // API call to upload file
      DocumentsService.createDocument({
        formData: { file },
      });

      //   return uploadDocument(formData);
    },
    onSuccess: () => {
      showSuccessToast("Upload successful");
      setFiles([]);
    },
    onError: (err: ApiError) => {
      console.error(err.message);

      handleError(err);
    },
  });

  const handleUpload = () => {
    if (files.length > 0) {
      mutation.mutate(files[0]); // if you want multiple, loop here
    }
  };

  return (
    <VStack gap={6} maxW="md" mx="auto">
      <FileUpload.Root
        maxW="xl"
        alignItems="stretch"
        maxFiles={10}
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

      {files.length > 0 && (
        <Button
          colorScheme="blue"
          onClick={handleUpload}
          loading={mutation.isPending}
        >
          Upload Document
        </Button>
      )}
    </VStack>
  );
};

export default AddDocument;
