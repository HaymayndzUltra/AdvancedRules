#!/usr/bin/env python3
"""
AdvancedRules Markdown Indexer
Indexes documentation files with structure-aware chunking
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib


class MarkdownIndexer:
    """Structure-aware markdown file indexer"""

    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 180):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Supported markdown extensions
        self.supported_extensions = {'.md', '.markdown', '.txt', '.rst'}

        # Markdown structure patterns
        self.header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        self.code_block_pattern = re.compile(r'```[\s\S]*?```', re.MULTILINE)
        self.list_pattern = re.compile(r'^[\s]*[-\*\+]\s+', re.MULTILINE)
        self.table_pattern = re.compile(r'^\|.*\|.*$', re.MULTILINE)

    def index_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Index a single markdown file"""
        if not file_path.exists() or not file_path.is_file():
            return []

        if file_path.suffix.lower() not in self.supported_extensions:
            return []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if not content.strip():
                return []

            # Extract structured chunks
            chunks = self._extract_structured_chunks(content)

            # Create documents
            documents = []
            for i, chunk in enumerate(chunks):
                # Generate content hash for deduplication
                content_hash = hashlib.sha256(chunk['content'].encode()).hexdigest()[:16]

                doc = {
                    'content': chunk['content'],
                    'source': str(file_path),
                    'file_path': str(file_path),
                    'chunk_id': i,
                    'chunk_type': chunk['type'],
                    'language': 'markdown',
                    'timestamp': self._get_timestamp(),
                    'content_hash': content_hash,
                }

                # Add metadata
                if 'metadata' in chunk:
                    doc.update(chunk['metadata'])

                documents.append(doc)

            return documents

        except Exception as e:
            print(f"Warning: Failed to index {file_path}: {e}")
            return []

    def _extract_structured_chunks(self, content: str) -> List[Dict[str, Any]]:
        """Extract structured chunks from markdown content"""
        chunks = []

        # Split by major sections (top-level headers)
        sections = self._split_by_headers(content)

        for section_title, section_content in sections:
            # Further chunk the section content
            section_chunks = self._chunk_section(section_content, section_title)

            for chunk in section_chunks:
                # Add section context to metadata
                if 'metadata' not in chunk:
                    chunk['metadata'] = {}
                chunk['metadata']['section'] = section_title

                chunks.append(chunk)

        # If no sections found, fall back to size-based chunking
        if not chunks:
            chunks = self._fallback_chunking(content)

        return chunks

    def _split_by_headers(self, content: str) -> List[tuple]:
        """Split content by top-level headers"""
        lines = content.split('\n')
        sections = []
        current_section = []
        current_title = "Document"

        for line in lines:
            # Check if this is a top-level header
            header_match = self.header_pattern.match(line)
            if header_match:
                level = len(header_match.group(1))
                title = header_match.group(2).strip()

                # Save previous section
                if current_section:
                    sections.append((current_title, '\n'.join(current_section)))

                # Start new section
                current_title = title
                current_section = [line]
            else:
                current_section.append(line)

        # Add final section
        if current_section:
            sections.append((current_title, '\n'.join(current_section)))

        return sections

    def _chunk_section(self, content: str, section_title: str) -> List[Dict[str, Any]]:
        """Chunk a section into smaller pieces"""
        chunks = []

        # Split by subsection headers or natural boundaries
        subsections = self._split_by_subsections(content)

        for subsection_title, subsection_content in subsections:
            # Check if subsection is too large
            if len(subsection_content) > self.chunk_size:
                # Split into smaller chunks
                sub_chunks = self._split_large_content(subsection_content)
                for sub_chunk in sub_chunks:
                    chunks.append({
                        'content': sub_chunk,
                        'type': 'documentation',
                        'metadata': {
                            'subsection': subsection_title,
                            'section': section_title
                        }
                    })
            else:
                chunks.append({
                    'content': subsection_content,
                    'type': 'documentation',
                    'metadata': {
                        'subsection': subsection_title,
                        'section': section_title
                    }
                })

        return chunks

    def _split_by_subsections(self, content: str) -> List[tuple]:
        """Split content by subsection headers (##, ###, etc.)"""
        lines = content.split('\n')
        subsections = []
        current_subsection = []
        current_title = "Content"

        for line in lines:
            # Check if this is a subsection header (## or deeper)
            header_match = self.header_pattern.match(line)
            if header_match and len(header_match.group(1)) >= 2:
                title = header_match.group(2).strip()

                # Save previous subsection
                if current_subsection:
                    subsections.append((current_title, '\n'.join(current_subsection)))

                # Start new subsection
                current_title = title
                current_subsection = [line]
            else:
                current_subsection.append(line)

        # Add final subsection
        if current_subsection:
            subsections.append((current_title, '\n'.join(current_subsection)))

        return subsections

    def _split_large_content(self, content: str) -> List[str]:
        """Split large content into smaller chunks"""
        chunks = []
        lines = content.split('\n')
        current_chunk = []

        for line in lines:
            current_chunk.append(line)
            current_content = '\n'.join(current_chunk)

            if len(current_content) >= self.chunk_size:
                chunks.append(current_content)

                # Start new chunk with overlap
                overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                current_chunk = current_chunk[overlap_start:]

        # Add remaining content
        if current_chunk:
            current_content = '\n'.join(current_chunk)
            if len(current_content) >= 50:  # Minimum chunk size
                chunks.append(current_content)

        return chunks

    def _fallback_chunking(self, content: str) -> List[Dict[str, Any]]:
        """Fallback to simple size-based chunking"""
        chunks = []
        lines = content.split('\n')
        current_chunk = []

        for line in lines:
            current_chunk.append(line)
            current_content = '\n'.join(current_chunk)

            if len(current_content) >= self.chunk_size:
                chunks.append({
                    'content': current_content,
                    'type': 'documentation',
                    'metadata': {}
                })

                # Start new chunk with overlap
                overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                current_chunk = current_chunk[overlap_start:]

        # Add remaining content
        if current_chunk:
            current_content = '\n'.join(current_chunk)
            if len(current_content) >= 50:
                chunks.append({
                    'content': current_content,
                    'type': 'documentation',
                    'metadata': {}
                })

        return chunks

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions"""
        return sorted(list(self.supported_extensions))

    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from markdown content"""
        metadata = {}

        # Extract title from first header
        title_match = self.header_pattern.search(content)
        if title_match:
            metadata['title'] = title_match.group(2).strip()

        # Count various elements
        metadata['headers'] = len(self.header_pattern.findall(content))
        metadata['code_blocks'] = len(self.code_block_pattern.findall(content))
        metadata['lists'] = len(self.list_pattern.findall(content))
        metadata['tables'] = len(self.table_pattern.findall(content))

        # Extract tags from content (common patterns)
        tags = []
        if 'TODO' in content.upper():
            tags.append('todo')
        if 'FIXME' in content.upper():
            tags.append('fixme')
        if 'NOTE' in content.upper():
            tags.append('note')
        if 'WARNING' in content.upper():
            tags.append('warning')

        if tags:
            metadata['tags'] = tags

        return metadata
