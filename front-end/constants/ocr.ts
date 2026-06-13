export type OcrModelBadge = "new" | "offline";

export interface OcrModelOption {
  /** Value sent to the backend; must match backend OcrModel.ALL. */
  value: string;
  label: string;
  badge?: OcrModelBadge;
}

/** PaddleOCR parsing models the user can pick before parsing a document. */
export const OCR_MODELS: OcrModelOption[] = [
  { value: "PaddleOCR-VL-1.6", label: "PaddleOCR-VL-1.6", badge: "new" },
  { value: "PaddleOCR-VL-1.5", label: "PaddleOCR-VL-1.5", badge: "offline" },
  { value: "PP-OCRv6", label: "PP-OCRv6", badge: "new" },
  { value: "PP-OCRv5", label: "PP-OCRv5", badge: "offline" },
  { value: "PP-StructureV3", label: "PP-StructureV3" },
];

export const DEFAULT_OCR_MODEL = OCR_MODELS[0].value;
