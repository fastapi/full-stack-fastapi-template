from unittest.mock import MagicMock, patch

from app.core.extractors import chunk_text, extract_text_and_save_to_db


def test_extract_text_and_save_chunks_to_db() -> None:
    fake_text = "abcdefghij"
    fake_s3_key = "some-s3-key"
    fake_doc_id = "123e4567-e89b-12d3-a456-426614174000"

    mock_document = MagicMock()
    mock_document.id = fake_doc_id

    with patch(
        "app.core.extractors.extract_text_from_s3_file", return_value=fake_text
    ) as _, patch("app.core.extractors.Session") as session_class_mock, patch(
        "app.core.extractors.save_chunks_to_db"
    ) as save_chunks_mock:
        session_instance = MagicMock()
        session_class_mock.return_value.__enter__.return_value = session_instance
        session_instance.exec.return_value.first.return_value = mock_document

        # Run function
        extract_text_and_save_to_db(fake_s3_key, fake_doc_id)

        # Check chunking worked
        expected_chunks = chunk_text(fake_text)  # default chunk_size=1000
        save_chunks_mock.assert_called_once_with(
            session_instance, fake_doc_id, expected_chunks
        )
