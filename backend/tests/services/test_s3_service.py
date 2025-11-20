import io
import uuid
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from PIL import Image

from app.services.s3_service import S3Service
from app.core.config import settings
from tests.utils.image import create_test_image_bytes


class TestS3Service:
    """Test suite for S3Service."""

    def setup_method(self):
        """Set up test fixtures."""
        # Mock settings
        self.mock_settings = MagicMock()
        self.mock_settings.AWS_ACCESS_KEY_ID = "test-access-key"
        self.mock_settings.AWS_SECRET_ACCESS_KEY = "test-secret-key"
        self.mock_settings.AWS_REGION = "us-east-1"
        self.mock_settings.AWS_S3_BUCKET = "test-bucket"
        self.mock_settings.AWS_CLOUDFRONT_DOMAIN = "test.cloudfront.net"

    @patch('app.services.s3_service.settings')
    @patch('app.services.s3_service.boto3')
    def test_s3_service_initialization(self, mock_boto3, mock_settings):
        """Test S3Service initialization."""
        mock_settings.AWS_ACCESS_KEY_ID = "test-key"
        mock_settings.AWS_SECRET_ACCESS_KEY = "test-secret"
        mock_settings.AWS_REGION = "us-east-1"
        mock_settings.AWS_S3_BUCKET = "test-bucket"
        mock_settings.AWS_CLOUDFRONT_DOMAIN = None

        service = S3Service()

        mock_boto3.client.assert_called_once_with(
            's3',
            aws_access_key_id="test-key",
            aws_secret_access_key="test-secret",
            region_name="us-east-1"
        )

        assert service.bucket_name == "test-bucket"
        assert service.cloudfront_domain is None

    def test_generate_s3_key(self):
        """Test S3 key generation."""
        service = S3Service()

        # Test basic filename
        s3_key = service._generate_s3_key("test.jpg")
        assert s3_key.startswith("images/")
        assert s3_key.endswith(".jpg")
        assert len(s3_key.split('/')[-1]) > 10  # Should have UUID

        # Test with custom prefix
        s3_key = service._generate_s3_key("test.jpg", prefix="custom")
        assert s3_key.startswith("custom/")
        assert s3_key.endswith(".jpg")

        # Test with different extensions
        s3_key = service._generate_s3_key("test.png", prefix="variants/large")
        assert s3_key.startswith("variants/large/")
        assert s3_key.endswith(".png")

    @patch('app.services.s3_service.settings')
    def test_get_public_url_without_cloudfront(self, mock_settings):
        """Test getting public URL without CloudFront."""
        mock_settings.AWS_REGION = "us-east-1"
        service = S3Service()
        service.cloudfront_domain = None
        service.bucket_name = "test-bucket"

        s3_key = "images/test.jpg"
        url = service._get_public_url(s3_key)

        expected_url = f"https://test-bucket.s3.us-east-1.amazonaws.com/{s3_key}"
        assert url == expected_url

    def test_get_public_url_with_cloudfront(self):
        """Test getting public URL with CloudFront."""
        service = S3Service()
        service.cloudfront_domain = "test.cloudfront.net"

        s3_key = "images/test.jpg"
        url = service._get_public_url(s3_key)

        expected_url = f"https://test.cloudfront.net/{s3_key}"
        assert url == expected_url

    @pytest.mark.asyncio
    @patch('app.services.s3_service.boto3')
    async def test_upload_file_success(self, mock_boto3):
        """Test successful file upload to S3."""
        # Mock S3 client
        mock_s3_client = MagicMock()
        mock_boto3.client.return_value = mock_s3_client

        # Mock settings
        with patch('app.services.s3_service.settings') as mock_settings:
            mock_settings.AWS_ACCESS_KEY_ID = "test-key"
            mock_settings.AWS_SECRET_ACCESS_KEY = "test-secret"
            mock_settings.AWS_REGION = "us-east-1"
            mock_settings.AWS_S3_BUCKET = "test-bucket"
            mock_settings.AWS_CLOUDFRONT_DOMAIN = None

            service = S3Service()

            # Test upload
            file_content = create_test_image_bytes()
            result = await service.upload_file(
                file_content=file_content,
                filename="test.jpg",
                content_type="image/jpeg"
            )

            # Verify S3 client was called correctly
            mock_s3_client.upload_fileobj.assert_called_once()

            # Check the call arguments
            call_args = mock_s3_client.upload_fileobj.call_args
            assert call_args[1]['Bucket'] == "test-bucket"
            assert call_args[1]['ExtraArgs']['ContentType'] == "image/jpeg"
            assert call_args[1]['ExtraArgs']['ServerSideEncryption'] == "AES256"

            # Check result
            assert 's3_key' in result
            assert 's3_url' in result
            assert 's3_bucket' in result
            assert 'file_size' in result
            assert result['s3_bucket'] == "test-bucket"
            assert result['file_size'] == len(file_content)

    @pytest.mark.asyncio
    @patch('app.services.s3_service.boto3')
    async def test_upload_file_no_such_bucket(self, mock_boto3):
        """Test upload when S3 bucket doesn't exist."""
        # Mock S3 client to raise NoSuchBucket error
        mock_s3_client = MagicMock()
        error_response = {'Error': {'Code': 'NoSuchBucket'}}
        mock_s3_client.upload_fileobj.side_effect = ClientError(error_response, 'UploadFile')
        mock_boto3.client.return_value = mock_s3_client

        with patch('app.services.s3_service.settings') as mock_settings:
            mock_settings.AWS_ACCESS_KEY_ID = "test-key"
            mock_settings.AWS_SECRET_ACCESS_KEY = "test-secret"
            mock_settings.AWS_REGION = "us-east-1"
            mock_settings.AWS_S3_BUCKET = "nonexistent-bucket"
            mock_settings.AWS_CLOUDFRONT_DOMAIN = None

            service = S3Service()

            file_content = create_test_image_bytes()

            with pytest.raises(Exception) as exc_info:
                await service.upload_file(
                    file_content=file_content,
                    filename="test.jpg",
                    content_type="image/jpeg"
                )

            assert "S3 bucket 'nonexistent-bucket' does not exist" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('app.services.s3_service.boto3')
    async def test_upload_file_access_denied(self, mock_boto3):
        """Test upload when access is denied."""
        mock_s3_client = MagicMock()
        error_response = {'Error': {'Code': 'AccessDenied'}}
        mock_s3_client.upload_fileobj.side_effect = ClientError(error_response, 'UploadFile')
        mock_boto3.client.return_value = mock_s3_client

        with patch('app.services.s3_service.settings') as mock_settings:
            mock_settings.AWS_ACCESS_KEY_ID = "test-key"
            mock_settings.AWS_SECRET_ACCESS_KEY = "test-secret"
            mock_settings.AWS_REGION = "us-east-1"
            mock_settings.AWS_S3_BUCKET = "restricted-bucket"
            mock_settings.AWS_CLOUDFRONT_DOMAIN = None

            service = S3Service()

            file_content = create_test_image_bytes()

            with pytest.raises(Exception) as exc_info:
                await service.upload_file(
                    file_content=file_content,
                    filename="test.jpg",
                    content_type="image/jpeg"
                )

            assert "Access denied to S3 bucket" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('app.services.s3_service.boto3')
    async def test_upload_file_no_credentials(self, mock_boto3):
        """Test upload when AWS credentials are missing."""
        mock_s3_client = MagicMock()
        mock_s3_client.upload_fileobj.side_effect = NoCredentialsError()
        mock_boto3.client.return_value = mock_s3_client

        with patch('app.services.s3_service.settings') as mock_settings:
            mock_settings.AWS_ACCESS_KEY_ID = "wrong-key"
            mock_settings.AWS_SECRET_ACCESS_KEY = "wrong-secret"
            mock_settings.AWS_REGION = "us-east-1"
            mock_settings.AWS_S3_BUCKET = "test-bucket"
            mock_settings.AWS_CLOUDFRONT_DOMAIN = None

            service = S3Service()

            file_content = create_test_image_bytes()

            with pytest.raises(Exception) as exc_info:
                await service.upload_file(
                    file_content=file_content,
                    filename="test.jpg",
                    content_type="image/jpeg"
                )

            assert "AWS credentials not found" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('app.services.s3_service.boto3')
    async def test_upload_image_variants(self, mock_boto3):
        """Test uploading image variants."""
        from PIL import Image

        mock_s3_client = MagicMock()
        mock_boto3.client.return_value = mock_s3_client

        # Mock successful upload responses
        mock_s3_client.upload_fileobj.return_value = None

        with patch('app.services.s3_service.settings') as mock_settings:
            mock_settings.AWS_ACCESS_KEY_ID = "test-key"
            mock_settings.AWS_SECRET_ACCESS_KEY = "test-secret"
            mock_settings.AWS_REGION = "us-east-1"
            mock_settings.AWS_S3_BUCKET = "test-bucket"
            mock_settings.AWS_CLOUDFRONT_DOMAIN = None

            service = S3Service()

            # Create test image
            img = Image.new('RGB', (800, 600), color='red')
            original_filename = "test_image.jpg"

            variant_types = [
                {'type': 'large', 'size': (1200, 1200), 'quality': 85, 'format': 'jpeg'},
                {'type': 'medium', 'size': (800, 800), 'quality': 85, 'format': 'jpeg'},
                {'type': 'thumb', 'size': (300, 300), 'quality': 75, 'format': 'jpeg'}
            ]

            variants = await service.upload_image_variants(
                image=img,
                original_filename=original_filename,
                variant_types=variant_types
            )

            # Verify all variants were created
            assert len(variants) == 3

            # Check S3 client was called for each variant
            assert mock_s3_client.upload_fileobj.call_count == 3

            # Verify variant structure
            for variant in variants:
                assert 'variant_type' in variant
                assert 'width' in variant
                assert 'height' in variant
                assert 'file_size' in variant
                assert 's3_bucket' in variant
                assert 's3_key' in variant
                assert 's3_url' in variant
                assert 'quality' in variant
                assert 'format' in variant

                assert variant['s3_bucket'] == "test-bucket"
                assert variant['file_size'] > 0
                assert variant['variant_type'] in variant['s3_key']

            # Verify variant types are correct
            variant_types_found = {v['variant_type'] for v in variants}
            assert variant_types_found == {'large', 'medium', 'thumb'}

    @pytest.mark.asyncio
    @patch('app.services.s3_service.boto3')
    async def test_delete_file_success(self, mock_boto3):
        """Test successful file deletion from S3."""
        mock_s3_client = MagicMock()
        mock_boto3.client.return_value = mock_s3_client

        with patch('app.services.s3_service.settings') as mock_settings:
            mock_settings.AWS_ACCESS_KEY_ID = "test-key"
            mock_settings.AWS_SECRET_ACCESS_KEY = "test-secret"
            mock_settings.AWS_REGION = "us-east-1"
            mock_settings.AWS_S3_BUCKET = "test-bucket"
            mock_settings.AWS_CLOUDFRONT_DOMAIN = None

            service = S3Service()

            s3_key = "images/test.jpg"
            result = await service.delete_file(s3_key)

            mock_s3_client.delete_object.assert_called_once_with(
                Bucket="test-bucket",
                Key=s3_key
            )
            assert result is True

    @pytest.mark.asyncio
    @patch('app.services.s3_service.boto3')
    async def test_delete_file_failure(self, mock_boto3):
        """Test file deletion failure."""
        mock_s3_client = MagicMock()
        mock_s3_client.delete_object.side_effect = Exception("Delete failed")
        mock_boto3.client.return_value = mock_s3_client

        with patch('app.services.s3_service.settings') as mock_settings:
            mock_settings.AWS_ACCESS_KEY_ID = "test-key"
            mock_settings.AWS_SECRET_ACCESS_KEY = "test-secret"
            mock_settings.AWS_REGION = "us-east-1"
            mock_settings.AWS_S3_BUCKET = "test-bucket"
            mock_settings.AWS_CLOUDFRONT_DOMAIN = None

            service = S3Service()

            s3_key = "images/test.jpg"
            result = await service.delete_file(s3_key)

            mock_s3_client.delete_object.assert_called_once_with(
                Bucket="test-bucket",
                Key=s3_key
            )
            assert result is False

    @pytest.mark.asyncio
    @patch('app.services.s3_service.boto3')
    async def test_generate_presigned_url(self, mock_boto3):
        """Test generating presigned URL."""
        mock_s3_client = MagicMock()
        mock_s3_client.generate_presigned_url.return_value = "https://presigned-url.com"
        mock_boto3.client.return_value = mock_s3_client

        with patch('app.services.s3_service.settings') as mock_settings:
            mock_settings.AWS_ACCESS_KEY_ID = "test-key"
            mock_settings.AWS_SECRET_ACCESS_KEY = "test-secret"
            mock_settings.AWS_REGION = "us-east-1"
            mock_settings.AWS_S3_BUCKET = "test-bucket"
            mock_settings.AWS_CLOUDFRONT_DOMAIN = None

            service = S3Service()

            s3_key = "images/test.jpg"
            presigned_url = await service.generate_presigned_url(s3_key)

            mock_s3_client.generate_presigned_url.assert_called_once_with(
                'get_object',
                Params={
                    'Bucket': "test-bucket",
                    'Key': s3_key
                },
                ExpiresIn=3600
            )
            assert presigned_url == "https://presigned-url.com"

    @pytest.mark.asyncio
    @patch('app.services.s3_service.boto3')
    async def test_check_file_exists(self, mock_boto3):
        """Test checking if file exists in S3."""
        mock_s3_client = MagicMock()
        mock_boto3.client.return_value = mock_s3_client

        with patch('app.services.s3_service.settings') as mock_settings:
            mock_settings.AWS_ACCESS_KEY_ID = "test-key"
            mock_settings.AWS_SECRET_ACCESS_KEY = "test-secret"
            mock_settings.AWS_REGION = "us-east-1"
            mock_settings.AWS_S3_BUCKET = "test-bucket"
            mock_settings.AWS_CLOUDFRONT_DOMAIN = None

            service = S3Service()

            # Test file exists
            s3_key = "images/test.jpg"
            mock_s3_client.head_object.return_value = {"ContentLength": 1024}

            result = await service.check_file_exists(s3_key)
            assert result is True

            mock_s3_client.head_object.assert_called_once_with(
                Bucket="test-bucket",
                Key=s3_key
            )

            # Test file doesn't exist
            from botocore.exceptions import ClientError
            error_response = {'Error': {'Code': '404'}}
            mock_s3_client.head_object.side_effect = ClientError(error_response, 'HeadObject')

            result = await service.check_file_exists(s3_key)
            assert result is False

    @pytest.mark.asyncio
    @patch('app.services.s3_service.boto3')
    async def test_check_file_exists_error(self, mock_boto3):
        """Test checking file existence with error."""
        mock_s3_client = MagicMock()
        mock_boto3.client.return_value = mock_s3_client

        with patch('app.services.s3_service.settings') as mock_settings:
            mock_settings.AWS_ACCESS_KEY_ID = "test-key"
            mock_settings.AWS_SECRET_ACCESS_KEY = "test-secret"
            mock_settings.AWS_REGION = "us-east-1"
            mock_settings.AWS_S3_BUCKET = "test-bucket"
            mock_settings.AWS_CLOUDFRONT_DOMAIN = None

            service = S3Service()

            s3_key = "images/test.jpg"
            mock_s3_client.head_object.side_effect = Exception("Connection error")

            result = await service.check_file_exists(s3_key)
            assert result is False