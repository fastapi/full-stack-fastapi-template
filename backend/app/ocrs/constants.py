class OcrJobStatus:
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class OcrModel:
    """Supported PaddleOCR parsing models (values sent to the OCR API)."""

    PADDLEOCR_VL_1_6 = "PaddleOCR-VL-1.6"
    PADDLEOCR_VL_1_5 = "PaddleOCR-VL-1.5"
    PP_OCRV6 = "PP-OCRv6"
    PP_OCRV5 = "PP-OCRv5"
    PP_STRUCTURE_V3 = "PP-StructureV3"

    ALL: set[str] = {
        PADDLEOCR_VL_1_6,
        PADDLEOCR_VL_1_5,
        PP_OCRV6,
        PP_OCRV5,
        PP_STRUCTURE_V3,
    }
