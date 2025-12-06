from typing import Dict, List, Optional
from openai import OpenAI, AsyncOpenAI
from app.core.config import get_settings
import logging
import base64
import io
from PIL import Image
import asyncio

logger = logging.getLogger(__name__)

class ArtworkService:
    def __init__(self):
        self.settings = get_settings()
        # Use new OpenAI client (supports DALL-E 3)
        self.client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)

    async def generate_artwork(self, prompt: str, size: str = "1024x1024", 
                             style: str = "natural", variations: int = 1,
                             model: str = "dall-e-3", quality: str = "standard") -> List[Dict]:
        """
        Generate artwork using DALL-E 3 (latest) or DALL-E 2.
        
        Args:
            prompt: Description of the artwork to generate
            size: Image size 
                - DALL-E 3: "1024x1024", "1792x1024", "1024x1792"
                - DALL-E 2: "256x256", "512x512", "1024x1024"
            style: Art style (natural, abstract, cartoon, etc.)
            variations: Number of variations (DALL-E 3: max 1, DALL-E 2: max 10)
            model: "dall-e-3" (default, better quality) or "dall-e-2" (faster, cheaper)
            quality: For DALL-E 3: "standard" or "hd" (higher quality, more expensive)
            
        Returns:
            List of Dicts containing generated images and metadata
        """
        try:
            # Enhance prompt with style
            enhanced_prompt = f"{prompt} in {style} style"
            
            # DALL-E 3 only supports 1 image per request, but higher quality
            if model == "dall-e-3":
                # DALL-E 3: Better quality, but only 1 image per request
                n = 1
                # DALL-E 3 size options
                valid_sizes = ["1024x1024", "1792x1024", "1024x1792"]
                if size not in valid_sizes:
                    size = "1024x1024"
            else:
                # DALL-E 2: Can generate multiple, but lower quality
                n = min(variations, 10)
                valid_sizes = ["256x256", "512x512", "1024x1024"]
                if size not in valid_sizes:
                    size = "1024x1024"
            
            # Generate images using new OpenAI API
            response = await self.client.images.generate(
                model=model,
                prompt=enhanced_prompt,
                n=n,
                size=size,
                quality=quality if model == "dall-e-3" else None
            )
            
            results = []
            # Handle both new API format (response.data) and old format
            image_list = response.data if hasattr(response, 'data') else response.get("data", [])
            
            for image_data in image_list:
                # New API returns ImageResponse objects, old API returns dicts
                if hasattr(image_data, 'url'):
                    image_url = image_data.url
                    revised_prompt = getattr(image_data, 'revised_prompt', None)  # DALL-E 3 provides this
                else:
                    image_url = image_data.get("url")
                    revised_prompt = None
                
                image = await self._download_image(image_url)
                
                # Convert to base64 for storage/transmission
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                results.append({
                    "image": img_str,
                    "prompt": enhanced_prompt,
                    "revised_prompt": revised_prompt,  # DALL-E 3's improved prompt
                    "style": style,
                    "size": size,
                    "model": model,
                    "quality": quality if model == "dall-e-3" else None,
                    "url": image_url
                })
            
            # If DALL-E 3 and user requested multiple variations, generate more
            if model == "dall-e-3" and variations > 1:
                for i in range(1, min(variations, 4)):  # DALL-E 3: max 4 requests per minute
                    try:
                        # Slight variation in prompt for diversity
                        variation_prompt = f"{enhanced_prompt}, variation {i+1}"
                        var_response = await self.client.images.generate(
                            model=model,
                            prompt=variation_prompt,
                            n=1,
                            size=size,
                            quality=quality
                        )
                        var_image_data = var_response.data[0]
                        var_image = await self._download_image(var_image_data.url)
                        buffered = io.BytesIO()
                        var_image.save(buffered, format="PNG")
                        img_str = base64.b64encode(buffered.getvalue()).decode()
                        
                        results.append({
                            "image": img_str,
                            "prompt": variation_prompt,
                            "revised_prompt": getattr(var_image_data, 'revised_prompt', None),
                            "style": style,
                            "size": size,
                            "model": model,
                            "quality": quality,
                            "url": var_image_data.url
                        })
                        # Rate limiting: wait between requests
                        await asyncio.sleep(1)
                    except Exception as e:
                        logger.warning(f"Could not generate variation {i+1}: {str(e)}")
                        break
            
            return results
            
        except Exception as e:
            logger.error(f"Error generating artwork: {str(e)}")
            raise

    async def edit_artwork(self, image_path: str, prompt: str, 
                          mask_path: Optional[str] = None, 
                          model: str = "dall-e-2") -> Dict:
        """
        Edit existing artwork using DALL-E 2 (DALL-E 3 doesn't support editing yet).
        
        Args:
            image_path: Path to the original image
            prompt: Description of the changes to make
            mask_path: Optional path to a mask image
            model: "dall-e-2" (only model that supports editing)
            
        Returns:
            Dict containing the edited image and metadata
        """
        try:
            # Open and prepare the image
            image = Image.open(image_path)
            
            # Prepare the mask if provided
            mask = None
            if mask_path:
                mask = Image.open(mask_path)
            
            # DALL-E 2 only supports editing
            # Note: New API format for image editing
            with open(image_path, 'rb') as img_file:
                image_bytes = img_file.read()
            
            mask_bytes = None
            if mask_path:
                with open(mask_path, 'rb') as mask_file:
                    mask_bytes = mask_file.read()
            
            # Create the edit using new API
            response = await self.client.images.edit(
                image=image_bytes,
                mask=mask_bytes,
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            
            # Process the result (handle both new and old API formats)
            if hasattr(response, 'data'):
                image_url = response.data[0].url
            else:
                image_url = response["data"][0]["url"]
            
            edited_image = await self._download_image(image_url)
            
            # Convert to base64
            buffered = io.BytesIO()
            edited_image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                "image": img_str,
                "prompt": prompt,
                "model": model,
                "url": image_url
            }
            
        except Exception as e:
            logger.error(f"Error editing artwork: {str(e)}")
            raise

    async def generate_variations(self, image_path: str, variations: int = 3,
                                  model: str = "dall-e-2") -> List[Dict]:
        """
        Generate variations of an existing image (DALL-E 2 only).
        
        Args:
            image_path: Path to the original image
            variations: Number of variations to generate (max 10)
            model: "dall-e-2" (only model that supports variations)
            
        Returns:
            List of Dicts containing the variations
        """
        try:
            # Read image bytes
            with open(image_path, 'rb') as img_file:
                image_bytes = img_file.read()
            
            # Generate variations using new API
            response = await self.client.images.create_variation(
                image=image_bytes,
                n=min(variations, 10),
                size="1024x1024"
            )
            
            results = []
            # Handle both new API format and old format
            image_list = response.data if hasattr(response, 'data') else response.get("data", [])
            
            for image_data in image_list:
                if hasattr(image_data, 'url'):
                    image_url = image_data.url
                else:
                    image_url = image_data.get("url")
                
                variation = await self._download_image(image_url)
                
                # Convert to base64
                buffered = io.BytesIO()
                variation.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                results.append({
                    "image": img_str,
                    "model": model,
                    "url": image_url
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error generating variations: {str(e)}")
            raise

    async def _download_image(self, url: str) -> Image.Image:
        """Download an image from a URL."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        return Image.open(io.BytesIO(image_data))
                    else:
                        raise Exception(f"Failed to download image: {response.status}")
        except Exception as e:
            logger.error(f"Error downloading image: {str(e)}")
            raise

    async def generate_artwork_batch(self, prompts: List[str], 
                                   size: str = "1024x1024", 
                                   style: str = "natural",
                                   model: str = "dall-e-3",
                                   quality: str = "standard") -> List[Dict]:
        """
        Generate multiple artworks in parallel.
        
        Args:
            prompts: List of prompts to generate artwork from
            size: Image size
            style: Art style
            model: "dall-e-3" or "dall-e-2"
            quality: For DALL-E 3: "standard" or "hd"
            
        Returns:
            List of Dicts containing all generated images
        """
        try:
            tasks = [
                self.generate_artwork(prompt, size, style, variations=1, model=model, quality=quality)
                for prompt in prompts
            ]
            
            results = await asyncio.gather(*tasks)
            return [item for sublist in results for item in sublist]
            
        except Exception as e:
            logger.error(f"Error in batch artwork generation: {str(e)}")
            raise
    
    async def generate_video(self, prompt: str, duration: int = 5, 
                            style: str = "cinematic") -> Dict:
        """
        Generate video using AI (when OpenAI Sora becomes available).
        
        Note: Currently returns placeholder. When Sora API is available, this will:
        1. Use OpenAI Sora for video generation
        2. Or integrate with alternatives like Runway ML, Pika Labs, Stable Video Diffusion
        
        Args:
            prompt: Description of the video to generate
            duration: Video duration in seconds
            style: Video style (cinematic, educational, etc.)
            
        Returns:
            Dict containing video URL and metadata
        """
        try:
            # Placeholder for future Sora integration
            # When Sora API is available, uncomment and use:
            # response = await self.client.videos.generate(
            #     model="sora",
            #     prompt=f"{prompt} in {style} style",
            #     duration=duration
            # )
            
            # For now, return information about video generation options
            return {
                "status": "not_available",
                "message": "Video generation requires OpenAI Sora (not yet publicly available) or alternative services",
                "alternatives": [
                    {
                        "service": "Runway ML",
                        "api": "https://runwayml.com",
                        "capabilities": "Text-to-video, image-to-video"
                    },
                    {
                        "service": "Pika Labs",
                        "api": "https://pika.art",
                        "capabilities": "AI video generation"
                    },
                    {
                        "service": "Stable Video Diffusion",
                        "api": "Stability AI API",
                        "capabilities": "Image-to-video generation"
                    }
                ],
                "note": "When Sora API becomes available, this function will automatically use it"
            }
            
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}")
            raise 
