#!/usr/bin/env python3
"""Test script to verify timeout enforcement across all providers."""

import asyncio
import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from providers.provider_factory import ProviderFactory
from providers.base import DEFAULT_PROVIDER_TIMEOUT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test configurations
TEST_TIMEOUT = 10.0  # 10 seconds for testing
TEST_MODELS = {
    'gemini': 'gemini-2.5-flash',
    'openai': 'o3-mini',
    'xai': 'grok-3'
}

def test_provider_timeout(provider_name: str, model_name: str):
    """Test timeout enforcement for a specific provider."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing {provider_name} provider with model {model_name}")
    logger.info(f"{'='*60}")
    
    # Get provider
    provider_factory = ProviderFactory()
    provider = provider_factory.get_provider(model_name)
    
    if not provider:
        logger.error(f"Could not get provider for {model_name}")
        return False
    
    # Create a prompt that will likely take a long time
    prompt = """
    Please provide an extremely detailed analysis of the following topics:
    1. The complete history of computing from abacus to quantum computers
    2. A comprehensive explanation of all sorting algorithms with code examples
    3. The evolution of programming languages with detailed syntax comparisons
    4. A deep dive into machine learning algorithms and their mathematical foundations
    5. The future of technology for the next 100 years with specific predictions
    
    For each topic, provide at least 5000 words of detailed explanation.
    """
    
    start_time = time.time()
    
    try:
        # Call with explicit timeout
        logger.info(f"Calling {provider_name} with {TEST_TIMEOUT}s timeout...")
        response = provider.generate_content(
            prompt=prompt,
            model_name=model_name,
            timeout=TEST_TIMEOUT
        )
        
        elapsed = time.time() - start_time
        logger.warning(f"Call completed in {elapsed:.2f}s - this should have timed out!")
        return False
        
    except TimeoutError as e:
        elapsed = time.time() - start_time
        logger.info(f"✓ Timeout correctly enforced after {elapsed:.2f}s")
        logger.info(f"  Error message: {str(e)}")
        return True
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Unexpected error after {elapsed:.2f}s: {type(e).__name__}: {str(e)}")
        return False

def main():
    """Run timeout tests for all providers."""
    logger.info("Starting provider timeout tests")
    logger.info(f"Test timeout: {TEST_TIMEOUT}s")
    logger.info(f"Default provider timeout: {DEFAULT_PROVIDER_TIMEOUT}s")
    
    results = {}
    
    # Test each provider
    for provider_name, model_name in TEST_MODELS.items():
        # Check if provider is configured
        env_key = f"{provider_name.upper()}_API_KEY"
        if provider_name == 'xai':
            env_key = "XAI_API_KEY"
            
        if not os.getenv(env_key):
            logger.warning(f"Skipping {provider_name} - {env_key} not configured")
            results[provider_name] = "SKIPPED"
            continue
            
        try:
            success = test_provider_timeout(provider_name, model_name)
            results[provider_name] = "PASSED" if success else "FAILED"
        except Exception as e:
            logger.error(f"Test failed for {provider_name}: {e}")
            results[provider_name] = "ERROR"
    
    # Print summary
    logger.info(f"\n{'='*60}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*60}")
    for provider, result in results.items():
        status_symbol = "✓" if result == "PASSED" else "✗" if result in ["FAILED", "ERROR"] else "○"
        logger.info(f"{status_symbol} {provider}: {result}")
    
    # Return success if all configured providers passed
    configured_providers = [p for p, r in results.items() if r != "SKIPPED"]
    passed_providers = [p for p, r in results.items() if r == "PASSED"]
    
    if configured_providers and len(passed_providers) == len(configured_providers):
        logger.info("\n✓ All configured providers have proper timeout enforcement!")
        return 0
    else:
        logger.error("\n✗ Some providers failed timeout enforcement")
        return 1

if __name__ == "__main__":
    sys.exit(main())