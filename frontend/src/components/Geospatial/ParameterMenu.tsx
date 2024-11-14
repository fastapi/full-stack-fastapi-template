import React from "react";
import { useDropzone } from "react-dropzone";
import {
  Box,
  Text,
  Input,
  VStack,
  FormControl,
  FormLabel,
  Heading,
} from "@chakra-ui/react";

// FileInput component for handling file uploads with drag-and-drop functionality
const FileInput: React.FC = () => {
  // Callback function triggered when files are dropped onto the dropzone
  const onDrop = React.useCallback((acceptedFiles: File[]) => {
    console.log(acceptedFiles); // Logs the accepted files for further handling
  }, []);

  // Destructure functions and states from useDropzone to handle drag-and-drop
  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  return (
    // Chakra UI Box component styled as a dropzone area
    <Box
      {...getRootProps()}
      border="2px dashed"
      borderColor="gray.300"
      p={4}
      borderRadius="md"
      textAlign="center"
      cursor="pointer"
      _hover={{ borderColor: "gray.400" }} // Style when hovered
    >
      <input {...getInputProps()} />
      {/* Display text changes based on drag state */}
      <Text>{isDragActive ? "Drop the files here ..." : "Drag 'n' drop or click to select files"}</Text>
    </Box>
  );
};

// ParameterMenu component for general parameter settings
const ParameterMenu: React.FC = () => {
  return (
    // Chakra VStack for vertically stacked form controls with spacing
    <VStack spacing={4} align="stretch">
      <Heading size="md">Parameter Settings</Heading>
      <FormControl>
        <FormLabel>Parameter 1</FormLabel>
        <FileInput /> {/* Using FileInput component for file upload */}
      </FormControl>
      <FormControl>
        <FormLabel>Parameter 2</FormLabel>
        <FileInput />
      </FormControl>
      <FormControl>
        <FormLabel>Parameter 3</FormLabel>
        <FileInput />
      </FormControl>
      <FormControl>
        <FormLabel>Parameter 4</FormLabel>
        <Input placeholder="Enter value for Parameter 4" /> {/* Text input for parameter value */}
      </FormControl>
      <FormControl>
        <FormLabel>Parameter 5</FormLabel>
        <Input placeholder="Enter value for Parameter 5" />
      </FormControl>
    </VStack>
  );
};

// PeakLocalDetect_ParameterMenu component for peak detection-specific parameters
const PeakLocalDetect_ParameterMenu: React.FC = () => {
  return (
    // Chakra VStack provides vertical alignment and spacing for each control
    <VStack spacing={4} align="stretch">
      <Heading size="md">Peak Detection Settings</Heading>
      <FormControl>
        <FormLabel>Landcover Map</FormLabel>
        <FileInput />
      </FormControl>
      <FormControl>
        <FormLabel>Digital Elevation Model</FormLabel>
        <FileInput />
      </FormControl>
      <FormControl>
        <FormLabel>Digital Surface Model</FormLabel>
        <FileInput />
      </FormControl>
      <FormControl>
        <FormLabel>Minimum Tree Height</FormLabel>
        <Input placeholder="Enter Value" type="number" /> {/* Input for numeric parameter */}
      </FormControl>
      <FormControl>
        <FormLabel>Parameter 5</FormLabel>
        <Input placeholder="Enter value for Parameter 5" />
      </FormControl>
    </VStack>
  );
};

export { ParameterMenu, PeakLocalDetect_ParameterMenu };