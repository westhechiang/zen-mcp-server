#!/usr/bin/env python3
"""
Test script to validate the timeout fix for zen-chat tool calls.
This script tests that timeout parameters are properly handled by all providers.
"""

import sys
import inspect
from typing import get_type_hints

def test_provider_timeout_support():
    """Test that all providers accept timeout parameter in generate_content method."""
    
    providers_to_test = [
        ('providers.gemini', 'GeminiModelProvider'),
        ('providers.openai_compatible', 'OpenAICompatibleProvider'),
        ('providers.openai_provider', 'OpenAIProvider'),
        ('providers.xai', 'XAIProvider'),
        ('providers.dial', 'DIALProvider'),
        ('providers.custom', 'CustomModelProvider'),
        ('providers.openrouter', 'OpenRouterProvider'),
    ]
    
    results = []
    
    for module_name, class_name in providers_to_test:
        try:
            # Import the module and class
            module = __import__(module_name, fromlist=[class_name])
            provider_class = getattr(module, class_name)
            
            # Get the generate_content method signature
            generate_content_method = getattr(provider_class, 'generate_content')
            sig = inspect.signature(generate_content_method)
            
            # Check if timeout parameter exists
            has_timeout = 'timeout' in sig.parameters
            accepts_kwargs = any(param.kind == param.VAR_KEYWORD for param in sig.parameters.values())
            
            # Get timeout parameter details if it exists
            timeout_param = None
            if has_timeout:
                timeout_param = sig.parameters['timeout']
                
            results.append({
                'provider': class_name,
                'has_timeout': has_timeout,
                'accepts_kwargs': accepts_kwargs,
                'timeout_param': str(timeout_param) if timeout_param else None,
                'status': '✅' if has_timeout or accepts_kwargs else '❌'
            })
            
        except Exception as e:
            results.append({
                'provider': class_name,
                'has_timeout': False,
                'accepts_kwargs': False,
                'timeout_param': None,
                'status': f'❌ Error: {e}'
            })
    
    return results

def main():
    print("🔧 Testing zen-mcp-server timeout fix...")
    print("=" * 60)
    
    results = test_provider_timeout_support()
    
    all_good = True
    for result in results:
        status = result['status']
        if not status.startswith('✅'):
            all_good = False
            
        print(f"{status} {result['provider']}")
        if result['timeout_param']:
            print(f"   └─ Timeout parameter: {result['timeout_param']}")
        elif result['accepts_kwargs']:
            print(f"   └─ Accepts **kwargs (timeout inherited)")
            
    print("=" * 60)
    
    if all_good:
        print("✅ All providers support timeout parameter!")
        print("🎯 zen-chat hanging issue should be resolved.")
    else:
        print("❌ Some providers may not support timeout parameter.")
        print("⚠️  zen-chat may still hang with unsupported providers.")
        
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())