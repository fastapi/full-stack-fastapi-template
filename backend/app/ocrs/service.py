import json
import logging
from typing import Any

import requests
from sqlmodel import Session

from app.aws.client import upload_file_to_r2
from app.core.config import settings
from app.files.crud import (
    create_file_job,
    get_file_job_by_file_id,
    update_file_job,
)
from app.files.models import File, FileJob
from app.files.schemas import FileJobCreate
from app.ocrs.constants import OcrJobStatus
from app.ocrs.dependencies import CurrentUser, SessionDep
from app.ocrs.schemas import OcrJobResponse, OcrSubmitResponse
from app.storages.service import increment_storage_stat
from app.utils import get_bytes_from_file_url

logger = logging.getLogger(__name__)

headers = {
    "Authorization": f"bearer {settings.OCR_API_TOKEN}",
    "Content-Type": "application/json",
}

optional_payload = {
    "useDocOrientationClassify": False,
    "useDocUnwarping": False,
    "useChartRecognition": False,
}

def post_ocr_jobs(
    session: Session, file: File, file_url: str, model: str | None = None
) -> tuple[bool, str | None]:
    """
    Submit an OCR job for the given file URL and create a FileJob record.
    Only posts the job — polling is handled separately.
    """

    selected_model = model or settings.OCR_MODEL
    payload = {
        "fileUrl": file_url,
        "model": selected_model,
        "optionalPayload": optional_payload,
    }

    raw = requests.post(str(settings.OCR_JOB_URL), json=payload, headers=headers)
    raw.raise_for_status()
    logger.info("Submitted OCR job for file %s, response: %s", file.id, raw.text)
    submit_response = OcrSubmitResponse.model_validate(raw.json())
    is_success = submit_response.is_success()
    if not is_success:
        create_file_job(
            session=session,
            file_job_in=FileJobCreate(
                file_id=file.id,
                state=OcrJobStatus.FAILED,
                model=selected_model,
                err_msg=submit_response.msg,
                ),
        )
        logger.error("Failed to submit OCR job for file %s: %s - %s", file.id, submit_response.code, submit_response.msg)
        return (False, None)

    job_id = submit_response.data.jobId
    logger.info("OCR job submitted successfully for file %s, job_id: %s", file.id, job_id)

    # Create a FileJob record to track this job
    create_file_job(
        session=session,
        file_job_in=FileJobCreate(
            job_id=job_id,
            file_id=file.id,
            state=OcrJobStatus.RUNNING,
            model=selected_model,
        ),
    )

    return (is_success, job_id)


def get_ocr_job_status(file: File, session: SessionDep, user: CurrentUser) -> str | None:
    """
    Poll the OCR API for job results. Reads job_id/state from the FileJob record.
    """
    file_job: FileJob | None = get_file_job_by_file_id(session=session, file_id=file.id)

    if not file_job:
        logger.error("File %s has no FileJob record", file.id)
        raise Exception("No FileJob record for this file")

    if file_job.state in (OcrJobStatus.DONE, OcrJobStatus.FAILED):
        return file_job.state

    req_headers = {"Authorization": f"bearer {settings.OCR_API_TOKEN}"}
    raw = requests.get(f"{settings.OCR_JOB_URL}/{file_job.job_id}", headers=req_headers)
    assert raw.status_code in (200, 404), f"OCR API returned unexpected status code {raw.status_code}"

    result: OcrJobResponse = OcrJobResponse.model_validate(raw.json())
    if not result.is_success():
        logger.error("Error fetching OCR job status for job_id %s: %s", file_job.job_id, result.msg)
        update_file_job(session=session, file_job=file_job, state=OcrJobStatus.FAILED, err_msg=result.msg)
        raise Exception(f"OCR API error: {result.msg}")

    state = result.data.state

    if state == OcrJobStatus.RUNNING and file_job.state == OcrJobStatus.PENDING:
        update_file_job(session=session, file_job=file_job, state=OcrJobStatus.RUNNING)

    elif state == OcrJobStatus.DONE:
        logger.info("OCR job %s completed successfully.", file_job.job_id)
        extract = result.data.extractProgress
        result_url = result.data.resultUrl
        update_file_job(
            session=session,
            file_job=file_job,
            state=OcrJobStatus.DONE,
            total_pages=extract.totalPages if extract else None,
            extracted_pages=extract.extractedPages if extract else None,
            json_url=result_url.jsonUrl if result_url else None,
            markdown_url=result_url.markdownUrl if result_url else None,
        )
        upload_ocr_job_result(user=user, file=file, result=result, session=session)

    elif state == OcrJobStatus.FAILED:
        logger.error("OCR job %s failed: %s", file_job.job_id, result.data.errorMsg)
        update_file_job(session=session, file_job=file_job, state=OcrJobStatus.FAILED, err_msg=result.data.errorMsg)

    return state


def fetch_ocr_table_pages(json_url: str) -> list[str]:
    """
    Fetch the parsed OCR result from its data URL (``json_url``) and return the
    extracted table(s) for each page as HTML — the same table data the download
    endpoint turns into a spreadsheet (see ``app.files.utils``).

    The result file is JSON Lines — one JSON record per page. Tables live under
    ``result.layoutParsingResults[*].prunedResult.parsing_res_list`` as blocks
    whose ``block_label`` is ``"table"`` and whose ``block_content`` is HTML.
    """
    raw = get_bytes_from_file_url(json_url).decode("utf-8")
    pages: list[str] = []
    for record in _parse_result_records(raw):
        html = _extract_tables(record)
        if html.strip():
            pages.append(html)
    return pages


def _parse_result_records(raw: str) -> list[Any]:
    """Parse the result payload as a single JSON value or as JSON Lines."""
    text = raw.strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, list) else [parsed]
    except json.JSONDecodeError:
        pass

    records: list[Any] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            logger.warning("Skipping malformed OCR result line")
    return records


def _extract_tables(record: Any) -> str:
    """Pull the table block(s) out of one page record as HTML.

    Mirrors the table lookup in ``app.files.utils.extract_tables_from_ocr``: each
    record wraps its payload under ``result``, whose ``layoutParsingResults`` hold
    ``prunedResult.parsing_res_list`` blocks; table blocks carry their HTML in
    ``block_content``.
    """
    if not isinstance(record, dict):
        return ""
    if isinstance(record.get("result"), dict):
        record = record["result"]
    results = record.get("layoutParsingResults") or record.get("ocrResults") or [record]
    if not isinstance(results, list):
        results = [results]

    tables: list[str] = []
    for item in results:
        if not isinstance(item, dict):
            continue
        pruned = item.get("prunedResult") if isinstance(item.get("prunedResult"), dict) else {}
        for block in pruned.get("parsing_res_list", []):
            if not isinstance(block, dict) or block.get("block_label") != "table":
                continue
            content = block.get("block_content")
            if isinstance(content, str) and content.strip():
                tables.append(content)
    return "\n".join(tables)


def upload_ocr_job_result(user: CurrentUser, file: File, result: OcrJobResponse, session: SessionDep):
    key = f"{user.email}/{file.id}/result.json"
    (json_url, md_url) = (result.data.resultUrl.jsonUrl, result.data.resultUrl.markdownUrl) if result.data.resultUrl else (None, None)
    logger.info(f"Uploading OCR job result for file {file.id} to R2, json_url: {json_url}, md_url: {md_url}")
    if json_url:
        upload_file_to_r2(key=key, data=get_bytes_from_file_url(json_url), content_type="application/json")

    increment_storage_stat(
        session=session,
        user_id=user.id,
        size_delta=file.size,
        total_pages_delta=result.data.extractProgress.extractedPages,  # ty:ignore[unresolved-attribute]
        file_count_delta=1
    )
