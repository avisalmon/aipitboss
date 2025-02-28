#!/usr/bin/env python
"""
Script to create the OpenAI example notebook with updated code to find keys.
"""

import json
import os
from pathlib import Path

# Load the original notebook
notebook_path = 'examples/openai_notebook_example_backup.ipynb'
with open(notebook_path, 'r') as f:
    notebook = json.load(f)

# Find the cell with the keys file code
for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code' and 'Path(keys_file).exists():' in ''.join(cell['source']):
        # Replace with our new code
        cell['source'] = [
            "import json\n",
            "import os\n",
            "from pathlib import Path\n",
            "from aipitboss import KeyManager\n",
            "\n",
            "# Check for keys file in current directory and parent directory\n",
            "current_dir_keys = \".keys.json\"\n",
            "parent_dir_keys = \"../.keys.json\"\n",
            "\n",
            "# First check current directory\n",
            "if Path(current_dir_keys).exists():\n",
            "    keys_file = current_dir_keys\n",
            "    print(f\"Keys file exists in current directory at {Path(keys_file).absolute()}\")\n",
            "# Then check parent directory\n",
            "elif Path(parent_dir_keys).exists():\n",
            "    keys_file = parent_dir_keys\n",
            "    print(f\"Keys file exists in parent directory at {Path(keys_file).absolute()}\")\n",
            "else:\n",
            "    keys_file = current_dir_keys  # Default to current directory for creation\n",
            "    print(\"Keys file doesn't exist in current or parent directory.\")\n",
            "    print(f\"Would create at: {Path(keys_file).absolute()}\")\n",
            "\n",
            "# If keys file was found, load and display available services\n",
            "if Path(keys_file).exists():\n",
            "    with open(keys_file, 'r') as f:\n",
            "        keys = json.load(f)\n",
            "    print(f\"Available keys for services: {list(keys.keys())}\")\n",
            "    \n",
            "    # Demonstration of how to create a keys file (commented out)\n",
            "    # KeyManager.save_keys({'openai': 'your-api-key-here'}, keys_file)\n",
            "    # print(f\"Keys file updated at {Path(keys_file).absolute()}\")"
        ]
        break

# Find the cell where the OpenAI service is initialized
for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code' and 'OpenAIService(keys_file=".keys.json")' in ''.join(cell['source']):
        # Update the cell to use default location checking
        cell['source'] = [
            "from aipitboss import OpenAIService\n",
            "\n",
            "# Initialize OpenAI service (will check multiple locations)\n",
            "# This will check .keys.json, ../.keys.json, and environment variables\n",
            "openai = OpenAIService()\n",
            "\n",
            "# Print confirmation (without revealing the actual key)\n",
            "if openai.api_key:\n",
            "    print(\"✓ Successfully initialized OpenAI service with API key\")\n",
            "    print(f\"  API key starts with: {openai.api_key[:8]}...\")\n",
            "else:\n",
            "    print(\"✗ Failed to initialize OpenAI service with API key\")"
        ]
        break

# Save the updated notebook
output_path = 'examples/openai_notebook_example.ipynb'
with open(output_path, 'w') as f:
    json.dump(notebook, f, indent=1)

print(f"Updated notebook saved to {output_path}") 