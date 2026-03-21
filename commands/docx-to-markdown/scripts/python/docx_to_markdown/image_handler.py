"""
Image extraction and handling for DOCX to Markdown conversion.

This module provides the ImageHandler class for extracting images from
DOCX documents and saving them to the filesystem.
"""

import logging
from pathlib import Path
from typing import Dict, Optional

from docx import Document

from .config import ConversionConfig
from .exceptions import ImageExtractionError

logger = logging.getLogger(__name__)


class ImageHandler:
    """Handles extraction and storage of images from DOCX documents.

    This class is responsible for extracting embedded images from the document,
    saving them to disk, and generating appropriate Markdown image references.
    Paths in Markdown are relative to the output file when output_path is set.

    Attributes:
        config: Configuration settings for image extraction
        document: The DOCX document containing images
        output_path: Path to the output .md file (for relative paths in Markdown)
        image_parts: Dictionary mapping relationship IDs to image data
        saved_images: Dictionary tracking saved image paths by relationship ID

    Example:
        >>> handler = ImageHandler(config, document, output_path)
        >>> image_path = handler.extract_image("rId5")
        >>> print(image_path)  # "Document_2/image1.png" (relative to output)
    """

    def __init__(
        self,
        config: ConversionConfig,
        document: Document,
        output_path: Optional[Path] = None,
    ):
        """Initialize the image handler.

        Args:
            config: Configuration settings controlling image extraction
            document: The loaded DOCX document
            output_path: Path to output .md file (enables relative paths in Markdown)
        """
        self.config = config
        self.document = document
        self.output_path = output_path
        self.image_parts: Dict[str, bytes] = {}
        self.saved_images: Dict[str, str] = {}
        self._image_counter = 0
        logger.debug("ImageHandler initialized")
    
    def load_image_parts(self, image_parts: Dict[str, bytes]) -> None:
        """Load image parts extracted from the document.
        
        Args:
            image_parts: Dictionary mapping relationship IDs to image binary data
        """
        self.image_parts = image_parts
        logger.info(f"Loaded {len(image_parts)} image parts")
    
    def extract_image(self, rel_id: str) -> Optional[str]:
        """Extract an image by its relationship ID and save to disk.
        
        Args:
            rel_id: The relationship ID of the image in the document
            
        Returns:
            Relative path to the saved image file, or None if extraction failed
            
        Raises:
            ImageExtractionError: If the image cannot be extracted or saved
        """
        if not self.config.extract_images:
            logger.debug(f"Image extraction disabled, skipping: {rel_id}")
            return None
        
        # Check if already extracted
        if rel_id in self.saved_images:
            return self.saved_images[rel_id]
        
        # Get image data
        if rel_id not in self.image_parts:
            logger.warning(f"Image not found in document: {rel_id}")
            return None
        
        try:
            image_data = self.image_parts[rel_id]
            
            # Determine file extension from image data
            extension = self._detect_image_extension(image_data)
            
            # Generate filename
            self._image_counter += 1
            filename = f"image{self._image_counter}{extension}"
            
            # Ensure image directory exists
            image_dir = Path(self.config.image_dir)
            image_dir.mkdir(parents=True, exist_ok=True)
            
            # Save image
            image_path = image_dir / filename
            image_path.write_bytes(image_data)

            # Path for Markdown: relative to output file when possible
            if self.output_path:
                try:
                    rel = image_path.resolve().relative_to(
                        self.output_path.parent.resolve()
                    )
                    relative_path = str(rel).replace("\\", "/")
                except ValueError:
                    relative_path = f"{self.config.image_dir}/{filename}"
            else:
                relative_path = f"{self.config.image_dir}/{filename}"

            self.saved_images[rel_id] = relative_path

            logger.info(f"Extracted image: {rel_id} -> {relative_path}")
            return relative_path
        
        except PermissionError:
            error_msg = f"Permission denied when saving image to {self.config.image_dir}"
            logger.error(error_msg)
            raise ImageExtractionError(rel_id, error_msg)
        
        except OSError as e:
            error_msg = f"OS error when saving image: {str(e)}"
            logger.error(error_msg)
            raise ImageExtractionError(rel_id, error_msg)
        
        except Exception as e:
            logger.error(f"Unexpected error extracting image {rel_id}: {e}")
            return None
    
    def _detect_image_extension(self, image_data: bytes) -> str:
        """Detect image file extension from binary data.
        
        Args:
            image_data: Binary image data
            
        Returns:
            File extension including the dot (e.g., '.png', '.jpg')
        """
        # Check magic bytes for common image formats
        if image_data.startswith(b'\x89PNG\r\n\x1a\n'):
            return '.png'
        elif image_data.startswith(b'\xff\xd8\xff'):
            return '.jpg'
        elif image_data.startswith(b'GIF87a') or image_data.startswith(b'GIF89a'):
            return '.gif'
        elif image_data.startswith(b'BM'):
            return '.bmp'
        elif image_data.startswith(b'RIFF') and b'WEBP' in image_data[:12]:
            return '.webp'
        else:
            logger.warning("Unknown image format, defaulting to .png")
            return '.png'
    
    def generate_markdown_image(self, rel_id: str, alt_text: str = "") -> str:
        """Generate Markdown syntax for an image reference.
        
        Args:
            rel_id: The relationship ID of the image
            alt_text: Alternative text for the image (optional)
            
        Returns:
            Markdown image syntax, or empty string if image not available
        """
        image_path = self.extract_image(rel_id)
        if image_path:
            # Escape special characters in alt text
            safe_alt_text = alt_text.replace('[', '\\[').replace(']', '\\]')
            return f"![{safe_alt_text}]({image_path})"
        return ""
