#!/usr/bin/env python3
"""Test script to verify Gemini timeout fix."""

import os
import sys
import time
import logging

# Add the zen-mcp-server directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from providers.gemini import GeminiModelProvider

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_timeout():
    """Test that the Gemini provider times out correctly."""
    # Initialize provider
    provider = GeminiModelProvider()
    
    # Create a complex prompt that might take a long time
    prompt = """
    Analyze the following complex architectural system in extreme detail:
    
    Design a distributed microservices architecture for a global e-commerce platform that must:
    - Handle 10 million concurrent users
    - Process 100,000 transactions per second
    - Support 50 different payment methods
    - Operate in 200 countries with different regulations
    - Provide sub-100ms response times
    - Achieve 99.999% uptime
    - Include AI-powered recommendation engine
    - Support real-time inventory management
    - Handle flash sales with 100x traffic spikes
    
    For each microservice, provide:
    1. Detailed API specifications
    2. Database schema designs
    3. Caching strategies
    4. Message queue implementations
    5. Service mesh configurations
    6. Monitoring and alerting setup
    7. Disaster recovery procedures
    8. Security implementation details
    9. Performance optimization techniques
    10. Cost analysis and optimization strategies
    
    Additionally, analyze all possible failure modes and provide detailed mitigation strategies.
    """
    
    # Test with a short timeout (10 seconds)
    logger.info("Testing Gemini timeout with 10 second limit...")
    start_time = time.time()
    
    try:
        response = provider.generate_content(
            prompt=prompt,
            model_name="gemini-2.5-pro",
            system_prompt="You are an expert system architect.",
            timeout=10.0  # 10 second timeout
        )
        
        elapsed = time.time() - start_time
        logger.error(f"Expected timeout but got response after {elapsed:.2f} seconds")
        logger.info(f"Response preview: {response.content[:200]}...")
        
    except TimeoutError as e:
        elapsed = time.time() - start_time
        logger.info(f"✅ SUCCESS: Timeout triggered after {elapsed:.2f} seconds")
        logger.info(f"Error message: {str(e)}")
        return True
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ FAILED: Unexpected error after {elapsed:.2f} seconds: {type(e).__name__}: {str(e)}")
        return False
    
    return False

if __name__ == "__main__":
    # Check if API key is set
    if not os.environ.get("GOOGLE_API_KEY"):
        logger.error("Please set GOOGLE_API_KEY environment variable")
        sys.exit(1)
    
    logger.info("Starting Gemini timeout test...")
    success = test_timeout()
    
    if success:
        logger.info("✅ Timeout test passed!")
        sys.exit(0)
    else:
        logger.error("❌ Timeout test failed!")
        sys.exit(1)