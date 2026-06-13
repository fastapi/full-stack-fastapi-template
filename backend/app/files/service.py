import io
import json
from io import StringIO
from typing import Any

import pandas as pd
from google import genai
from pandas.core.frame import DataFrame
from sqlmodel import Session

from app.api_keys.crud import get_api_key_by_user
from app.files.crud import get_file_job_by_file_id
from app.files.dependencies import CurrentUser
from app.files.models import File, FileJob
from app.files.strategies import DOWNLOAD_STRATEGIES
from app.files.utils import get_df_from_result_json

model = "gemini-3-flash-preview"

user_instruction = (
    "Tôi muốn bạn đọc file này. Sau đó dựa vào nội dung để xác định giao dịch (Bạn phải tự xác định cột chứa nội dung giao dịch)"
    "này thuộc mã tài khoản kế toán nào (mã này được lấy từ thị trường Việt Nam). Sau đó trả ra "
    "cho tôi file mới có thêm cột mã tk, và tên tk ở cuối. Nếu nội dung chuyển khoản không chắc chắn, hãy bỏ trống\n\n"
    "Dưới đây là nội dung file (nguyên văn). Hãy trả lại CHÍNH XÁC NỘI DUNG file mới dưới dạng CSV hoặc plain text, "
    "không thêm giải thích, chú thích hay văn bản khác. Chỉ output nội dung file mới.\n\n"
)

def download_file(session: Session, file: File, type: str = "xlsx") -> tuple[bytes, str]:
    """
    Given a File record, download the file content from its URL and return bytes
    and a Content-Disposition header for the requested format.

    The format-specific conversion is delegated to a :class:`DownloadStrategy`
    looked up from ``DOWNLOAD_STRATEGIES``.

    Supported types: "xlsx", "csv", "json", "html".
    """
    strategy = DOWNLOAD_STRATEGIES.get(type)
    if strategy is None:
        raise ValueError(f"Unsupported file type requested: {type}")

    file_job = get_file_job_by_file_id(session=session, file_id=file.id)
    if not file_job or not file_job.json_url:
        raise ValueError("No OCR result available for this file yet.")

    df: DataFrame | None = get_df_from_result_json(file_job.json_url)
    if df is None:
        df = pd.DataFrame()

    safe_name = file.filename.rsplit(".", 1)[0] if "." in file.filename else file.filename
    data_bytes, content_disposition = strategy.convert(df, safe_name)

    return (data_bytes, content_disposition)

def get_preview_data(file_job: FileJob) -> tuple[list[str], list[dict[str, Any]]]:
    """Build the OCR result table for previewing.

    Fetches the parsed OCR result from the job's ``json_url`` and returns it as a
    ``(columns, rows)`` tuple: ``columns`` is the ordered list of headers and
    ``rows`` is the table content as JSON-serialisable ``{column: value}``
    records (``NaN`` values are normalised to ``None``). This is the same table
    the JSON download exports, returned inline rather than as a file.
    """
    df: DataFrame | None = get_df_from_result_json(file_job.json_url)
    if df is None:
        return [], []

    # Drop the internal page-tracking column used only for debugging exports.
    df = df.drop(columns=["__page__"], errors="ignore")

    columns = [str(col) for col in df.columns]
    # to_json normalises NaN/NaT to null and keeps unicode intact.
    rows = json.loads(df.to_json(orient="records", force_ascii=False) or "[]")

    return columns, rows


def get_gemini_response_for_file(input_path: str, output_path: str, *, model: str | None = None) -> None:
    """Read a local file (CSV or XLSX), send its contents to Gemini with the Vietnamese
    prompt, and write the model's returned contents into `output_path` as XLSX when
    the output filename ends with .xlsx.

    Behavior:
    - If input is .xlsx or .xls, read with pandas and convert to CSV text for the prompt.
    - Otherwise, read the file as text and include it verbatim.
    - The prompt explicitly asks Gemini to return only the new file contents (CSV/plain text).
    - If the output is requested as .xlsx, the function will attempt to parse the model's
      CSV/plain-text response back into a DataFrame and write it to Excel.
      If parsing fails, the raw response will be put into a single-cell Excel sheet.

    Prompt used (Vietnamese):
    "Tôi muốn bạn đọc file này. Sau đó dựa vào nội dung trong cột thứ 2 để xác định giao dịch này thuộc mã tài khoản kế toán nào (mã này được lấy từ thị trường Việt Nam). Sau đó trả ra cho tôi file mới có thêm cột mã tk, và tên tk ở cuối"

    Note: The GEMINI_API_KEY must be set in the environment for `genai.Client()` to authenticate.
    """

    client = genai.Client()

    if model is None:
        model = "gemini-3-flash-preview"

    # Load input file. If Excel, convert to CSV text to include in the prompt.
    file_ext = input_path.lower().rsplit('.', 1)[-1] if '.' in input_path else ''
    if file_ext in ("xlsx", "xls"):
        df_in = pd.read_excel(input_path)
        file_text = df_in.to_csv(index=False)
    else:
        # For non-excel files, read as text
        with open(input_path, encoding="utf-8") as f:
            file_text = f.read()

    # Build prompt that asks the model to return only the file contents (CSV/plain text)

    full_prompt = user_instruction + "---FILE-BEGIN---\n" + file_text + "\n---FILE-END---\n"

    # Send to Gemini
    response = client.models.generate_content(model=model, contents=full_prompt)
    resp_text = response.text or ""

    # If output path requests xlsx, try to parse response as CSV/plain text and write to Excel
    out_ext = output_path.lower().rsplit('.', 1)[-1] if '.' in output_path else ''
    if out_ext in ("xlsx", "xls"):
        try:
            df_out = pd.read_csv(StringIO(resp_text))
            df_out.to_excel(output_path, index=False, engine='openpyxl')
        except Exception:
            # Fallback: write the raw response into a single-cell sheet
            fallback_df = pd.DataFrame({"result": [resp_text]})
            fallback_df.to_excel(output_path, index=False, engine='openpyxl')
    else:
        # For non-xlsx output, write raw text
        with open(output_path, "w", encoding="utf-8") as out_f:
            out_f.write(resp_text)

def download_file_with_accounting_code(session: Session, file: File, user: CurrentUser) -> tuple[bytes, str]:
    """
    This is a placeholder for a future function that would download the file with an additional account code column.
    The implementation would likely involve calling `get_gemini_response_for_file` to get the modified file content,
    then returning the bytes and content disposition for that modified file.
    """
    api_key = get_api_key_by_user(session=session, user_id=user.id)  # type: ignore[call-arg]
    client = genai.Client(api_key=api_key.key)
    file_job = get_file_job_by_file_id(session=session, file_id=file.id)

    if not file_job or not file_job.json_url:
        raise ValueError("No OCR result available for this file yet.")

    df: DataFrame | None = get_df_from_result_json(file_job.json_url)
    if df is None:
        raise ValueError("No tables found in OCR result.")
    file_text = df.to_csv(index=False)

    full_prompt = user_instruction + "---FILE-BEGIN---\n" + file_text + "\n---FILE-END---\n"
    response = client.models.generate_content(model=model, contents=full_prompt)
    resp_text = response.text or ""

    df_out = pd.read_csv(StringIO(resp_text))
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:  # type: ignore[abstract]  # ty:ignore[invalid-argument-type]
        df_out.to_excel(writer, index=False, sheet_name="OCR Tables with Account Codes")

    return output.getvalue(), DOWNLOAD_STRATEGIES["xlsx"].get_content_disposition(f"{file.filename.rsplit('.', 1)[0]}_with_account_codes.xlsx")