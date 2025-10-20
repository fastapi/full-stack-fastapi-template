
import DocumentDropzoneComponent from "@/components/form/form-elements/DocumentDropZone";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Upload Page",
  description: "This is Next.js Upload Page",
};

export default function Upload() {
  return <DocumentDropzoneComponent />;
}
