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
    with patch('openai.Image.acreate', new_callable=AsyncMock) as mock_create, \
         patch('aiohttp.ClientSession.get', new_callable=AsyncMock) as mock_get:
        
        # Setup mocks
        mock_create.return_value = mock_openai_response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.read.return_value = mock_image
        mock_get.return_value.__aenter__.return_value = mock_response
        
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
        
        # Verify OpenAI API call
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert call_args["prompt"] == "test prompt in natural style"
        assert call_args["n"] == 2
        assert call_args["size"] == "1024x1024"

@pytest.mark.asyncio
async def test_edit_artwork(artwork_service, mock_openai_response, mock_image):
    with patch('openai.Image.acreate_edit', new_callable=AsyncMock) as mock_edit, \
         patch('aiohttp.ClientSession.get', new_callable=AsyncMock) as mock_get, \
         patch('PIL.Image.open') as mock_pil_open:
        
        # Setup mocks
        mock_edit.return_value = mock_openai_response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.read.return_value = mock_image
        mock_get.return_value.__aenter__.return_value = mock_response
        mock_pil_open.return_value = MagicMock()
        
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
        
        # Verify OpenAI API call
        mock_edit.assert_called_once()
        call_args = mock_edit.call_args[1]
        assert call_args["prompt"] == "test edit"
        assert call_args["n"] == 1
        assert call_args["size"] == "1024x1024"

@pytest.mark.asyncio
async def test_generate_variations(artwork_service, mock_openai_response, mock_image):
    with patch('openai.Image.acreate_variation', new_callable=AsyncMock) as mock_variation, \
         patch('aiohttp.ClientSession.get', new_callable=AsyncMock) as mock_get, \
         patch('PIL.Image.open') as mock_pil_open:
        
        # Setup mocks
        mock_variation.return_value = mock_openai_response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.read.return_value = mock_image
        mock_get.return_value.__aenter__.return_value = mock_response
        mock_pil_open.return_value = MagicMock()
        
        # Test variation generation
        results = await artwork_service.generate_variations(
            image_path="test_image.png",
            variations=2
        )
        
        # Verify results
        assert len(results) == 2
        assert all("image" in result for result in results)
        assert all("url" in result for result in results)
        
        # Verify OpenAI API call
        mock_variation.assert_called_once()
        call_args = mock_variation.call_args[1]
        assert call_args["n"] == 2
        assert call_args["size"] == "1024x1024"

@pytest.mark.asyncio
async def test_generate_artwork_batch(artwork_service, mock_openai_response, mock_image):
    with patch('openai.Image.acreate', new_callable=AsyncMock) as mock_create, \
         patch('aiohttp.ClientSession.get', new_callable=AsyncMock) as mock_get:
        
        # Setup mocks
        mock_create.return_value = mock_openai_response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.read.return_value = mock_image
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Test batch generation
        prompts = ["prompt1", "prompt2"]
        results = await artwork_service.generate_artwork_batch(
            prompts=prompts,
            size="1024x1024",
            style="natural"
        )
        
        # Verify results
        assert len(results) == 4  # 2 prompts * 2 variations
        assert all("image" in result for result in results)
        assert all("prompt" in result for result in results)
        
        # Verify OpenAI API calls
        assert mock_create.call_count == 2
        for i, call in enumerate(mock_create.call_args_list):
            call_args = call[1]
            assert call_args["prompt"] == f"{prompts[i]} in natural style"
            assert call_args["n"] == 1
            assert call_args["size"] == "1024x1024"

@pytest.mark.asyncio
async def test_download_image_error(artwork_service):
    with patch('aiohttp.ClientSession.get', new_callable=AsyncMock) as mock_get:
        # Setup mock to simulate failed download
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Test error handling
        with pytest.raises(Exception) as exc_info:
            await artwork_service._download_image("https://example.com/image.png")
        
        assert "Failed to download image: 404" in str(exc_info.value) 
