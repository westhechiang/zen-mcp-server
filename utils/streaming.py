"""
Streaming response utilities for Zen MCP Server.

This module provides chunked response functionality to improve CLI rendering
performance for large outputs from zen tools.
"""

import logging
import os
from typing import Generator, List
from mcp.types import TextContent

logger = logging.getLogger(__name__)

# Configuration from environment variables
STREAMING_ENABLED = os.getenv("STREAMING_ENABLED", "true").lower() == "true"
STREAMING_CHUNK_SIZE = int(os.getenv("STREAMING_CHUNK_SIZE", "1500"))
STREAMING_MAX_CHUNKS = int(os.getenv("STREAMING_MAX_CHUNKS", "25"))
STREAMING_THRESHOLD = int(os.getenv("STREAMING_THRESHOLD", "1000"))

class StreamingResponse:
    """
    Manages chunked responses for better CLI rendering performance.
    
    The zen tools complete successfully but Claude Code CLI hangs while rendering
    large outputs. This class breaks responses into smaller chunks to improve
    the user experience.
    """
    
    def __init__(self, chunk_size: int = None, max_chunks: int = None):
        """
        Initialize streaming response handler.
        
        Args:
            chunk_size: Maximum characters per chunk (uses env var if None)
            max_chunks: Maximum number of chunks before summary (uses env var if None)
        """
        self.chunk_size = chunk_size or STREAMING_CHUNK_SIZE
        self.max_chunks = max_chunks or STREAMING_MAX_CHUNKS
    
    def chunk_response(self, content: str, tool_name: str = "zen") -> List[TextContent]:
        """
        Break large content into manageable chunks with progress indicators.
        
        Args:
            content: Large content string to chunk
            tool_name: Name of the tool generating the content
            
        Returns:
            List of TextContent chunks with progress indicators
        """
        if len(content) <= self.chunk_size:
            # Content is small enough, return as-is
            return [TextContent(type="text", text=content)]
        
        logger.info(f"Chunking large {tool_name} response: {len(content)} chars into {self.chunk_size} char chunks")
        
        chunks = []
        total_chunks = min((len(content) + self.chunk_size - 1) // self.chunk_size, self.max_chunks)
        
        # Add initial status
        status_header = f"🔄 {tool_name.upper()} ANALYSIS STREAMING ({len(content):,} chars, {total_chunks} chunks)\n{'='*60}\n\n"
        
        for i in range(total_chunks):
            start_idx = i * self.chunk_size
            end_idx = min(start_idx + self.chunk_size, len(content))
            chunk_content = content[start_idx:end_idx]
            
            # Add progress header to each chunk
            progress = f"📄 CHUNK {i + 1}/{total_chunks}"
            if i == 0:
                chunk_text = status_header + progress + "\n" + "─" * 40 + "\n\n" + chunk_content
            else:
                chunk_text = f"\n{progress}\n" + "─" * 40 + "\n\n" + chunk_content
            
            # Add completion indicator for final chunk
            if i == total_chunks - 1:
                if end_idx < len(content):
                    # Truncated due to max_chunks limit
                    remaining = len(content) - end_idx
                    chunk_text += f"\n\n⚠️  TRUNCATED: {remaining:,} characters remaining. Use 'continue' to see more."
                else:
                    # Complete content
                    chunk_text += f"\n\n✅ ANALYSIS COMPLETE ({total_chunks} chunks delivered)"
            
            chunks.append(TextContent(type="text", text=chunk_text))
        
        logger.info(f"Generated {len(chunks)} chunks for {tool_name} response")
        return chunks

def create_streaming_response(content: str, tool_name: str = "zen", 
                            chunk_size: int = None, max_chunks: int = None) -> List[TextContent]:
    """
    Convenience function to create a streaming response.
    
    Args:
        content: Content to stream
        tool_name: Name of the tool
        chunk_size: Characters per chunk (uses env var if None)
        max_chunks: Maximum chunks before truncation (uses env var if None)
        
    Returns:
        List of TextContent chunks
    """
    if not STREAMING_ENABLED:
        # Return single response if streaming disabled
        return [TextContent(type="text", text=content)]
        
    streaming = StreamingResponse(chunk_size=chunk_size, max_chunks=max_chunks)
    return streaming.chunk_response(content, tool_name)

def is_large_response(content: str, threshold: int = None) -> bool:
    """
    Check if response is large enough to benefit from streaming.
    
    Args:
        content: Response content
        threshold: Size threshold in characters (uses env var if None)
        
    Returns:
        True if content should be streamed (always True if STREAMING_ENABLED)
    """
    if not STREAMING_ENABLED:
        return False
        
    threshold = threshold or STREAMING_THRESHOLD
    return len(content) > threshold