"""
Custom exceptions for DOCX to Markdown conversion.

This module defines exception classes that represent various error conditions
that can occur during the conversion process.
"""


class ConversionError(Exception):
    """Base exception for all conversion-related errors.
    
    This exception serves as the base class for all custom exceptions
    in the conversion process, making it easy to catch all conversion
    errors with a single except clause.
    """
    pass


class InvalidDocxError(ConversionError):
    """Raised when the input file is not a valid DOCX document.
    
    This exception is raised when:
    - The file is not a valid ZIP archive
    - The file doesn't contain required DOCX components
    - The file is corrupted or malformed
    
    Attributes:
        file_path: Path to the invalid DOCX file
        message: Description of why the file is invalid
    """
    
    def __init__(self, file_path: str, message: str = "Invalid DOCX file"):
        self.file_path = file_path
        self.message = f"{message}: {file_path}"
        super().__init__(self.message)


class ImageExtractionError(ConversionError):
    """Raised when an error occurs during image extraction.
    
    This exception is raised when:
    - An image cannot be extracted from the document
    - The image directory cannot be created
    - Permission is denied when saving images
    - Disk space is insufficient
    
    Attributes:
        image_id: Identifier of the image that failed to extract
        message: Description of the extraction failure
    """
    
    def __init__(self, image_id: str, message: str = "Failed to extract image"):
        self.image_id = image_id
        self.message = f"{message}: {image_id}"
        super().__init__(self.message)
