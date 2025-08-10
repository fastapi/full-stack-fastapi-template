import { useState } from "react";
import { Button, VStack, Text } from "@chakra-ui/react";
import { FileUpload } from "@chakra-ui/react";
import useCustomToast from "@/hooks/useCustomToast";

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
        maxFiles={1}
        onFileChange={({ acceptedFiles }) => onFileChange(acceptedFiles)}
      >
        <FileUpload.HiddenInput />
        <FileUpload.Dropzone>
          <Text>Drag and drop a file or click to select</Text>
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
