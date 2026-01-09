"""Main orchestrator for the Philosophy Social Media Agent."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

try:
    from .ai_engine import AIEngine
    from .image_generator import ImageGenerator
    from .blotato_client import BlotatoClient
except ImportError:
    # Fallback for direct execution
    from ai_engine import AIEngine
    from image_generator import ImageGenerator
    from blotato_client import BlotatoClient


def main():
    """Main execution function."""
    # Load environment variables from .env file if it exists
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    
    try:
        # Initialize components
        print("Initializing AI Engine...")
        ai_engine = AIEngine()
        
        print("Initializing Image Generator...")
        image_generator = ImageGenerator()
        
        print("Initializing Blotato Client...")
        blotato_client = BlotatoClient()
        
        # Generate quote
        print("Generating philosophical quote...")
        quote_data = ai_engine.generate_quote()
        
        print(f"Quote by {quote_data['author']}:")
        print(f'"{quote_data["quote"]}"')
        print(f"\nContext: {quote_data['context']}")
        
        # Generate quote card image
        print("\nGenerating quote card image...")
        image_path = image_generator.generate_quote_card(
            quote=quote_data['quote'],
            author=quote_data['author']
        )
        print(f"Image saved to: {image_path}")
        
        # Prepare post text
        post_text = f"{quote_data['quote']}\n\n— {quote_data['author']}"
        if quote_data.get('context'):
            post_text += f"\n\n{quote_data['context']}"
        
        # Publish to social media
        print("\nPublishing to social media...")
        result = blotato_client.publish_with_image(
            text=post_text,
            image_path=image_path,
            platform="twitter"  # Can be changed to "instagram" or other platforms
        )
        
        print("Successfully published post!")
        print(f"Response: {result}")
        
        return 0
        
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"Runtime error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
