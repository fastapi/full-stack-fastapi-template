import { useState } from "react";
import { Button, VStack } from "@chakra-ui/react";
import useCustomToast from "@/hooks/useCustomToast";
import { Box, FileUpload, Icon } from "@chakra-ui/react";
import { LuUpload } from "react-icons/lu";

const AddDocument = () => {
  const [files, setFiles] = useState<File[]>([]);
  const { showSuccessToast } = useCustomToast();

  const onFileChange = (files: File[]) => {
    setFiles(files);
  };

  const handleUpload = () => {
    // Implement your upload logic here: API call etc.
    showSuccessToast("Upload successful");
    setFiles([]);
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
        <Button colorScheme="blue" onClick={handleUpload}>
          Upload Document
        </Button>
      )}
    </VStack>
  );
};

export default AddDocument;
