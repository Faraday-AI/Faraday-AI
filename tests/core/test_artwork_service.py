import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.artwork_service import ArtworkService
import base64
from PIL import Image
import io

@pytest.fixture
def artwork_service():
    return ArtworkService()

@pytest.fixture
def mock_openai_response():
    return {
        "data": [
            {
                "url": "https://example.com/image1.png"
            },
            {
                "url": "https://example.com/image2.png"
            }
        ]
    }

@pytest.fixture
def mock_image():
    # Create a small test image
    img = Image.new('RGB', (100, 100), color='red')
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

@pytest.mark.asyncio
async def test_generate_artwork(artwork_service, mock_openai_response, mock_image):
    # Test artwork generation
    results = await artwork_service.generate_artwork(
        prompt="test prompt",
        size="1024x1024",
        style="natural",
        variations=2
    )
    
    # Verify results
    assert len(results) == 2
    assert all("image" in result for result in results)
    assert all("prompt" in result for result in results)
    assert all("style" in result for result in results)
    assert all("size" in result for result in results)
    assert all("url" in result for result in results)
    assert all("generated_at" in result for result in results)

@pytest.mark.asyncio
async def test_edit_artwork(artwork_service, mock_openai_response, mock_image):
    # Test artwork editing
    result = await artwork_service.edit_artwork(
        image_path="test_image.png",
        prompt="test edit",
        mask_path="test_mask.png"
    )
    
    # Verify result
    assert "image" in result
    assert "prompt" in result
    assert "url" in result
    assert "original_image" in result
    assert "mask_path" in result
    assert "edited_at" in result

@pytest.mark.asyncio
async def test_generate_variations(artwork_service, mock_openai_response, mock_image):
    # Test variation generation
    results = await artwork_service.generate_variations(
        image_path="test_image.png",
        variations=2
    )
    
    # Verify results
    assert len(results) == 2
    assert all("image" in result for result in results)
    assert all("url" in result for result in results)
    assert all("original_image" in result for result in results)
    assert all("generated_at" in result for result in results)

@pytest.mark.asyncio
async def test_generate_artwork_batch(artwork_service, mock_openai_response, mock_image):
    # Test batch generation
    prompts = ["prompt1", "prompt2"]
    results = await artwork_service.generate_artwork_batch(
        prompts=prompts,
        size="1024x1024",
        style="natural"
    )
    
    # Verify results
    assert len(results) == 2  # 2 prompts * 1 variation each
    assert all("image" in result for result in results)
    assert all("prompt" in result for result in results)
    assert all("style" in result for result in results)
    assert all("size" in result for result in results)
    assert all("url" in result for result in results)
    assert all("generated_at" in result for result in results)

@pytest.mark.asyncio
async def test_download_image_error(artwork_service):
    # Test error handling by directly testing the exception message
    with pytest.raises(Exception) as exc_info:
        # This will fail because we're not mocking the network call
        # but we can test that the method raises an exception
        await artwork_service.download_image("https://invalid-url-that-will-fail.com/image.png")
    
    # The actual error will be a connection error, but we can verify it's an exception
    assert "Cannot connect to host" in str(exc_info.value) or "Error downloading image" in str(exc_info.value) 
