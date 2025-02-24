# MCG Take-Home Assessment - Patient Care Management System

## Design

See the system design in [Excalidraw here](https://excalidraw.com/#json=4cLkV3RAlGQ95xFiVW1fY,QTeiqBvSWKEk77UItun2aA)

## Implementation

This is based on the [FastAPI full stack template](https://fastapi.tiangolo.com/project-generation/), started as a fork of that project.

It includes an API server based on Python and FastAPI, with an SQLModel ORM,
Pydantic type checking, connects to a PostgreSQL database with
migrations managed by Alembic, and creates AWS presigned URLs for attachment
uploads and downloads using `boto3`.

- Added SQLModel classes and associated Alembic migrations for Patient and Attachment tables
- Added configuration variables for setting AWS credentials for use by `boto3`
- Implemented `/patients/...` and `/attachments/...` API routes as specified in the "REST API Sketch" section of the [Design Document](https://excalidraw.com/#json=4cLkV3RAlGQ95xFiVW1fY,QTeiqBvSWKEk77UItun2aA)
- Implemented automated tests for all API routes based on `pytest` and the FastAPI TestClient.
- All patient and attachment APIs require a valid JWT authentication token present in the request headers.

AI coding assistants used in development: [GitHub Copilot](https://github.com/features/copilot) and [Aider](https://aider.chat) connected to Claude 3.5-sonnet. Aider proved quite adept at writing tests.

### Design Notes

Publicly visible patient and attachment IDs are non-sequential UUIDs, which is a security best practice.

File uploads and downloads go directly to and from AWS S3 via presigned URLs, bypassing the application server, which greatly reduces load on the application server and improves upload and download performance.

### APIs Implemented

#### Authentication and User Management

Fully functional user management and authentication APIs are
included in the base project, including password reset emails.
See the template documentation for details.

#### POST `/api/v1/patients`

Creates a new patient record.

    headers: user's JWT token
    response: JSON representation of new patient record

#### GET `/api/v1/patients/<patient_uuid>`

Gets the details of a single patient.

    request headers: user's JWT token
    response: JSON representation of patient

#### GET `/api/v1/patients?<query>`

Retrieves patient records.

    request headers: user's JWT token
    query parameters (optional):
        - name_text
        - name_exact
        - history_text 
        - has_attachment_mime_type
        - skip, limit (for paging)
    response:
        JSON array of matching patient records,
        filtered according to query params.

#### POST `/api/v1/attachments`

Creates a new attachment.

    request headers:
        user's JWT token
        - Content-Type: <mime_type>
    body:
        - file_name
    response:
        - id
        - upload_url: presigned upload URL

Note: after creating the attachment, the client should upload the file
itself to the provided presigned AWS S3 URL.

#### GET `/api/v1/attachments/<attachment_uuid>/content`

Retrieves attachment content

    request headers: user's JWT token
    response:
        302 redirect to presigned blob storage URL

NOTE: AWS presigned URL generation supports setting the Content-Disposition header (and thus the downloaded file name) that will be provided to the client, which is what is implemented here.

## License

This is a fork of the [FastAPI full stack template](https://fastapi.tiangolo.com/project-generation/) and is licensed under the terms of the MIT license.
