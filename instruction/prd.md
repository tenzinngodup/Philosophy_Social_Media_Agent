Here is a complete **Product Requirements Document (PRD)** tailored for use with **Cursor**. You can copy this entire content into a file named `PRD.md` in your project root. Cursor will be able to read this file and implement the agent for you.

***

# Product Requirements Document: Philosophy Social Media Agent

## 1. Project Overview
**Goal:** Create an automated social media agent that generates meaningful quotes from popular Western philosophers, creates aesthetic "Quote Cards" (images), and publishes them to social media platforms (Twitter/X, Instagram, etc.) using the Blotato API.

**Core Features:**
*   **AI Content Generation:** Uses Google Gemini to select or generate relevant quotes and context.
*   **Image Generation:** Uses Python `Pillow` to overlay text onto aesthetic backgrounds (or AI-generated backgrounds).
*   **Publishing:** Uses Blotato API to handle multi-platform posting.
*   **Automation:** Runs on a schedule using GitHub Actions.
*   **Cursor Skills Integration:** specific rule sets defined in `.cursor/rules` to guide development and maintenance.

## 2. Tech Stack
*   **Language:** Python 3.10+
*   **AI Model:** Google Gemini API (`google-genai` SDK) - Use Gemini 3 Flash
*   **Image Processing:** Pillow (`PIL`)
*   **Social Publishing:** Blotato API
*   **Infrastructure:** GitHub Actions (Workflow) with Environment Secrets
*   **Environment Management:** `dotenv`

## 3. Architecture & File Structure

```text
philosophy-bot/
├── .cursor/
│   └── rules/
│       └── agent-skills.mdc    # Cursor Skill definition for this project
├── .github/
│   └── workflows/
│       └── daily_post.yml      # Automation schedule
├── src/
│   ├── __init__.py
│   ├── ai_engine.py            # Gemini integration (Quote generation)
│   ├── image_generator.py      # Pillow logic (Text-to-Image)
│   ├── blotato_client.py       # Blotato API wrapper
│   └── main.py                 # Orchestrator
├── assets/
│   └── templates/              # Background images for quotes
├── requirements.txt
├── .env.example
├── .gitignore                  # Protects .env file
├── run.py                      # Entry point script
└── PRD.md
```

## 4. Feature Specifications

### 4.1. AI Engine (`src/ai_engine.py`)
*   **Input:** Topic (optional) or "Random".
*   **Logic:**
    *   Use `google-genai` package (NOT deprecated `google-generativeai`).
    *   Initialize: `client = genai.Client(api_key=api_key)`
    *   Model: `gemini-3-flash-preview` (or `gemini-3-pro-preview` for advanced reasoning).
    *   Call: `client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)`
    *   Prompt: "Generate a profound quote from a famous Western philosopher. Return ONLY raw JSON: `{ "quote": "...", "author": "...", "context": "..." }`"
*   **Output:** JSON object `{ "quote": "...", "author": "...", "context": "..." }`.
*   **API Docs:** https://ai.google.dev/gemini-api/docs/gemini-3

### 4.2. Image Generator (`src/image_generator.py`)
*   **Input:** Quote text, Author name.
*   **Logic:**
    *   Load a random background from `assets/templates/` (or a solid color if none exist).
    *   Use `Pillow` to wrap text, center it, and draw it with a high-contrast font.
    *   Save image to `/tmp/quote_card.jpg`.
*   **Output:** Path to the generated image file.

### 4.3. Blotato Client (`src/blotato_client.py`)
*   **Endpoint:** `POST https://backend.blotato.com/v2/posts`
*   **Authentication:** Header `Authorization: Bearer <API_KEY>` (NOT `apiKey` header).
*   **Media Upload:** Blotato `/v2/media` endpoint requires public URLs (not multipart/form-data). For local images, upload to hosting service first or post text-only.
*   **Payload Structure:**
    ```json
    {
      "post": {
        "accountId": "<BLOTATO_ACCOUNT_ID>",
        "content": {
          "text": "Quote text here",
          "mediaUrls": [],  // REQUIRED field (empty array for text-only)
          "platform": "twitter"
        },
        "target": {
          "targetType": "twitter"  // Use targetType, not platform
        }
      }
    }
    ```
*   **API Docs:** 
    *   Publish: https://help.blotato.com/api/api-reference/publish-post
    *   Media: https://help.blotato.com/api/api-reference/upload-media-v2-media

### 4.4. Automation (`.github/workflows/daily_post.yml`)
*   **Trigger:** Schedule (`cron: '0 14 * * *'`) - Runs daily at 2 PM UTC. Also supports manual trigger.
*   **Environment Secrets Setup:**
    1. Go to: Repository Settings → Environments → Create environment (e.g., `social_bot`)
    2. Add secrets to environment (NOT repository secrets):
       *   `GEMINI_API_KEY`
       *   `BLOTATO_API_KEY`
       *   `BLOTATO_ACCOUNT_ID`
*   **Workflow Configuration:**
    ```yaml
    jobs:
      job-name:
        runs-on: ubuntu-latest
        environment: social_bot  # Matches environment name
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-python@v4
            with:
              python-version: '3.10'
          - run: pip3 install -r requirements.txt
          - run: python3 run.py
            env:
              GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
              BLOTATO_API_KEY: ${{ secrets.BLOTATO_API_KEY }}
              BLOTATO_ACCOUNT_ID: ${{ secrets.BLOTATO_ACCOUNT_ID }}
    ```

## 5. Implementation Guide (For Cursor)

Use the following Context and Skills definition to instruct Cursor on how to build this.

### Step 1: Define the Cursor Skill
Create `.cursor/rules/agent-skills.mdc` with the content below. This "teaches" Cursor the specific APIs involved.

### Step 2: Generate Code
Open Cursor Chat and type:
> "Read PRD.md and the skill in .cursor/rules. Scaffold the Python project structure, install dependencies, and implement the Gemini and Image generation modules first."

---

## 6. API Schemas (Context for Cursor)

### Blotato API
*   **Publish Endpoint:** `POST https://backend.blotato.com/v2/posts`
*   **Headers:** `Content-Type: application/json`, `Authorization: Bearer <API_KEY>`
*   **Required Fields:** `accountId`, `content.text`, `content.mediaUrls` (array, can be empty), `target.targetType`
*   **Docs:** https://help.blotato.com/api/api-reference/publish-post

### Google Gemini API
*   **Package:** `google-genai` (install: `pip install google-genai`)
*   **Model:** `gemini-3-flash-preview` (fast, cost-effective) or `gemini-3-pro-preview` (advanced reasoning)
*   **Usage:**
    ```python
    from google import genai
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents="Your prompt here"
    )
    print(response.text)
    ```
*   **Docs:** https://ai.google.dev/gemini-api/docs/gemini-3

---

## Appendix: The Cursor Skill File content
*Copy the content below into `.cursor/rules/agent-skills.mdc`*

```markdown
---
description: "Expert knowledge for Philosophy Bot: Blotato API, Gemini API, and Image Generation"
globs: "*.py", ".github/workflows/*.yml"
---

# Philosophy Social Media Agent Skills

You are an expert Python developer building a social media bot. You have specific knowledge of the following APIs and libraries.

## 1. Blotato API (Publishing)
- **Base URL**: `https://backend.blotato.com/v2`
- **Publish Post**: `POST /posts`
- **Auth**: Header `Authorization: Bearer <API_KEY>` (NOT `apiKey` header)
- **Payload**:
  - Required: `accountId`, `content.text`, `content.mediaUrls` (array, required even if empty), `target.targetType`
  - `mediaUrls` must be public URLs. For local images, upload to hosting service first.
- **Sources**: 
  - https://help.blotato.com/api/api-reference/publish-post
  - https://help.blotato.com/api/api-reference/upload-media-v2-media

## 2. Google Gemini API
- **Package**: `google-genai` (NOT deprecated `google-generativeai`)
- **Initialize**: `client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])`
- **Model**: `gemini-3-flash-preview` (default) or `gemini-3-pro-preview`
- **Call**: `client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)`
- **Prompt Engineering**: Force JSON output: "Return ONLY raw JSON: {\"quote\": \"...\", \"author\": \"...\"}"
- **Source**: https://ai.google.dev/gemini-api/docs/gemini-3

## 3. Image Generation (Pillow)
- Use `from PIL import Image, ImageDraw, ImageFont`.
- Logic:
  1. Create `Image.new('RGB', (1080, 1080), color='black')`.
  2. Load a font (handle cases where fonts are missing in CI/CD environment by using a default or downloading one).
  3. Wrap text to fit within margins.
  4. Save to a temporary path.

## 4. GitHub Actions
- Use `python-version: '3.10'` and explicit `python3`/`pip3` commands.
- Use **Environment Secrets** (not repository secrets):
  - Create environment in repo settings (e.g., `social_bot`)
  - Add secrets to environment
  - Reference in workflow: `environment: social_bot`
  - Access secrets: `${{ secrets.NAME }}` (automatically uses environment secrets)
- Install dependencies: `pip3 install -r requirements.txt`

## Development Rules
- Always use `dotenv` for local environment variables.
- distinct logic for `src/ai_engine.py` (AI), `src/image_generator.py` (Visuals), and `src/main.py` (Orchestration).
- Add error handling (try/except) around all external API calls.
```