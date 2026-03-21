"""
DOCX to Markdown Converter Package.

This package provides functionality to convert Microsoft Word (.docx) documents
to Markdown format with support for essential formatting elements.

Main Components:
- DocxToMarkdownConverter: Main orchestrator class
- convert_docx_to_markdown: Convenience function for simple conversions

Example:
    >>> from pathlib import Path
    >>> from docx_to_markdown import convert_docx_to_markdown
    >>> 
    >>> convert_docx_to_markdown(
    ...     input_path=Path("document.docx"),
    ...     output_path=Path("output.md")
    ... )
"""

import logging
from pathlib import Path
from typing import List, Optional

from .config import ConversionConfig
from .docx_extractor import DocxExtractor
from .element_converters import ElementConverter, ParagraphConverter, TableConverter
from .exceptions import ConversionError, InvalidDocxError, ImageExtractionError
from .image_handler import ImageHandler
from .markdown_writer import FileMarkdownWriter, MarkdownWriter

# Package version
__version__ = "1.0.0"

# Configure package logger
logger = logging.getLogger(__name__)


class DocxToMarkdownConverter:
    """Main orchestrator for DOCX to Markdown conversion.
    
    This class coordinates the extraction, conversion, and writing processes
    using dependency injection for maximum flexibility and testability.
    
    Attributes:
        extractor: Handles DOCX document loading
        converters: List of element converters (paragraph, list, etc.)
        image_handler: Handles image extraction
        writer: Writes Markdown output
        warnings: List of warnings collected during conversion
        
    Example:
        >>> extractor = DocxExtractor(Path("doc.docx"))
        >>> writer = FileMarkdownWriter(Path("output.md"))
        >>> converter = DocxToMarkdownConverter(
        ...     extractor=extractor,
        ...     converters=[ParagraphConverter()],
        ...     image_handler=None,
        ...     writer=writer
        ... )
        >>> converter.convert()
    """
    
    def __init__(
        self,
        extractor: DocxExtractor,
        converters: List[ElementConverter],
        image_handler: Optional[ImageHandler],
        writer: MarkdownWriter
    ):
        """Initialize the converter with its dependencies.
        
        Args:
            extractor: Document extractor instance
            converters: List of element converters to use
            image_handler: Optional image handler
            writer: Markdown writer instance
        """
        self.extractor = extractor
        self.converters = converters
        self.image_handler = image_handler
        self.writer = writer
        self.warnings: List[str] = []
        
        logger.debug("DocxToMarkdownConverter initialized")
    
    def convert(self) -> None:
        """Execute the conversion process.
        
        This method orchestrates the entire conversion:
        1. Load the DOCX document
        2. Extract images (if enabled)
        3. Convert each element to Markdown
        4. Write the output
        
        Raises:
            ConversionError: If an error occurs during conversion
        """
        try:
            # Step 1: Load document
            logger.info("Starting DOCX to Markdown conversion")
            document = self.extractor.load_document()
            
            # Step 2: Extract images if handler is available
            if self.image_handler:
                image_parts = self.extractor.get_image_parts()
                self.image_handler.load_image_parts(image_parts)
                logger.info(f"Image handler loaded with {len(image_parts)} images")
            
            # Step 3: Convert elements
            markdown_content = []
            
            # Process document body elements in order (paragraphs and tables)
            logger.info("Converting document elements (paragraphs and tables)")
            
            # Iterate through body elements to maintain order
            for element in document.element.body:
                converted = ""
                
                # Check if it's a paragraph
                if element.tag.endswith('p'):
                    # Find the corresponding Paragraph object
                    for para in document.paragraphs:
                        if para._element == element:
                            converted = self._convert_element(para)
                            break
                
                # Check if it's a table
                elif element.tag.endswith('tbl'):
                    # Find the corresponding Table object
                    for table in document.tables:
                        if table._element == element:
                            converted = self._convert_element(table)
                            break
                
                if converted:
                    markdown_content.append(converted)
            
            # Step 4: Write output
            final_content = ''.join(markdown_content)
            self.writer.write(final_content)
            
            logger.info(f"Conversion complete. Output: {self.writer.get_output_info()}")
            
            # Log warnings if any
            if self.warnings:
                logger.warning(f"Conversion completed with {len(self.warnings)} warnings")
                for warning in self.warnings:
                    logger.warning(f"  - {warning}")
        
        except ConversionError:
            # Re-raise conversion errors as-is
            raise
        
        except Exception as e:
            logger.error(f"Unexpected error during conversion: {e}")
            raise ConversionError(f"Conversion failed: {str(e)}")
    
    def _convert_element(self, element) -> str:
        """Convert a single element using the appropriate converter.
        
        Args:
            element: The DOCX element to convert
            
        Returns:
            Markdown representation of the element
        """
        for converter in self.converters:
            if converter.can_convert(element):
                try:
                    return converter.convert(element)
                except Exception as e:
                    warning = f"Error converting element: {str(e)}"
                    self.warnings.append(warning)
                    logger.warning(warning)
                    return ""
        
        # No converter found for this element type
        logger.debug(f"No converter found for element type: {type(element)}")
        return ""
    
    def get_warnings(self) -> List[str]:
        """Get list of warnings from the conversion process.
        
        Returns:
            List of warning messages
        """
        return self.warnings.copy()


def convert_docx_to_markdown(
    input_path: Path,
    output_path: Optional[Path] = None,
    config: Optional[ConversionConfig] = None
) -> None:
    """Convenience function to convert a DOCX file to Markdown.
    
    This function sets up all necessary components and performs the conversion
    with sensible defaults. For more control, use DocxToMarkdownConverter directly.
    
    Args:
        input_path: Path to the input DOCX file
        output_path: Path for the output Markdown file (default: input_path with .md extension)
        config: Optional configuration (default: ConversionConfig with defaults)
        
    Raises:
        FileNotFoundError: If the input file doesn't exist
        ConversionError: If an error occurs during conversion
        
    Example:
        >>> convert_docx_to_markdown(
        ...     input_path=Path("document.docx"),
        ...     output_path=Path("output.md")
        ... )
    """
    # Set defaults
    if output_path is None:
        output_path = input_path.with_suffix('.md')
    
    if config is None:
        config = ConversionConfig()
    
    # Validate configuration
    config.validate()
    
    # Create components
    extractor = DocxExtractor(input_path)
    
    # Load document first to pass to image handler
    document = extractor.load_document()
    
    # Create image handler if needed
    image_handler = None
    if config.extract_images:
        image_handler = ImageHandler(config, document, output_path)
    
    # Create converters
    paragraph_converter = ParagraphConverter(image_handler)
    table_converter = TableConverter(image_handler)
    converters = [paragraph_converter, table_converter]
    
    # Create writer
    writer = FileMarkdownWriter(output_path, config.output_encoding)
    
    # Create and run converter
    converter = DocxToMarkdownConverter(
        extractor=extractor,
        converters=converters,
        image_handler=image_handler,
        writer=writer
    )
    
    converter.convert()
    
    # Log any warnings
    warnings = converter.get_warnings()
    if warnings:
        logger.info(f"Conversion completed with {len(warnings)} warnings")


def setup_logging(level: int = logging.INFO) -> None:
    """Set up logging configuration for the converter package.
    
    Args:
        level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )


# Export public API
__all__ = [
    'DocxToMarkdownConverter',
    'convert_docx_to_markdown',
    'ConversionConfig',
    'ConversionError',
    'InvalidDocxError',
    'ImageExtractionError',
    'setup_logging',
    '__version__',
]
