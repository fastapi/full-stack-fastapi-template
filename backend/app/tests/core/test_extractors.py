from unittest.mock import MagicMock, patch
from app.core.extractors import extract_text_and_save_to_db
from app.models import Document

# def test_extract_text_and_save_to_db_success() -> None:
#     fake_text = "Extracted text content"
#     fake_s3_url = "s3://bucket/path/to/file.pdf"
#     fake_doc_id = "123e4567-e89b-12d3-a456-426614174000"

#     # Mock document object
#     mock_document = Document(id=fake_doc_id)
    
#     with patch("app.core.extractors.extract_text_from_file", return_value=fake_text) as extract_mock, \
#          patch("app.core.extractors.Session") as session_class_mock:

#         # Mock session and query chain
#         session_instance = MagicMock()
#         session_class_mock.return_value.__enter__.return_value = session_instance
#         session_instance.query.return_value.filter.return_value.first.return_value = mock_document

#         # Run the function
#         extract_text_and_save_to_db(fake_s3_url, fake_doc_id)

#         # Assertions
#         extract_mock.assert_called_once_with(fake_s3_url)
#         session_instance.query.assert_called_once()
#         assert mock_document.extracted_text == fake_text
#         session_instance.commit.assert_called_once()

def test_extract_text_and_save_to_db_success() -> None:
    fake_text = "Extracted text content"
    fake_s3_url = "s3://bucket/path/to/file.pdf"
    fake_doc_id = "123e4567-e89b-12d3-a456-426614174000"

    mock_document = Document(id=fake_doc_id)

    with patch("app.core.extractors.extract_text_from_file", return_value=fake_text) as extract_mock, \
         patch("app.core.extractors.Session") as session_class_mock:

        # Mock session context manager
        session_instance = MagicMock()
        session_class_mock.return_value.__enter__.return_value = session_instance

        # Mock session.exec(...).first()
        mock_exec_result = MagicMock()
        mock_exec_result.first.return_value = mock_document
        session_instance.exec.return_value = mock_exec_result

        # Run the function
        extract_text_and_save_to_db(fake_s3_url, fake_doc_id)

        # Assertions
        extract_mock.assert_called_once_with(fake_s3_url)
        session_instance.exec.assert_called_once()
        assert mock_document.extracted_text == fake_text
        session_instance.commit.assert_called_once()