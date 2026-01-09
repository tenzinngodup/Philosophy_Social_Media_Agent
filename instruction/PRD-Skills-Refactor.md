This is a great strategic move. By turning your hard-coded functions into **Reusable Agent Skills**, you create a library of tools that any future agent can simply "plug and play."

Below is a **Product Requirements Document (PRD)** specifically designed to refactor your current bot into a **Modular Skills Library** following the **Agent Skills specification** (referencing the concepts from `agentskills.io` regarding standardized inputs/outputs and descriptors).

You can save this as `PRD-Skills-Refactor.md`.

***

# PRD: Reusable Agent Skills Library (Blotato & Gemini)

## 1. Project Overview
**Goal:** Refactor the existing hard-coded Philosophy Bot into a set of standardized, portable **Agent Skills**.
**Objective:** Create self-contained skill packages (Blotato Publisher, Gemini Generator, Image Factory) that define their own dependencies, inputs, outputs, and metadata.
**Success Criteria:**
1.  Independent `skills/` directory where each folder is a portable skill.
2.  Each skill contains a `skill.json` (metadata) and `tool.py` (logic).
3.  The main `philosophy_bot` simply imports and orchestrates these skills, rather than containing the logic itself.

## 2. The "Agent Skill" Standard
To ensure portability to other agents (LangChain, AutoGen, or custom Cursor agents), every skill must follow this structure:

```text
skills/
└── <skill_slug>/
    ├── skill.json       # Metadata: Description, inputs, required secrets
    ├── tool.py          # The Python implementation (Class or Function)
    └── requirements.txt # Dependencies specific to this skill
```

### 2.1 Metadata Schema (`skill.json`)
```json
{
  "name": "Skill Name",
  "slug": "skill_slug",
  "version": "1.0.0",
  "description": "What this skill does...",
  "secrets": ["REQUIRED_ENV_VAR_NAME"],
  "inputs": {
    "arg_name": { "type": "string", "description": "..." }
  }
}
```

## 3. Skills to Build

### 3.1. Skill: Blotato Publisher (`skills/blotato_publish`)
*   **Purpose:** publish content to social media via Blotato.
*   **Source Logic:** Refactored from your working `blotato_client.py`.
*   **Secrets Required:** `BLOTATO_API_KEY`, `BLOTATO_ACCOUNT_ID`.
*   **Inputs:**
    *   `text` (string): The post caption/body.
    *   `media_urls` (list[string]): Optional public URLs to images/video.
    *   `platform` (string): Target platform (default: "twitter").
*   **Implementation Details:**
    *   Must use the verified **Blotato V2 API**.
    *   Headers: `Authorization: Bearer <KEY>` (Not `apiKey`).
    *   Endpoint: `https://backend.blotato.com/v2/posts`.
    *   Payload logic: Handle empty `mediaUrls` gracefully.

### 3.2. Skill: Gemini Philosopher (`skills/gemini_philosophy`)
*   **Purpose:** Generate structured philosophical content using Google's latest models.
*   **Source Logic:** Refactored from `ai_engine.py`.
*   **Secrets Required:** `GEMINI_API_KEY`.
*   **Inputs:**
    *   `topic` (string): Specific topic or "random".
    *   `model` (string): default `gemini-3-flash-preview`.
*   **Implementation Details:**
    *   Use `google-genai` SDK.
    *   Enforce JSON schema in the system prompt to ensure the output is always machine-readable (`{quote, author, context}`).

### 3.3. Skill: Quote Card Designer (`skills/quote_imager`)
*   **Purpose:** Generate a visual representation of text using Pillow.
*   **Source Logic:** Refactored from `image_generator.py`.
*   **Inputs:**
    *   `text` (string): The quote.
    *   `author` (string): The author name.
    *   `background_style` (string): "dark", "light", or path to template.
*   **Output:** Returns a file path to the generated local image.

## 4. Architecture & Migration Plan

### 4.1. New Directory Structure
```text
project_root/
├── .cursor/rules/agent-skills.mdc  # Update to read from skills/ dir
├── skills/
│   ├── blotato_publish/
│   │   ├── skill.json
│   │   ├── tool.py
│   │   └── requirements.txt
│   ├── gemini_philosophy/
│   │   ├── skill.json
│   │   └── tool.py
│   └── quote_imager/
│       ├── skill.json
│       ├── tool.py
│       └── assets/ (fonts/templates)
├── src/
│   └── main.py  # Now much smaller, just imports skills
└── run.py
```

### 4.2. Orchestration (The Main Agent)
The `main.py` will no longer hold logic. It will act as the "User" of these skills:
```python
# Conceptual Main
from skills.gemini_philosophy.tool import generate_philosophy
from skills.quote_imager.tool import create_card
from skills.blotato_publish.tool import publish_post

def run_workflow():
    # Step 1: Think
    content = generate_philosophy(topic="Stoicism")
    
    # Step 2: Create
    image_path = create_card(content['quote'], content['author'])
    
    # Step 3: Publish
    # Note: If Blotato needs a URL, we might need a step to upload image 
    # OR publish text-only if image hosting isn't available.
    publish_post(text=content['quote'], media_urls=[]) 
```

## 5. Implementation Guide for Cursor

### Step 1: Create the Skill Definitions
Ask Cursor to create the folder structure and the `skill.json` files first. This sets the strict contract for inputs/outputs.

### Step 2: Refactor Logic
Ask Cursor to move the tested logic from your existing `src/*.py` files into the respective `skills/*/tool.py` files, ensuring they read from the `skill.json` configuration where applicable.

### Step 3: Update Cursor Rules
We need to update `.cursor/rules/agent-skills.mdc` so that in the future, if you ask Cursor to "fix the blotato bug", it knows to look in `skills/blotato_publish`.

---

## 6. Updated Cursor Rules (For the new structure)

*Copy this into `.cursor/rules/modular-skills.mdc`*

```markdown
---
description: "Standard for Modular Agent Skills (Blotato, Gemini, Pillow)"
globs: "skills/**/*.py", "skills/**/*.json"
---

# Modular Agent Skills Standard

You are maintaining a library of reusable AI Agent skills. 

## Structure
Every skill resides in `skills/<skill_slug>/` and MUST contain:
1.  `skill.json`: Metadata defining inputs, outputs, and required secrets.
2.  `tool.py`: The Python implementation. The entry point function usually matches the skill name or is named `run`.
3.  `requirements.txt`: Dependencies specific to this tool.

## Skill Specifics

### Blotato Publisher (`skills/blotato_publish`)
- **API**: V2 (`https://backend.blotato.com/v2/posts`)
- **Auth**: `Authorization: Bearer <KEY>`
- **Crucial**: The `post.content.mediaUrls` field is required. Pass `[]` if no media.

### Gemini Generator (`skills/gemini_philosophy`)
- **SDK**: `google-genai`
- **Output**: Must return a Python Dictionary (parsed from JSON).

## Development Rules
- **Isolation**: Changes to one skill should not break others.
- **Env Vars**: Skills should look for environment variables defined in their `skill.json` `secrets` array (e.g., `os.environ.get('BLOTATO_API_KEY')`).
- **Imports**: When importing skills in `main.py`, use absolute imports: `from skills.blotato_publish.tool import publish_to_blotato`.
```

***

## How to execute this with Cursor:

1.  Save the content above as `PRD-Skills-Refactor.md`.
2.  Open Cursor Chat.
3.  **Prompt:**
    > "I want to refactor my project to use a Modular Skills architecture. Read `PRD-Skills-Refactor.md`.
    >
    > 1. Create the `skills/` directory structure and the `skill.json` files for Blotato, Gemini, and Image Generator.
    > 2. Move the logic from my existing `src/` files into the new `skills/*/tool.py` files.
    > 3. Create a `main.py` that imports and uses these new skills to perform the daily post."