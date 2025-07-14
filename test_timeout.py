#!/usr/bin/env python3
"""Test script to verify timeout functionality in AI providers."""

import asyncio
import logging
import time
import os
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from providers.openai_provider import OpenAIModelProvider
from providers.base import DEFAULT_PROVIDER_TIMEOUT

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_timeout():
    """Test that the timeout is properly applied to provider calls."""
    
    # This test requires a valid OPENAI_API_KEY
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not set - skipping test")
        return
    
    provider = OpenAIModelProvider(api_key)
    
    # Test 1: Normal call should complete
    logger.info("Test 1: Normal call with default timeout")
    start = time.time()
    try:
        response = provider.generate_content(
            prompt="Say hello in one word",
            model_name="gpt-4.1-2025-04-14",
            temperature=0.5,
        )
        elapsed = time.time() - start
        logger.info(f"✓ Normal call completed in {elapsed:.2f}s: {response.content}")
    except Exception as e:
        logger.error(f"✗ Normal call failed: {e}")
    
    # Test 2: Call with very short timeout should fail
    logger.info("\nTest 2: Call with 0.1 second timeout (should timeout)")
    start = time.time()
    try:
        response = provider.generate_content(
            prompt="Write a long essay about quantum physics",
            model_name="gpt-4.1-2025-04-14",
            temperature=0.5,
            timeout=0.1,  # Very short timeout
        )
        elapsed = time.time() - start
        logger.error(f"✗ Call should have timed out but completed in {elapsed:.2f}s")
    except Exception as e:
        elapsed = time.time() - start
        logger.info(f"✓ Call timed out as expected after {elapsed:.2f}s: {type(e).__name__}")
    
    # Test 3: Verify default timeout is applied
    logger.info(f"\nTest 3: Verify default timeout of {DEFAULT_PROVIDER_TIMEOUT}s is used")
    logger.info("(This test just verifies the timeout parameter is passed correctly)")
    
    # We can't actually test a 5-minute timeout, but we can verify the parameter is accepted
    try:
        # This should complete quickly but accept the timeout parameter
        response = provider.generate_content(
            prompt="Say yes",
            model_name="gpt-4.1-2025-04-14",
            temperature=0.5,
            timeout=DEFAULT_PROVIDER_TIMEOUT,
        )
        logger.info(f"✓ Default timeout parameter accepted: {response.content}")
    except Exception as e:
        logger.error(f"✗ Failed with default timeout: {e}")

if __name__ == "__main__":
    asyncio.run(test_timeout())