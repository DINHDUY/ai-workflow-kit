"""
Configuration settings for DOCX to Markdown conversion.

This module defines the configuration dataclass that controls conversion behavior,
including image extraction settings and output formatting options.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ConversionConfig:
    """Configuration for DOCX to Markdown conversion.
    
    Attributes:
        extract_images: Whether to extract embedded images from the document.
        image_dir: Directory path where extracted images will be saved.
        output_encoding: Character encoding for the output Markdown file.
        markdown_flavor: Markdown variant to use (currently only 'gfm' supported).
        
    Example:
        >>> config = ConversionConfig(
        ...     extract_images=True,
        ...     image_dir="images",
        ...     output_encoding="utf-8"
        ... )
    """
    
    extract_images: bool = True
    image_dir: str = "images"
    output_encoding: str = "utf-8"
    markdown_flavor: str = "gfm"  # GitHub Flavored Markdown
    
    def validate(self) -> None:
        """Validate configuration settings.
        
        Raises:
            ValueError: If image_dir contains invalid characters or is empty.
        """
        if self.extract_images and not self.image_dir.strip():
            raise ValueError("image_dir cannot be empty when extract_images is True")
        
        if self.markdown_flavor not in ["gfm", "standard", "commonmark"]:
            raise ValueError(
                f"Unsupported markdown_flavor: {self.markdown_flavor}. "
                "Use 'gfm', 'standard', or 'commonmark'."
            )
    
    def get_image_dir_path(self, base_path: Optional[Path] = None) -> Path:
        """Get the full path for the image directory.
        
        Args:
            base_path: Base directory for relative image paths. If None, uses current directory.
            
        Returns:
            Path object representing the image directory.
        """
        img_path = Path(self.image_dir)
        if not img_path.is_absolute() and base_path:
            return base_path / img_path
        return img_path
