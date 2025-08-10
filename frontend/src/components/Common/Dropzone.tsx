import React from "react";
import { Box, FileUpload, Icon } from "@chakra-ui/react";
import { LuUpload } from "react-icons/lu";

const Dropzone = () => {
  return (
    <FileUpload.Root maxW="xl" alignItems="stretch" maxFiles={10}>
      <FileUpload.HiddenInput />
      <FileUpload.Dropzone>
        <Icon size="md" color="fg.muted">
          <LuUpload />
        </Icon>
        <FileUpload.DropzoneContent>
          <Box>Drag and drop files here</Box>
          <Box color="fg.muted">.pdf up to 5MB</Box>
        </FileUpload.DropzoneContent>
      </FileUpload.Dropzone>
      {/* <FileUpload.List /> */}
    </FileUpload.Root>
  );
};

export default Dropzone;
