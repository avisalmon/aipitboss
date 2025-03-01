# AIPitBoss

AIPitBoss is a Python package that provides a simplified interface for interacting with AI services through a unified API.

## Installation

```bash
pip install aipitboss
```

No need for service-specific installations - AIPitBoss supports all providers through a unified interface based on a `.keys.json` file.

## Features

- Simplified, unified interface for multiple AI services
- Key management through `.keys.json` file
- Streamlined chat interactions
- Comprehensive test coverage
- Pre-commit hooks for code quality

## Usage

### Simplified API

```python
from aipitboss import OpenAIService, Chat

# Initialize a service with just the service name
# This will automatically search for keys in the .keys.json file
service = OpenAIService("openai")

# Get a list of available services
available_services = service.get_services()
print(f"Available services: {available_services}")

# Change the service provider if you have multiple services configured
if "anthropic" in available_services:
    service.set_service("anthropic")

# Create a chat instance
chat = Chat(service)

# Ask a question with the simplified 'ask' method
response = chat.ask("What's the capital of France?")
print(response)
```

### OpenAI Integration

```python
from aipitboss import OpenAIService

# Create an OpenAI connection
openai = OpenAIService("openai")  # Will use key from .keys.json

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

### API Key Management

AIPitBoss provides a flexible key management system that allows you to provide API keys in several ways:

```python
from aipitboss import OpenAIService, KeyManager

# Option 1: Direct API key
openai = OpenAIService(api_key="your-openai-api-key")

# Option 2: From environment variable (OPENAI_API_KEY)
openai = OpenAIService(use_env=True)

# Option 3: From .keys.json file (preferred)
openai = OpenAIService("openai")  # Will search for .keys.json automatically

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

## Development

1. Clone the repository
2. Create a virtual environment: `python -m venv env`
3. Activate the virtual environment:
   - Windows: `env\Scripts\activate`
   - Linux/Mac: `source env/bin/activate`
4. Install development dependencies: `pip install -e ".[dev]"`
5. Run tests: `pytest -k "not live"`
   - To run live tests (requires API keys): `pytest -v --runlive`

Pre-commit hooks will automatically run tests before each commit to ensure code quality.

## License

MIT 