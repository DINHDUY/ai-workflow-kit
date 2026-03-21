"""
Element converters for transforming DOCX elements to Markdown.

This module provides the abstract ElementConverter base class and concrete
implementations for converting different DOCX elements (paragraphs, lists, etc.)
to their Markdown equivalents.
"""

import logging
import re
from abc import ABC, abstractmethod
from typing import List, Optional

from docx.oxml import CT_Hyperlink
from docx.table import Table
from docx.text.paragraph import Paragraph

from .image_handler import ImageHandler

logger = logging.getLogger(__name__)

# OOXML namespaces for image extraction
NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "v": "urn:schemas-microsoft-com:vml",
}


def _get_image_rids_from_element(element) -> List[str]:
    """Extract relationship IDs of inline images from an XML element.

    Supports both DrawingML (a:blip r:embed) and VML (v:imagedata r:id).
    """
    rids: List[str] = []
    try:
        # DrawingML: a:blip with r:embed
        for blip in element.iter(f"{{{NS['a']}}}blip"):
            embed = blip.get(f"{{{NS['r']}}}embed")
            if embed:
                rids.append(embed)
        # VML (legacy): v:imagedata with r:id
        for imagedata in element.iter(f"{{{NS['v']}}}imagedata"):
            rid = imagedata.get(f"{{{NS['r']}}}id")
            if rid:
                rids.append(rid)
    except Exception as e:
        logger.debug(f"Error extracting image rIds: {e}")
    return rids


class ElementConverter(ABC):
    """Abstract base class for element converters.
    
    This class defines the interface for converting DOCX elements to Markdown.
    Concrete implementations handle specific element types (paragraphs, tables, etc.).
    
    Following the Open/Closed Principle: open for extension, closed for modification.
    """
    
    @abstractmethod
    def can_convert(self, element) -> bool:
        """Check if this converter can handle the given element.
        
        Args:
            element: The DOCX element to check
            
        Returns:
            True if this converter can handle the element, False otherwise
        """
        pass
    
    @abstractmethod
    def convert(self, element) -> str:
        """Convert the element to Markdown.
        
        Args:
            element: The DOCX element to convert
            
        Returns:
            Markdown string representation of the element
        """
        pass


class ParagraphConverter(ElementConverter):
    """Converts DOCX paragraphs to Markdown.
    
    Handles:
    - Headings (Heading 1-6 -> # to ######)
    - Text formatting (bold, italic, combined)
    - Hyperlinks
    - Regular paragraphs
    
    Attributes:
        image_handler: Handler for extracting and referencing images
    """
    
    def __init__(self, image_handler: Optional[ImageHandler] = None):
        """Initialize the paragraph converter.
        
        Args:
            image_handler: Optional image handler for processing inline images
        """
        self.image_handler = image_handler
        logger.debug("ParagraphConverter initialized")
    
    def can_convert(self, element) -> bool:
        """Check if element is a Paragraph.
        
        Args:
            element: The element to check
            
        Returns:
            True if element is a Paragraph instance
        """
        return isinstance(element, Paragraph)
    
    def convert(self, element: Paragraph) -> str:
        """Convert a paragraph to Markdown.
        
        Args:
            element: The Paragraph to convert
            
        Returns:
            Markdown representation of the paragraph
        """
        if not self.can_convert(element):
            return ""
        
        # Check if it's a heading
        heading_level = self._get_heading_level(element)
        if heading_level:
            markdown_text = self._convert_runs(element)
            return f"{'#' * heading_level} {markdown_text}\n\n"
        
        # Check if it's a list item
        if self._is_list_item(element):
            return self._convert_list_item(element)
        
        # Regular paragraph
        markdown_text = self._convert_runs(element)
        
        # Empty paragraphs become blank lines
        if not markdown_text.strip():
            return "\n"
        
        return f"{markdown_text}\n\n"
    
    def _get_heading_level(self, paragraph: Paragraph) -> Optional[int]:
        """Determine if paragraph is a heading and get its level.
        
        Args:
            paragraph: The paragraph to check
            
        Returns:
            Heading level (1-6) or None if not a heading
        """
        style_name = paragraph.style.name if paragraph.style else ""
        
        # Check for heading styles
        heading_match = re.match(r'Heading\s*(\d+)', style_name, re.IGNORECASE)
        if heading_match:
            level = int(heading_match.group(1))
            return min(level, 6)  # Markdown only supports 6 levels
        
        # Check for Title style (treat as H1)
        if 'title' in style_name.lower():
            return 1
        
        return None
    
    def _is_list_item(self, paragraph: Paragraph) -> bool:
        """Check if paragraph is a list item.
        
        Args:
            paragraph: The paragraph to check
            
        Returns:
            True if paragraph is part of a list
        """
        style_name = paragraph.style.name if paragraph.style else ""
        
        # Check style name for list indicators
        if any(indicator in style_name.lower() for indicator in ['list', 'bullet', 'number']):
            return True
        
        # Check paragraph numbering properties
        try:
            if paragraph._element.pPr is not None:
                if paragraph._element.pPr.numPr is not None:
                    return True
        except Exception:
            pass
        
        return False
    
    def _convert_list_item(self, paragraph: Paragraph) -> str:
        """Convert a list item paragraph to Markdown.
        
        Args:
            paragraph: The list item paragraph
            
        Returns:
            Markdown list item
        """
        markdown_text = self._convert_runs(paragraph)
        
        # Determine list type and indentation
        indent_level = self._get_list_indent_level(paragraph)
        indent = "  " * indent_level  # 2 spaces per indent level
        
        # Check if numbered or bulleted
        if self._is_numbered_list(paragraph):
            return f"{indent}1. {markdown_text}\n"
        else:
            return f"{indent}- {markdown_text}\n"
    
    def _get_list_indent_level(self, paragraph: Paragraph) -> int:
        """Get the indentation level of a list item.
        
        Args:
            paragraph: The list item paragraph
            
        Returns:
            Indentation level (0-based)
        """
        try:
            if paragraph._element.pPr is not None:
                if paragraph._element.pPr.numPr is not None:
                    ilvl = paragraph._element.pPr.numPr.ilvl
                    if ilvl is not None:
                        return int(ilvl.val)
        except Exception:
            pass
        
        return 0
    
    def _is_numbered_list(self, paragraph: Paragraph) -> bool:
        """Check if list item is numbered (vs. bulleted).
        
        Args:
            paragraph: The list item paragraph
            
        Returns:
            True if numbered list, False if bulleted
        """
        style_name = paragraph.style.name if paragraph.style else ""
        return 'number' in style_name.lower()
    
    def _convert_runs(self, paragraph: Paragraph) -> str:
        """Convert all runs in a paragraph to Markdown.
        
        Args:
            paragraph: The paragraph containing runs
            
        Returns:
            Markdown-formatted text from all runs
        """
        result = []

        for element in paragraph._element:
            if isinstance(element, CT_Hyperlink):
                result.append(self._convert_hyperlink(element))
            elif hasattr(element, "tag") and "r" in element.tag:
                for run in paragraph.runs:
                    if run._element == element:
                        # Extract and save inline images first
                        if self.image_handler:
                            for rid in _get_image_rids_from_element(element):
                                img_md = self.image_handler.generate_markdown_image(rid)
                                if img_md:
                                    result.append(img_md)
                        result.append(self._convert_run(run))
                        break

        if not result:
            for run in paragraph.runs:
                if self.image_handler:
                    for rid in _get_image_rids_from_element(run._element):
                        img_md = self.image_handler.generate_markdown_image(rid)
                        if img_md:
                            result.append(img_md)
                result.append(self._convert_run(run))

        return "".join(result)
    
    def _convert_run(self, run) -> str:
        """Convert a single run to Markdown with formatting.
        
        Args:
            run: The run to convert
            
        Returns:
            Markdown-formatted text
        """
        text = run.text
        
        if not text:
            return ""
        
        # Apply formatting
        is_bold = run.bold
        is_italic = run.italic
        
        # Combined bold and italic
        if is_bold and is_italic:
            return f"***{text}***"
        elif is_bold:
            return f"**{text}**"
        elif is_italic:
            return f"*{text}*"
        else:
            return text
    
    def _convert_hyperlink(self, hyperlink_element: CT_Hyperlink) -> str:
        """Convert a hyperlink to Markdown link syntax.
        
        Args:
            hyperlink_element: The hyperlink XML element
            
        Returns:
            Markdown link syntax [text](url)
        """
        try:
            # Extract text from hyperlink
            text_elements = hyperlink_element.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
            text = ''.join(elem.text for elem in text_elements if elem.text)
            
            # Get URL (this is simplified; full implementation would resolve relationship IDs)
            # For now, we'll use the anchor or leave the URL empty
            anchor = hyperlink_element.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}anchor')
            
            if anchor:
                return f"[{text}](#{anchor})"
            else:
                # Would need to resolve rId to actual URL via relationships
                return f"[{text}]"
        
        except Exception as e:
            logger.warning(f"Error converting hyperlink: {e}")
            return ""


class TableConverter(ElementConverter):
    """Converts DOCX tables to Markdown table syntax.
    
    Handles conversion of Word tables to GitHub Flavored Markdown pipe tables.
    Supports:
    - Multi-row and multi-column tables
    - Header rows
    - Cell text formatting (bold, italic)
    - Nested content within cells
    
    Limitations:
    - Cell merging (colspan/rowspan) not fully supported
    - Complex nested tables simplified
    - Cell alignment defaults to left
    """
    
    def __init__(self, image_handler: Optional[ImageHandler] = None):
        """Initialize the table converter.
        
        Args:
            image_handler: Optional image handler for processing images in cells
        """
        self.image_handler = image_handler
        logger.debug("TableConverter initialized")
    
    def can_convert(self, element) -> bool:
        """Check if element is a Table.
        
        Args:
            element: The element to check
            
        Returns:
            True if element is a Table instance
        """
        return isinstance(element, Table)
    
    def convert(self, element: Table) -> str:
        """Convert a table to Markdown table syntax.
        
        Args:
            element: The Table to convert
            
        Returns:
            Markdown representation of the table
        """
        if not self.can_convert(element):
            return ""
        
        try:
            rows = element.rows
            if not rows:
                return ""
            
            # Get table dimensions
            num_cols = len(rows[0].cells)
            if num_cols == 0:
                return ""
            
            markdown_lines = []
            
            # Process each row
            for row_idx, row in enumerate(rows):
                cells = row.cells
                cell_texts = []
                
                # Extract text from each cell
                for cell in cells:
                    cell_text = self._extract_cell_text(cell)
                    # Clean and escape pipe characters
                    cell_text = cell_text.replace('|', '\\|').replace('\n', ' ')
                    cell_texts.append(cell_text)
                
                # Ensure consistent column count
                while len(cell_texts) < num_cols:
                    cell_texts.append('')
                
                # Build row
                row_text = '| ' + ' | '.join(cell_texts[:num_cols]) + ' |'
                markdown_lines.append(row_text)
                
                # Add separator after first row (treat as header)
                if row_idx == 0:
                    separator = '| ' + ' | '.join(['---'] * num_cols) + ' |'
                    markdown_lines.append(separator)
            
            # Join all rows and add spacing
            return '\n'.join(markdown_lines) + '\n\n'
        
        except Exception as e:
            logger.warning(f"Error converting table: {e}")
            return ""
    
    def _extract_cell_text(self, cell) -> str:
        """Extract formatted text from a table cell.
        
        Args:
            cell: The table cell to extract text from
            
        Returns:
            Formatted text with inline Markdown formatting
        """
        parts = []
        
        for paragraph in cell.paragraphs:
            para_text = self._format_paragraph_text(paragraph)
            if para_text:
                parts.append(para_text)
        
        # Join multiple paragraphs with space
        return ' '.join(parts).strip()
    
    def _format_paragraph_text(self, paragraph) -> str:
        """Format paragraph text with inline Markdown and images.
        
        Args:
            paragraph: The paragraph to format
            
        Returns:
            Text with Markdown formatting and image references
        """
        result = []

        for run in paragraph.runs:
            # Extract and save inline images
            if self.image_handler:
                for rid in _get_image_rids_from_element(run._element):
                    img_md = self.image_handler.generate_markdown_image(rid)
                    if img_md:
                        result.append(img_md)

            text = run.text
            if not text:
                continue

            is_bold = run.bold
            is_italic = run.italic
            if is_bold and is_italic:
                text = f"***{text}***"
            elif is_bold:
                text = f"**{text}**"
            elif is_italic:
                text = f"*{text}*"
            result.append(text)

        return "".join(result)


class ListConverter(ElementConverter):
    """Converts DOCX lists to Markdown.
    
    Note: In python-docx, lists are represented as specially-styled paragraphs,
    so the ParagraphConverter handles most list conversion. This converter exists
    for potential future enhancements and to maintain the architecture.
    """
    
    def can_convert(self, element) -> bool:
        """Check if element is a list.
        
        Args:
            element: The element to check
            
        Returns:
            False (lists are handled by ParagraphConverter)
        """
        return False
    
    def convert(self, element) -> str:
        """Convert element to Markdown.
        
        Args:
            element: The element to convert
            
        Returns:
            Empty string (lists handled by ParagraphConverter)
        """
        return ""
