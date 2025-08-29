#!/usr/bin/env python3
"""
AdvancedRules Code Indexer
Indexes source code files with intelligent chunking
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib


class CodeIndexer:
    """Intelligent code file indexer with semantic chunking"""

    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 180):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # File extensions to index
        self.supported_extensions = {
            '.py', '.ts', '.tsx', '.js', '.jsx', '.java', '.cpp', '.c', '.h',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala'
        }

        # Language-specific patterns for better chunking
        self.language_patterns = {
            'python': {
                'class_pattern': re.compile(r'^class\s+(\w+)'),
                'function_pattern': re.compile(r'^def\s+(\w+)'),
                'import_pattern': re.compile(r'^(?:import|from)'),
            },
            'typescript': {
                'class_pattern': re.compile(r'^(?:export\s+)?class\s+(\w+)'),
                'function_pattern': re.compile(r'^(?:export\s+)?(?:function|const|let|var)\s+(\w+)\s*[=:]'),
                'import_pattern': re.compile(r'^(?:import|export)'),
            },
            'javascript': {
                'class_pattern': re.compile(r'^(?:export\s+)?class\s+(\w+)'),
                'function_pattern': re.compile(r'^(?:export\s+)?(?:function|const|let|var)\s+(\w+)\s*[=:]'),
                'import_pattern': re.compile(r'^(?:import|export)'),
            }
        }

    def index_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Index a single code file"""
        if not file_path.exists() or not file_path.is_file():
            return []

        if file_path.suffix.lower() not in self.supported_extensions:
            return []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if not content.strip():
                return []

            # Detect language
            language = self._detect_language(file_path)

            # Extract semantic chunks
            chunks = self._extract_semantic_chunks(content, language)

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
                    'language': language,
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

    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension"""
        ext = file_path.suffix.lower()

        language_map = {
            '.py': 'python',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
        }

        return language_map.get(ext, 'unknown')

    def _extract_semantic_chunks(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Extract semantic chunks from code content"""
        lines = content.split('\n')
        chunks = []

        # Get language patterns
        patterns = self.language_patterns.get(language, {})

        current_chunk = []
        current_type = 'code'
        current_metadata = {}
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check for semantic boundaries
            if self._is_semantic_boundary(line, patterns):
                # Save current chunk if it has content
                if current_chunk:
                    chunk_content = '\n'.join(current_chunk)
                    if len(chunk_content) >= 50:  # Minimum chunk size
                        chunks.append({
                            'content': chunk_content,
                            'type': current_type,
                            'metadata': current_metadata.copy()
                        })

                # Start new chunk
                current_chunk = [line]
                current_type, current_metadata = self._classify_line(line, patterns)
            else:
                current_chunk.append(line)

            i += 1

        # Add final chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            if len(chunk_content) >= 50:
                chunks.append({
                    'content': chunk_content,
                    'type': current_type,
                    'metadata': current_metadata.copy()
                })

        # If no semantic chunks found, fall back to size-based chunking
        if not chunks:
            return self._fallback_chunking(content)

        # Post-process chunks to ensure they're not too large
        processed_chunks = []
        for chunk in chunks:
            if len(chunk['content']) > self.chunk_size:
                # Split large chunks
                sub_chunks = self._split_large_chunk(chunk)
                processed_chunks.extend(sub_chunks)
            else:
                processed_chunks.append(chunk)

        return processed_chunks

    def _is_semantic_boundary(self, line: str, patterns: Dict) -> bool:
        """Check if line represents a semantic boundary"""
        stripped = line.strip()

        # Empty lines
        if not stripped:
            return False

        # Comments
        if stripped.startswith(('#', '//', '/*', '*', '///')):
            return False

        # Class definitions
        if 'class_pattern' in patterns and patterns['class_pattern'].match(stripped):
            return True

        # Function definitions
        if 'function_pattern' in patterns and patterns['function_pattern'].match(stripped):
            return True

        # Import statements
        if 'import_pattern' in patterns and patterns['import_pattern'].match(stripped):
            return True

        # General patterns
        if re.match(r'^\s*(?:class|def|function|const|let|var|public|private|protected)\s', stripped):
            return True

        return False

    def _classify_line(self, line: str, patterns: Dict) -> tuple:
        """Classify a line and extract metadata"""
        stripped = line.strip()

        # Class definition
        if 'class_pattern' in patterns:
            match = patterns['class_pattern'].match(stripped)
            if match:
                return 'class', {'entity_name': match.group(1), 'entity_type': 'class'}

        # Function definition
        if 'function_pattern' in patterns:
            match = patterns['function_pattern'].match(stripped)
            if match:
                return 'function', {'entity_name': match.group(1), 'entity_type': 'function'}

        # Import statement
        if 'import_pattern' in patterns and patterns['import_pattern'].match(stripped):
            return 'imports', {'entity_type': 'imports'}

        return 'code', {}

    def _split_large_chunk(self, chunk: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split a large chunk into smaller pieces"""
        content = chunk['content']
        lines = content.split('\n')

        sub_chunks = []
        current_lines = []

        for line in lines:
            current_lines.append(line)

            # Check if current chunk is large enough to split
            current_content = '\n'.join(current_lines)
            if len(current_content) >= self.chunk_size:
                # Create sub-chunk
                sub_chunk = {
                    'content': current_content,
                    'type': chunk['type'],
                    'metadata': chunk.get('metadata', {}).copy()
                }
                sub_chunks.append(sub_chunk)

                # Start new chunk with overlap
                overlap_start = max(0, len(current_lines) - self.chunk_overlap)
                current_lines = current_lines[overlap_start:]

        # Add remaining lines
        if current_lines:
            current_content = '\n'.join(current_lines)
            if len(current_content) >= 50:
                sub_chunk = {
                    'content': current_content,
                    'type': chunk['type'],
                    'metadata': chunk.get('metadata', {}).copy()
                }
                sub_chunks.append(sub_chunk)

        return sub_chunks

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
                    'type': 'code',
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
                    'type': 'code',
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
