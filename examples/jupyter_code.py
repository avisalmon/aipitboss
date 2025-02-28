import json

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# AIPitBoss: OpenAI API Integration Tutorial\n",
    "\n",
    "This notebook demonstrates how to:\n",
    "1. Obtain an OpenAI API key\n",
    "2. Configure AIPitBoss to use your API key\n",
    "3. Create a simple question-answering application using AIPitBoss and OpenAI"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Step 1: Getting an OpenAI API Key\n",
    "\n",
    "To use OpenAI's API with AIPitBoss, you need an API key. Here's how to get one:\n",
    "\n",
    "1. **Create an OpenAI account**: Go to [OpenAI's website](https://openai.com/) and sign up for an account if you don't already have one.\n",
    "\n",
    "2. **Navigate to the API section**: After logging in, go to the [API keys page](https://platform.openai.com/api-keys).\n",
    "\n",
    "3. **Create a new API key**: Click on \"Create new secret key\" and give it a name (e.g., \"AIPitBoss Integration\").\n",
    "\n",
    "4. **Save your API key**: OpenAI will show you the API key once. Copy it and store it securely as you won't be able to see it again.\n",
    "\n",
    "5. **Set up billing**: Make sure you have billing set up in your OpenAI account to use the API.\n",
    "\n",
    "![OpenAI API Key Page](https://platform.openai.com/docs/images/api-keys-page.webp)\n",
    "\n",
    "**Important**: Your API key is a secret. Never share it publicly or commit it to a public repository."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Step 2: Configuring AIPitBoss with Your API Key\n",
    "\n",
    "AIPitBoss offers three ways to provide your API key:\n",
    "\n",
    "1. **Directly in code** (not recommended for production)\n",
    "2. **Using environment variables**\n",
    "3. **Using a .keys.json file** (recommended for development)\n",
    "\n",
    "Let's explore each method:"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Method 1: Direct API Key (For Testing Only)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Import AIPitBoss\n",
    "from aipitboss import OpenAIService\n",
    "\n",
    "# Initialize with direct API key (not recommended for shared or production code)\n",
    "# openai = OpenAIService(api_key='your-api-key-here')\n",
    "\n",
    "# Note: We're not executing this code as it's not the recommended approach"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Method 2: Using Environment Variables"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "from aipitboss import OpenAIService\n",
    "\n",
    "# Set environment variable (in a real environment, you'd set this in your system)\n",
    "# os.environ[\"OPENAI_API_KEY\"] = \"your-api-key-here\"\n",
    "\n",
    "# Initialize service using environment variable\n",
    "# openai = OpenAIService(use_env=True)\n",
    "\n",
    "# Check if the environment variable is already set\n",
    "if \"OPENAI_API_KEY\" in os.environ:\n",
    "    print(\"OPENAI_API_KEY environment variable is set\")\n",
    "else:\n",
    "    print(\"OPENAI_API_KEY environment variable is not set\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Method 3: Using a Keys File (Recommended for Development)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import json\n",
    "from pathlib import Path\n",
    "from aipitboss import KeyManager\n",
    "\n",
    "# Path to the keys file\n",
    "keys_file = \".keys.json\"\n",
    "\n",
    "# Check if keys file exists\n",
    "if Path(keys_file).exists():\n",
    "    print(f\"Keys file exists at {Path(keys_file).absolute()}\")\n",
    "    \n",
    "    # Load and print available services (without showing the actual keys)\n",
    "    with open(keys_file, 'r') as f:\n",
    "        keys = json.load(f)\n",
    "    print(f\"Available keys for services: {list(keys.keys())}\")\n",
    "else:\n",
    "    print(\"Keys file doesn't exist. Creating one...\")\n",
    "    \n",
    "    # Demonstration of how to create a keys file\n",
    "    # Replace 'your-api-key-here' with your actual API key\n",
    "    # KeyManager.save_keys({'openai': 'your-api-key-here'}, keys_file)\n",
    "    # print(f\"Keys file created at {Path(keys_file).absolute()}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Step 3: Using AIPitBoss to Interact with OpenAI\n",
    "\n",
    "Now that we have our API key configured, let's use AIPitBoss to interact with OpenAI's API:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "from aipitboss import OpenAIService\n",
    "\n",
    "# Initialize OpenAI service using the keys file\n",
    "openai = OpenAIService(keys_file=\".keys.json\")\n",
    "\n",
    "# Print confirmation (without revealing the actual key)\n",
    "if openai.api_key:\n",
    "    print(\"✓ Successfully initialized OpenAI service with API key\")\n",
    "    print(f\"  API key starts with: {openai.api_key[:8]}...\")\n",
    "else:\n",
    "    print(\"✗ Failed to initialize OpenAI service with API key\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Creating a Simple Question-Answering Application\n",
    "\n",
    "Let's create a simple function to ask questions to OpenAI's models using our AIPitBoss integration:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "def ask_question(question, model=\"gpt-3.5-turbo\"):\n",
    "    \"\"\"Ask a question to OpenAI and get the response.\"\"\"\n",
    "    # Prepare the messages\n",
    "    messages = [\n",
    "        {\"role\": \"system\", \"content\": \"You are a helpful, concise assistant.\"},\n",
    "        {\"role\": \"user\", \"content\": question}\n",
    "    ]\n",
    "    \n",
    "    # Make the API call\n",
    "    response = openai.chat_completion(\n",
    "        messages=messages,\n",
    "        model=model,\n",
    "        temperature=0.7,\n",
    "        max_tokens=150\n",
    "    )\n",
    "    \n",
    "    # Extract the answer text\n",
    "    answer = response[\"choices\"][0][\"message\"][\"content\"]\n",
    "    return answer"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Now let's try asking some questions:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Ask a question\n",
    "question = \"What is artificial intelligence in simple terms?\"\n",
    "print(f\"Question: {question}\")\n",
    "print(\"\\nAnswer:\")\n",
    "answer = ask_question(question)\n",
    "print(answer)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Ask another question\n",
    "question = \"What are the three main types of machine learning?\"\n",
    "print(f\"Question: {question}\")\n",
    "print(\"\\nAnswer:\")\n",
    "answer = ask_question(question)\n",
    "print(answer)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Interactive Question Answering\n",
    "\n",
    "Let's create a simple interactive interface to ask questions:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Only run this in a notebook environment\n",
    "from IPython.display import display, clear_output\n",
    "import ipywidgets as widgets\n",
    "\n",
    "# Create text input for questions\n",
    "question_input = widgets.Text(\n",
    "    value='',\n",
    "    placeholder='Type your question here',\n",
    "    description='Question:',\n",
    "    disabled=False,\n",
    "    layout=widgets.Layout(width='80%')\n",
    ")\n",
    "\n",
    "# Create output area for answers\n",
    "output = widgets.Output()\n",
    "\n",
    "# Function to handle submission\n",
    "def on_submit(b):\n",
    "    with output:\n",
    "        clear_output()\n",
    "        question = question_input.value\n",
    "        if not question.strip():\n",
    "            print(\"Please enter a question.\")\n",
    "            return\n",
    "            \n",
    "        print(f\"Q: {question}\")\n",
    "        print(\"\\nThinking...\")\n",
    "        \n",
    "        try:\n",
    "            answer = ask_question(question)\n",
    "            clear_output()\n",
    "            print(f\"Q: {question}\\n\")\n",
    "            print(f\"A: {answer}\")\n",
    "        except Exception as e:\n",
    "            clear_output()\n",
    "            print(f\"Error: {e}\")\n",
    "\n",
    "# Create button\n",
    "button = widgets.Button(\n",
    "    description='Ask',\n",
    "    disabled=False,\n",
    "    button_style='info',\n",
    "    tooltip='Ask question',\n",
    "    icon='question'\n",
    ")\n",
    "button.on_click(on_submit)\n",
    "\n",
    "# Also trigger on Enter key\n",
    "question_input.on_submit(lambda sender: on_submit(None))\n",
    "\n",
    "# Display the interface\n",
    "display(widgets.HBox([question_input, button]))\n",
    "display(output)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Additional Features\n",
    "\n",
    "### Streaming Responses\n",
    "\n",
    "AIPitBoss also supports streaming responses from OpenAI. Here's how to use it:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import requests\n",
    "from aipitboss import StreamProcessor\n",
    "\n",
    "def ask_question_streaming(question, model=\"gpt-3.5-turbo\"):\n",
    "    \"\"\"Ask a question and stream the response.\"\"\"\n",
    "    # Prepare URL and headers\n",
    "    url = \"https://api.openai.com/v1/chat/completions\"\n",
    "    headers = {\n",
    "        \"Authorization\": f\"Bearer {openai.api_key}\",\n",
    "        \"Content-Type\": \"application/json\"\n",
    "    }\n",
    "    \n",
    "    # Prepare data\n",
    "    data = {\n",
    "        \"model\": model,\n",
    "        \"messages\": [\n",
    "            {\"role\": \"system\", \"content\": \"You are a helpful, concise assistant.\"},\n",
    "            {\"role\": \"user\", \"content\": question}\n",
    "        ],\n",
    "        \"stream\": True  # Enable streaming\n",
    "    }\n",
    "    \n",
    "    print(f\"Q: {question}\\n\")\n",
    "    print(\"A: \", end=\"\", flush=True)\n",
    "    \n",
    "    # Make streaming request\n",
    "    with requests.post(url, json=data, headers=headers, stream=True) as response:\n",
    "        response.raise_for_status()\n",
    "        \n",
    "        # Process the stream\n",
    "        return StreamProcessor.process_openai_stream(\n",
    "            response.iter_lines(),\n",
    "            chunk_handler=StreamProcessor.print_stream\n",
    "        )"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Try the streaming function\n",
    "full_response = ask_question_streaming(\"Write a short poem about artificial intelligence.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Conclusion\n",
    "\n",
    "You've successfully learned how to:\n",
    "1. Obtain an OpenAI API key\n",
    "2. Configure AIPitBoss to use your API key\n",
    "3. Use AIPitBoss to create a question-answering application\n",
    "4. Implement streaming responses\n",
    "\n",
    "AIPitBoss provides a simple, intuitive interface to work with OpenAI's API, making it easy to build AI-powered applications. You can extend this notebook to explore more features like image generation, model fine-tuning, and more.\n",
    "\n",
    "For more examples, check out the other examples in the `examples/` directory of the AIPitBoss package."
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.10"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}

# Save the notebook
with open('examples/openai_notebook_example.ipynb', 'w') as f:
    json.dump(notebook, f, indent=2)

print("Jupyter notebook created successfully in examples/openai_notebook_example.ipynb") 