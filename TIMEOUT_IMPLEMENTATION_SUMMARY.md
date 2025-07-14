# Timeout Implementation Summary for Zen MCP Server

## Problem
The zen MCP server's thinkdeep tool was hanging indefinitely after completing analysis (step 3/3 with next_step_required: false) due to synchronous AI provider calls without timeout.

## Solution Implemented
Added comprehensive timeout support across the AI provider architecture:

### 1. Base Provider Changes (`providers/base.py`)
- Added `DEFAULT_PROVIDER_TIMEOUT = 300.0` (5 minutes) constant
- Updated `generate_content` abstract method signature to include `timeout: Optional[float] = None`

### 2. Workflow Mixin Changes (`tools/workflow/workflow_mixin.py`)
- Imported `DEFAULT_PROVIDER_TIMEOUT` from base provider
- Added timeout parameter to `provider.generate_content()` call at line 1478:
  ```python
  model_response = provider.generate_content(
      # ... other parameters ...
      timeout=DEFAULT_PROVIDER_TIMEOUT,
  )
  ```

### 3. Provider Implementations Updated

#### Gemini Provider (`providers/gemini.py`)
- Added timeout parameter to `generate_content` method
- Pass timeout to Google genai client:
  ```python
  response = self.client.models.generate_content(
      model=resolved_name,
      contents=contents,
      config=generation_config,
      request_options={"timeout": timeout_seconds},
  )
  ```

#### OpenAI Compatible Provider (`providers/openai_compatible.py`)
- Added timeout parameter to `generate_content` method
- Pass timeout to OpenAI client for both endpoints:
  ```python
  # Chat completions endpoint
  response = self.client.chat.completions.create(
      **completion_params,
      timeout=timeout_seconds
  )
  
  # Responses endpoint (for o3-pro)
  response = self.client.responses.create(
      **completion_params,
      timeout=timeout_seconds
  )
  ```

#### OpenAI Provider (`providers/openai_provider.py`)
- Inherits timeout functionality from OpenAICompatibleProvider
- No changes needed as it uses parent class implementation

### 4. Test Script Created (`test_timeout.py`)
- Tests normal calls complete successfully
- Tests short timeout (0.1s) fails as expected
- Tests default timeout parameter is accepted

## Usage
The timeout is now automatically applied to all AI provider calls from workflow tools:
- Default timeout: 5 minutes (300 seconds)
- Prevents indefinite hanging during heavy thinking operations
- Allows zen tools to fail gracefully if AI providers are unresponsive

## Next Steps
1. Restart the zen MCP server to apply the changes
2. Test with actual zen tool calls to verify timeout works as expected
3. Consider making timeout configurable via environment variable if needed