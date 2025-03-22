from typing import Dict, List, Optional
import openai
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
        openai.api_key = self.settings.OPENAI_API_KEY

    async def generate_artwork(self, prompt: str, size: str = "1024x1024", 
                             style: str = "natural", variations: int = 1) -> List[Dict]:
        """
        Generate artwork using DALL-E.
        
        Args:
            prompt: Description of the artwork to generate
            size: Image size (256x256, 512x512, or 1024x1024)
            style: Art style (natural, abstract, cartoon, etc.)
            variations: Number of variations to generate
            
        Returns:
            List of Dicts containing generated images and metadata
        """
        try:
            # Enhance prompt with style
            enhanced_prompt = f"{prompt} in {style} style"
            
            # Generate images
            response = await openai.Image.acreate(
                prompt=enhanced_prompt,
                n=variations,
                size=size
            )
            
            results = []
            for image_data in response["data"]:
                # Download and process the image
                image_url = image_data["url"]
                image = await self._download_image(image_url)
                
                # Convert to base64 for storage/transmission
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                results.append({
                    "image": img_str,
                    "prompt": enhanced_prompt,
                    "style": style,
                    "size": size,
                    "url": image_url
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error generating artwork: {str(e)}")
            raise

    async def edit_artwork(self, image_path: str, prompt: str, 
                          mask_path: Optional[str] = None) -> Dict:
        """
        Edit existing artwork using DALL-E.
        
        Args:
            image_path: Path to the original image
            prompt: Description of the changes to make
            mask_path: Optional path to a mask image
            
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
            
            # Create the edit
            response = await openai.Image.acreate_edit(
                image=image,
                mask=mask,
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            
            # Process the result
            image_url = response["data"][0]["url"]
            edited_image = await self._download_image(image_url)
            
            # Convert to base64
            buffered = io.BytesIO()
            edited_image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                "image": img_str,
                "prompt": prompt,
                "url": image_url
            }
            
        except Exception as e:
            logger.error(f"Error editing artwork: {str(e)}")
            raise

    async def generate_variations(self, image_path: str, variations: int = 3) -> List[Dict]:
        """
        Generate variations of an existing image.
        
        Args:
            image_path: Path to the original image
            variations: Number of variations to generate
            
        Returns:
            List of Dicts containing the variations
        """
        try:
            # Open the image
            image = Image.open(image_path)
            
            # Generate variations
            response = await openai.Image.acreate_variation(
                image=image,
                n=variations,
                size="1024x1024"
            )
            
            results = []
            for image_data in response["data"]:
                image_url = image_data["url"]
                variation = await self._download_image(image_url)
                
                # Convert to base64
                buffered = io.BytesIO()
                variation.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                results.append({
                    "image": img_str,
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
                                   style: str = "natural") -> List[Dict]:
        """
        Generate multiple artworks in parallel.
        
        Args:
            prompts: List of prompts to generate artwork from
            size: Image size
            style: Art style
            
        Returns:
            List of Dicts containing all generated images
        """
        try:
            tasks = [
                self.generate_artwork(prompt, size, style)
                for prompt in prompts
            ]
            
            results = await asyncio.gather(*tasks)
            return [item for sublist in results for item in sublist]
            
        except Exception as e:
            logger.error(f"Error in batch artwork generation: {str(e)}")
            raise 
