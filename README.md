# AIPitBoss

AIPitBoss is a Python package that provides tools for connecting to various AI APIs.

## Installation

```bash
pip install aipitboss

# Install with specific service dependencies
pip install aipitboss[openai]      # For OpenAI-specific features
pip install aipitboss[anthropic]   # For Anthropic-specific features
pip install aipitboss[huggingface] # For Hugging Face-specific features
pip install aipitboss[all]         # Install all service dependencies
```

## Usage

### Generic API Connection

```python
from aipitboss import APIConnect

# Create an API connection
api = APIConnect(
    api_key="your_api_key",
    base_url="https://api.example.com/v1"
)

# Make a request
response = api.get("/endpoint")
print(response)
```

### OpenAI Integration

```python
from aipitboss import OpenAIService

# Create an OpenAI connection
openai = OpenAIService(api_key="your_openai_api_key")

# Chat completion
response = openai.chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the capital of France?"}
    ],
    model="gpt-3.5-turbo"
)

# Extract the answer
from aipitboss import extract_text_from_response
answer = extract_text_from_response(response, "choices.0.message.content")
print(answer)

# Generate an image
image_response = openai.image_generation(
    prompt="A beautiful sunset over Paris",
    size="512x512"
)
```

### Anthropic Integration

```python
from aipitboss import AnthropicService

# Create an Anthropic connection
claude = AnthropicService(api_key="your_anthropic_api_key")

# Format messages for Claude
messages = claude.format_message_prompt(
    human_message="Explain quantum computing in simple terms"
)

# Get a response using modern messages API
response = claude.message(
    messages=messages,
    model="claude-3-opus-20240229",
    max_tokens=1000,
    system="You are a helpful, clear, and concise assistant."
)

# Extract the content
content = response["content"][0]["text"]
print(content)

# Legacy completions API
completion = claude.complete(
    prompt="What is machine learning?",
    model="claude-3-haiku-20240307",
    max_tokens_to_sample=500
)
print(completion["completion"])
```

### Hugging Face Integration

```python
from aipitboss import HuggingFaceService

# Create a Hugging Face connection
hf = HuggingFaceService(api_key="your_huggingface_api_key")

# Generate text
response = hf.text_generation(
    model="gpt2",
    prompt="Once upon a time"
)
print(response)

# Classify an image
image_response = hf.image_classification(
    model="google/vit-base-patch16-224",
    image_url="https://example.com/image.jpg"
)
```

### Streaming Support

```python
import requests
from aipitboss import StreamProcessor

# Example with OpenAI streaming
url = "https://api.openai.com/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
data = {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Write a poem"}],
    "stream": True
}

# Make streaming request
with requests.post(url, json=data, headers=headers, stream=True) as response:
    # Process the stream with default handler (prints to console)
    StreamProcessor.process_openai_stream(
        response.iter_lines(),
        chunk_handler=StreamProcessor.print_stream
    )

# Example with custom handler
def my_handler(content):
    # Do something with each chunk
    print(f"Received: {content}")

# Process with custom handler
with requests.post(url, json=data, headers=headers, stream=True) as response:
    StreamProcessor.process_openai_stream(
        response.iter_lines(),
        chunk_handler=my_handler
    )
```

### API Key Management

AIPitBoss provides a flexible key management system that allows you to provide API keys in several ways:

```python
from aipitboss import OpenAIService, KeyManager

# Option 1: Direct API key
openai = OpenAIService(api_key="your-openai-api-key")

# Option 2: From environment variable (OPENAI_API_KEY)
openai = OpenAIService(use_env=True)

# Option 3: From .keys.json file
openai = OpenAIService(keys_file=".keys.json")

# You can also use the KeyManager directly
api_key = KeyManager.get_api_key(
    service="openai",
    api_key=None,  # Explicitly provided key takes priority
    keys_file=".keys.json",
    use_env=True
)

# Save keys to a file
KeyManager.save_keys(
    {"openai": "your-key", "anthropic": "your-key"},
    keys_file=".keys.json"
)
```

You can use the included setup script to configure your API keys:

```bash
# Run the setup script
python setup_keys.py
```

The script will prompt you for your API keys and save them to `.keys.json`.

### Utility Functions

```python
from aipitboss import retry, format_prompt

# Format a prompt template
prompt = format_prompt(
    "Summarize the following text: {text}",
    text="This is a long text that needs summarization..."
)

# Use retry for API calls that might fail
def api_call():
    # Some API call that might fail
    return api.get("/endpoint")

result = retry(
    api_call,
    max_retries=5,
    retry_delay=2.0
)
```

## Development

1. Clone the repository
2. Create a virtual environment: `python -m venv env`
3. Activate the virtual environment:
   - Windows: `env\Scripts\activate`
   - Linux/Mac: `source env/bin/activate`
4. Install development dependencies: `pip install -e ".[dev]"`
5. Run tests: `pytest`

## License

MIT 