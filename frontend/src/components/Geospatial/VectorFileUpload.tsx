import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { Box, Text } from '@chakra-ui/react';

interface VectorFileUploadProps {
  onFileUpload: (geojson: any) => void;
}

const VectorFileUpload: React.FC<VectorFileUploadProps> = ({ onFileUpload }) => {
  const [uploadSuccess, setUploadSuccess] = useState(false);

  // onDrop: Triggered when a file is selected or dropped
  const onDrop = (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      console.log("Uploading file:", file.name);
      const formData = new FormData();
      formData.append('file', file);

      // Make a POST request to upload the shapefile to the backend
      axios.post('http://127.0.0.1:8000/files/upload_shapefile', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      .then((response) => {
        const geojson = response.data.geojson; // GeoJSON data received from the backend
        onFileUpload(JSON.parse(geojson)); // Pass parsed GeoJSON to parent component
        console.log("GeoJSON data loaded...");
        setUploadSuccess(true);
      })
      .catch((error) => {
        console.error("Error uploading file:", error);
        setUploadSuccess(false);
      });
    } else {
      console.error("No file selected");
    }
  };

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: { 'application/zip': ['.zip'] }, // Use object notation for MIME type
  });

  return (
    <Box className="geojson-upload-container" {...getRootProps()} border="1px dashed" padding="4" borderRadius="md" textAlign="center" cursor="pointer">
      <input {...getInputProps()} />
      <Text>
        {uploadSuccess ? "Change Area Of Interest?" : "Drag 'n' drop a .zip file containing shapefiles here, or click to select a file"}
      </Text>
    </Box>
  );
};

export default VectorFileUpload;