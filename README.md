# Philosophy Social Media Agent

An automated social media agent that generates meaningful quotes from popular Western philosophers, creates aesthetic "Quote Cards" (images), and publishes them to social media platforms using the Blotato API.

## Features

- **AI Content Generation**: Uses Google Gemini to generate relevant quotes and context
- **Image Generation**: Uses Python Pillow to overlay text onto aesthetic backgrounds
- **Publishing**: Uses Blotato API to handle multi-platform posting
- **Automation**: Runs on a schedule using GitHub Actions

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Add background images (optional)**:
   - Place background images in `assets/templates/` directory
   - Supported formats: jpg, jpeg, png, webp
   - If no images are provided, the bot will use a solid color background

4. **Set up GitHub Actions secrets** (for automation):
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `BLOTATO_API_KEY`: Your Blotato API key
   - `BLOTATO_ACCOUNT_ID`: Your Blotato account ID

## Usage

### Local Execution

```bash
python run.py
```

Or alternatively:
```bash
python -m src.main
```

### Manual GitHub Actions Trigger

The workflow can be manually triggered from the GitHub Actions tab in your repository.

## Project Structure

```
philosophy-bot/
├── .cursor/
│   └── rules/
│       └── agent-skills.mdc    # Cursor Skill definition
├── .github/
│   └── workflows/
│       └── daily_post.yml      # Automation schedule
├── src/
│   ├── __init__.py
│   ├── ai_engine.py            # Gemini integration
│   ├── image_generator.py      # Pillow logic
│   ├── blotato_client.py       # Blotato API wrapper
│   └── main.py                 # Orchestrator
├── assets/
│   └── templates/              # Background images
├── requirements.txt
├── .env.example
└── PRD.md
```

## API Keys Required

- **Google Gemini API**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
  - The bot uses **Gemini 3 Flash** (`gemini-3-flash-preview`) by default for fast, cost-effective quote generation
  - You can switch to `gemini-3-pro-preview` in `src/ai_engine.py` if you need more advanced reasoning
- **Blotato API**: Get your API key and account ID from [Blotato Dashboard](https://blotato.com)

## License

MIT
