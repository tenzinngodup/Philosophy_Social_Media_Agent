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
*   **AI Model:** Google Gemini API (`google-generativeai` SDK)
*   **Image Processing:** Pillow (`PIL`)
*   **Social Publishing:** Blotato API
*   **Infrastructure:** GitHub Actions (Workflow)
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
└── PRD.md
```

## 4. Feature Specifications

### 4.1. AI Engine (`src/ai_engine.py`)
*   **Input:** Topic (optional) or "Random".
*   **Logic:**
    *   Call Google Gemini API.
    *   Prompt: "Generate a profound quote from a famous Western philosopher (e.g., Marcus Aurelius, Nietzsche, Seneca, Kant). Output JSON with `quote`, `author`, and `short_context`."
*   **Output:** JSON object `{ "quote": "...", "author": "...", "context": "..." }`.

### 4.2. Image Generator (`src/image_generator.py`)
*   **Input:** Quote text, Author name.
*   **Logic:**
    *   Load a random background from `assets/templates/` (or a solid color if none exist).
    *   Use `Pillow` to wrap text, center it, and draw it with a high-contrast font.
    *   Save image to `/tmp/quote_card.jpg`.
*   **Output:** Path to the generated image file.

### 4.3. Blotato Client (`src/blotato_client.py`)
*   **Endpoint:** `POST https://backend.blotato.com/v2/posts`
*   **Authentication:** API Key (Header: `x-api-key` or `apiKey` - *Verify in Dashboard*).
*   **Logic:**
    *   **Upload Media:** If Blotato requires uploading first, use the `/media` endpoint. *Note: Blotato v2 often allows passing public URLs. Since we generate images locally in GitHub Actions, we might need to upload to a temporary host or use Blotato's base64/upload capability if supported.*
    *   *Workaround for Local Images:* Send the image as a `base64` string or binary upload if the API supports it. If Blotato strictly requires a URL, we may need to use a simple image host or commit the image to a generic "latest" branch (less ideal).
    *   *Refined Plan:* Use Blotato's "Upload Media" endpoint if it accepts binary/multipart, otherwise, we will post *text only* for v1 and upgrade to images if a public URL is available.
    *   **Payload Construction:**
        ```json
        {
          "post": {
            "accountId": "<BLOTATO_ACCOUNT_ID>",
            "content": {
              "text": "Quote of the day by {author}...\n\n{quote}",
              "mediaUrls": ["<UPLOADED_MEDIA_URL>"],
              "platform": "twitter"
            }
          }
        }
        ```

### 4.4. Automation (`.github/workflows/daily_post.yml`)
*   **Trigger:** Schedule (`cron: '0 14 * * *'`) - Runs daily at 2 PM UTC.
*   **Secrets Needed:**
    *   `GEMINI_API_KEY`
    *   `BLOTATO_API_KEY`
    *   `BLOTATO_ACCOUNT_ID`

## 5. Implementation Guide (For Cursor)

Use the following Context and Skills definition to instruct Cursor on how to build this.

### Step 1: Define the Cursor Skill
Create `.cursor/rules/agent-skills.mdc` with the content below. This "teaches" Cursor the specific APIs involved.

### Step 2: Generate Code
Open Cursor Chat and type:
> "Read PRD.md and the skill in .cursor/rules. Scaffold the Python project structure, install dependencies, and implement the Gemini and Image generation modules first."

---

## 6. API Schemas (Context for Cursor)

### Blotato Publish Endpoint
*   **URL:** `https://backend.blotato.com/v2/posts`
*   **Method:** `POST`
*   **Headers:** `Content-Type: application/json`, `apiKey: <YOUR_KEY>`
*   **Body:**
    ```json
    {
      "post": {
        "accountId": "string (Required)",
        "content": {
          "text": "string (Required)",
          "mediaUrls": ["string (Public URL)"],
          "platform": "twitter"
        },
        "target": { "platform": "twitter" }
      }
    }
    ```

### Google Gemini Python SDK
```python
import google.generativeai as genai
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Your prompt here")
print(response.text)
```

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
- **Auth**: Pass the API Key in the header. Check if the documentation requires `apiKey` or `Authorization`.
- **Payload**:
  - The `post` object requires `accountId`, `content` (with `text` and `mediaUrls`), and `target`.
  - `mediaUrls` expects accessible URLs. If running locally/actions, prioritize text-only posts OR implement an upload step if Blotato has a `/media` upload endpoint that accepts binary.
source:https://help.blotato.com/api/api-reference/publish-post
https://help.blotato.com/api/api-reference/upload-media-v2-media
blotato_id=blotato_account_id

## 2. Google Gemini API
- Use `google-generativeai` library.
- Always use `genai.configure(api_key=os.environ["GEMINI_API_KEY"])`.
- Use `gemini-pro` (or latest flash model) for text generation.
- **Prompt Engineering**: When asking for quotes, force JSON output to ensure the Python script can parse the Author vs Quote easily.
  - Example Prompt: "Give me a quote by Nietzsche. Return ONLY raw JSON: {\"quote\": \"...\", \"author\": \"...\"}"
use source: https://ai.google.dev/gemini-api/docs/gemini-3

## 3. Image Generation (Pillow)
- Use `from PIL import Image, ImageDraw, ImageFont`.
- Logic:
  1. Create `Image.new('RGB', (1080, 1080), color='black')`.
  2. Load a font (handle cases where fonts are missing in CI/CD environment by using a default or downloading one).
  3. Wrap text to fit within margins.
  4. Save to a temporary path.

## 4. GitHub Actions
- When writing workflows, ensure `python-version` is set to `3.10`.
- Map secrets using `${{ secrets.NAME }}`.
- Install dependencies via `pip install -r requirements.txt`.

## Development Rules
- Always use `dotenv` for local environment variables.
- distinct logic for `src/ai_engine.py` (AI), `src/image_generator.py` (Visuals), and `src/main.py` (Orchestration).
- Add error handling (try/except) around all external API calls.
```