# AIPitBoss

AIPitBoss is a Python package that provides a simplified interface for interacting with AI services through a unified API. It lets you use multiple AI providers (like OpenAI, Anthropic, etc.) with a consistent interface, handling authentication, token tracking, and conversation management.

## Installation

```bash
pip install aipitboss
```

No need for service-specific installations - AIPitBoss supports all providers through a unified interface based on a `.keys.json` file.

## Features

- Unified interface for multiple AI services (OpenAI, Anthropic, etc.)
- Flexible key management (environment variables, JSON file, direct input)
- Token usage tracking and budget management
- Comprehensive conversation history management
- Save and load chat sessions
- Service switching mid-conversation
- Streaming responses (selected services)
- Comprehensive test coverage

## Core Components

AIPitBoss consists of three main components:

1. **KeyManager**: Handles API key management, validation, and service discovery
2. **AiService**: Provides a unified interface to different AI service providers
3. **Chat**: Manages conversations, history, and simplifies interactions

## Documentation

### KeyManager

The `KeyManager` handles loading and validating API keys from different sources, discovering available services and models.

#### Basic Usage

```python
from aipitboss import KeyManager

# Initialize with default options (searches for .keys.json in current directory)
keys = KeyManager()

# Check which services are available
services = keys.available_services()
print(f"Available services: {', '.join(services.keys())}")

# Print details for each service
for service, info in services.items():
    print(f"\n{service.upper()} SERVICE:")
    print(f"  Valid API key: {info['valid']}")
    print(f"  Models found: {len(info['models'])}")
    if len(info['models']) > 0:
        print(f"  First few models: {info['models'][:3]}")
```

#### Advanced KeyManager Options

```python
# Initialize with custom options
keys = KeyManager(
    keys_file="path/to/custom.keys.json",  # Custom keys file path
    use_env=True,                          # Also check environment variables
    validate_keys=True                     # Validate keys are working
)

# Get a specific API key
openai_key = keys.get_api_key("openai")

# Add a new key (will also update keys file)
keys.add_key("anthropic", "sk-ant-your-key-here")

# Update an existing key
keys.update_key("openai", "sk-your-updated-key")

# Save all keys to a file
KeyManager.save_keys(
    {"openai": "sk-your-key", "anthropic": "sk-ant-your-key"},
    file_path=".custom_keys.json"  # Optional custom path
)
```

#### Key File Format

The `.keys.json` file should have a simple structure of service names and their API keys:

```json
{
  "openai": "sk-your-openai-api-key",
  "anthropic": "sk-ant-your-anthropic-api-key",
  "huggingface": "hf_your-huggingface-api-key"
}
```

### AiService

The `AiService` class provides a unified interface to different AI providers, handling API communication, token tracking, and budget management.

#### Basic Usage

```python
from aipitboss import KeyManager, AiService

# Initialize key manager
keys = KeyManager()

# Create an OpenAI service
openai = AiService(keys, "openai", "gpt-3.5-turbo")

# Check if service was initialized successfully
if not openai.initialized:
    print("Failed to initialize OpenAI service")
    exit()

# Get service status
status = openai.get_status()
print(f"Service: {status['service']}")
print(f"Model: {status['model']}")
print(f"Initialized: {status['initialized']}")
print(f"Token budget: {status['token_budget']}")

# Make a chat completion request
response = openai.chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the capital of France?"}
    ],
    temperature=0.7,
    max_tokens=100
)

# Process the response based on service type
if openai.service_supplier == "openai":
    answer = response["choices"][0]["message"]["content"]
elif openai.service_supplier == "anthropic":
    answer = response["content"][0]["text"]
else:
    # Generic extraction
    from aipitboss import extract_text_from_response
    answer = extract_text_from_response(response, "choices.0.message.content", "No answer found")
    
print(f"Answer: {answer}")

# Check token usage
print(f"Tokens used: {openai.tokens_in} in, {openai.tokens_out} out")
print(f"Remaining budget: {openai.token_budget}")
```

#### Token Budget Management

```python
# AiService has built-in token budget management
service = AiService(keys, "openai", "gpt-3.5-turbo")

# Each request updates token counts
for i in range(5):
    response = service.chat_completion(
        messages=[{"role": "user", "content": f"Count to {i}"}]
    )
    
    print(f"Request {i+1}:")
    print(f"  Tokens in: {service.tokens_in}")
    print(f"  Tokens out: {service.tokens_out}")
    print(f"  Remaining budget: {service.token_budget}")
    
    # Service goes on hold if budget is depleted
    if service.hold:
        print("Service is on hold due to depleted budget")
        
        # Increase the budget to continue
        service.bump_budget(10000)
        print(f"Budget increased: {service.token_budget}")
```

#### Multi-Service Support

```python
# Create services for different providers
openai = AiService(keys, "openai", "gpt-3.5-turbo")
claude = AiService(keys, "anthropic", "claude-3-sonnet-20240229")

# Check if services are available
if openai.initialized and claude.initialized:
    print("Both services are available")
    
    # Get status from each service
    openai_status = openai.get_status()
    claude_status = claude.get_status()
    
    print(f"OpenAI service: {openai_status['model']}")
    print(f"Claude service: {claude_status['model']}")
```

### Chat

The `Chat` class provides a simplified interface for conversations with AI services, handling message history, token tracking, and more.

#### Basic Usage

```python
from aipitboss import KeyManager, AiService, Chat

# Set up the service
keys = KeyManager()
ai = AiService(keys, "openai", "gpt-3.5-turbo")

# Create a chat instance with custom system message
chat = Chat(ai, "You are a helpful, concise assistant. Keep responses brief.")

# Ask questions
response1 = chat.ask("What are three interesting facts about Mars?")
print(f"Response: {response1}")

# Ask follow-up questions (conversation history is maintained)
response2 = chat.ask("How does its gravity compare to Earth?")
print(f"Response: {response2}")

# Get information about the last request
info = chat.last_as_info()
print(f"Last request took {info['time_taken']:.2f} seconds")
print(f"Used {info['tokens_in']} input tokens and {info['tokens_out']} output tokens")
```

#### Enhanced Chat Features

```python
# Initialize chat as before
keys = KeyManager()
ai = AiService(keys, "openai", "gpt-3.5-turbo")
chat = Chat(ai)

# Ask initial questions
chat.ask("What's the population of Tokyo?")
chat.ask("How does that compare to New York City?")

# Get and display conversation history
history = chat.get_history()
print("Current conversation:")
for msg in history:
    print(f"[{msg['role']}]: {msg['content'][:50]}...")

# Save the chat to a file
chat.save_chat("tokyo_chat.json")
print("Chat saved to file")

# Clear history but keep system message
chat.clear_history()
print(f"History cleared. History length: {len(chat.get_history())}")

# Start a new conversation
chat.ask("What are the main programming languages used for web development?")

# Replace the conversation with a summary
chat.replace_history("We've been discussing web development languages.")
chat.ask("What are the best frameworks for JavaScript?")

# Switch to a different service (if available)
if "anthropic" in keys.available_services():
    claude = AiService(keys, "anthropic", "claude-3-sonnet-20240229")
    chat.replace_service(claude)
    print("Switched to Claude service")
    
    response = chat.ask("How do you compare to other AI assistants?")
    print(f"Claude's response: {response}")

# Load a previously saved chat
new_chat = Chat(ai)
new_chat.load_chat("tokyo_chat.json")
print("Loaded previous chat about Tokyo")
response = new_chat.ask("What's another major city in Japan?")
print(f"Response to follow-up: {response}")
```

## PyPI Documentation

### PyPI Documentation Structure

When uploading to PyPI, this README.md file will be used as the main documentation on your package's PyPI page. PyPI renders markdown, so all the formatting you see here will be preserved.

For more comprehensive documentation beyond what's in the README:

1. **Documentation Website**: Consider setting up a dedicated documentation site using tools like:
   - [Sphinx](https://www.sphinx-doc.org/): Python's standard documentation generator
   - [MkDocs](https://www.mkdocs.org/): A fast, simple static site generator
   - [Read the Docs](https://readthedocs.org/): Free hosting for documentation

2. **Documentation URL**: Add a link to your documentation website in your `setup.py`:
   ```python
   setup(
       # other parameters
       project_urls={
           "Documentation": "https://your-docs-site.com",
           "Source": "https://github.com/avisalmon/aipitboss",
       }
   )
   ```

3. **Table of Contents and Navigation**: The navigation features you mentioned (next/back buttons, table of contents) are not built into PyPI itself, but are provided by documentation tools like Sphinx or MkDocs. 

4. **Docstrings**: Make sure to include detailed docstrings in your code as they'll be used to generate API reference documentation.

## Development

1. Clone the repository
2. Create a virtual environment: `python -m venv env`
3. Activate the virtual environment:
   - Windows: `env\Scripts\activate`
   - Linux/Mac: `source env/bin/activate`
4. Install development dependencies: `pip install -e ".[dev]"`
5. Set up Git hooks (Windows): `setup_hooks.bat`
6. Run tests: `pytest -k "not live"`
   - To run live tests (requires API keys): `pytest -v --runlive`

Pre-commit hooks will automatically run tests before each commit to ensure code quality. On Windows, run the `setup_hooks.bat` script to properly configure Git hooks. If you encounter issues with the pre-commit hook, you can bypass it using `git commit --no-verify -m "your message"`.

## Development Roadmap

The following features are planned for future releases:

1. **Full Streaming Support**: Complete implementation of streaming functionality for real-time responses from AI services.
2. **Additional Service Providers**: Integration with more AI service providers beyond OpenAI and Anthropic.
3. **Enhanced Token Management**: More sophisticated token budget management and cost tracking.
4. **Improved Error Handling**: Better error messages and automatic retries for temporary service issues.
5. **Web Interface**: A simple web interface for interacting with AI services.

Contributions to any of these areas are welcome!

## License

MIT
