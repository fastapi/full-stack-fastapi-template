import React from 'react';
import { useDropzone } from 'react-dropzone';
import { fromArrayBuffer } from 'geotiff';

const RasterFileUpload = ({ onFileUpload }) => {
  const onDrop = (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const arrayBuffer = e.target.result;
        const tiff = await fromArrayBuffer(arrayBuffer);
        const image = await tiff.getImage();
        const data = await image.readRasters();
        onFileUpload(data);
      };
      reader.readAsArrayBuffer(file);
    }
  };

  const { getRootProps, getInputProps } = useDropzone({ onDrop, accept: '.tif,.tiff' });

  return (
    <div {...getRootProps({ className: 'dropzone' })}>
      <input {...getInputProps()} />
      <p>Drag 'n' drop some raster files here, or click to select files</p>
    </div>
  );
};

export default RasterFileUpload;