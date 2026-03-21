"""
Markdown output writing.

This module provides classes for writing Markdown content to various outputs,
following the Liskov Substitution Principle with interchangeable writers.
"""

import logging
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path

logger = logging.getLogger(__name__)


class MarkdownWriter(ABC):
    """Abstract base class for Markdown writers.
    
    This defines the interface for writing Markdown content. Concrete
    implementations can write to files, strings, or other destinations.
    
    Following LSP: all implementations can be used interchangeably.
    """
    
    @abstractmethod
    def write(self, content: str) -> None:
        """Write Markdown content.
        
        Args:
            content: The Markdown content to write
        """
        pass
    
    @abstractmethod
    def get_output_info(self) -> str:
        """Get information about the output destination.
        
        Returns:
            Description of where content is written
        """
        pass


class FileMarkdownWriter(MarkdownWriter):
    """Writes Markdown content to a file.
    
    Uses atomic write operations (write to temp file, then rename) to
    ensure file integrity even if the write operation is interrupted.
    
    Attributes:
        output_path: Path to the output file
        encoding: Character encoding for the file
        
    Example:
        >>> writer = FileMarkdownWriter(Path("output.md"))
        >>> writer.write("# Hello\\n\\nThis is markdown.")
    """
    
    def __init__(self, output_path: Path, encoding: str = 'utf-8'):
        """Initialize the file writer.
        
        Args:
            output_path: Path where the Markdown file will be written
            encoding: Character encoding to use (default: 'utf-8')
        """
        self.output_path = output_path
        self.encoding = encoding
        logger.debug(f"FileMarkdownWriter initialized: {output_path}")
    
    def write(self, content: str) -> None:
        """Write Markdown content to file atomically.
        
        Args:
            content: The Markdown content to write
            
        Raises:
            PermissionError: If unable to write to the output path
            OSError: If an OS-level error occurs during writing
        """
        try:
            # Ensure parent directory exists
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to temporary file first (atomic operation)
            temp_file = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    encoding=self.encoding,
                    dir=self.output_path.parent,
                    delete=False,
                    suffix='.tmp'
                ) as tf:
                    temp_file = Path(tf.name)
                    tf.write(content)
                    tf.flush()
                
                # Atomic rename
                temp_file.replace(self.output_path)
                logger.info(f"Successfully wrote Markdown to: {self.output_path}")
            
            finally:
                # Clean up temp file if rename failed
                if temp_file and temp_file.exists():
                    try:
                        temp_file.unlink()
                    except Exception:
                        pass
        
        except PermissionError as e:
            logger.error(f"Permission denied writing to {self.output_path}: {e}")
            raise
        
        except OSError as e:
            logger.error(f"OS error writing to {self.output_path}: {e}")
            raise
        
        except Exception as e:
            logger.error(f"Unexpected error writing to {self.output_path}: {e}")
            raise
    
    def get_output_info(self) -> str:
        """Get information about the output file.
        
        Returns:
            Path to the output file as a string
        """
        return str(self.output_path)


class StringMarkdownWriter(MarkdownWriter):
    """Writes Markdown content to an in-memory string buffer.
    
    Useful for testing or when the Markdown output needs to be
    processed further before being written to a file.
    
    Attributes:
        buffer: String buffer containing the accumulated content
        
    Example:
        >>> writer = StringMarkdownWriter()
        >>> writer.write("# Title\\n")
        >>> print(writer.get_content())
        # Title
    """
    
    def __init__(self):
        """Initialize the string writer with an empty buffer."""
        self.buffer = ""
        logger.debug("StringMarkdownWriter initialized")
    
    def write(self, content: str) -> None:
        """Append content to the string buffer.
        
        Args:
            content: The Markdown content to append
        """
        self.buffer += content
        logger.debug(f"Appended {len(content)} characters to buffer")
    
    def get_content(self) -> str:
        """Get the accumulated content.
        
        Returns:
            The complete Markdown content in the buffer
        """
        return self.buffer
    
    def get_output_info(self) -> str:
        """Get information about the buffer.
        
        Returns:
            Description of the buffer size
        """
        return f"String buffer ({len(self.buffer)} characters)"
    
    def clear(self) -> None:
        """Clear the buffer content."""
        self.buffer = ""
        logger.debug("Buffer cleared")
