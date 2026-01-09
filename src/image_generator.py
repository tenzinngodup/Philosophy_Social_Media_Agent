"""Image Generator module for creating quote cards using Pillow."""

import os
import random
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont


class ImageGenerator:
    """Handles creation of quote card images."""
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the Image Generator.
        
        Args:
            templates_dir: Path to directory containing background templates.
                          Defaults to assets/templates relative to project root.
        """
        if templates_dir is None:
            # Get project root (assuming this file is in src/)
            project_root = Path(__file__).parent.parent
            templates_dir = project_root / "assets" / "templates"
        
        self.templates_dir = Path(templates_dir)
        self.image_size = (1080, 1080)
        self.margin = 80
        self.text_color = (255, 255, 255)  # White text
        self.background_color = (20, 20, 30)  # Dark background
    
    def _get_background_image(self) -> Optional[Image.Image]:
        """Load a random background image if available, otherwise return None."""
        if not self.templates_dir.exists():
            return None
        
        # Get all image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        image_files = [
            f for f in self.templates_dir.iterdir()
            if f.suffix.lower() in image_extensions and f.is_file()
        ]
        
        if not image_files:
            return None
        
        # Select random background
        bg_path = random.choice(image_files)
        try:
            bg = Image.open(bg_path)
            # Resize to match our canvas size
            bg = bg.resize(self.image_size, Image.Resampling.LANCZOS)
            return bg
        except Exception as e:
            print(f"Warning: Could not load background {bg_path}: {e}")
            return None
    
    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get a font, falling back to default if custom fonts are unavailable."""
        # Try to use a system font first
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
            "C:/Windows/Fonts/arial.ttf",  # Windows
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except Exception:
                    continue
        
        # Fallback to default font
        try:
            return ImageFont.truetype("arial.ttf", size)
        except Exception:
            return ImageFont.load_default()
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
        """Wrap text to fit within max_width pixels."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    def generate_quote_card(
        self,
        quote: str,
        author: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate a quote card image.
        
        Args:
            quote: The quote text to display.
            author: The author name to display.
            output_path: Path to save the image. Defaults to /tmp/quote_card.jpg
            
        Returns:
            Path to the generated image file.
        """
        if output_path is None:
            output_path = "/tmp/quote_card.jpg"
        
        # Create canvas
        bg_image = self._get_background_image()
        if bg_image:
            img = bg_image.copy()
        else:
            img = Image.new('RGB', self.image_size, color=self.background_color)
        
        draw = ImageDraw.Draw(img)
        
        # Get fonts
        quote_font = self._get_font(48)
        author_font = self._get_font(36)
        
        # Calculate text area
        text_area_width = self.image_size[0] - (2 * self.margin)
        
        # Wrap quote text
        quote_lines = self._wrap_text(quote, quote_font, text_area_width)
        
        # Calculate total height needed
        line_height = 60
        quote_height = len(quote_lines) * line_height
        author_height = 50
        spacing = 30
        
        total_height = quote_height + spacing + author_height
        start_y = (self.image_size[1] - total_height) // 2
        
        # Draw quote lines
        y = start_y
        for line in quote_lines:
            bbox = quote_font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            x = (self.image_size[0] - text_width) // 2
            draw.text((x, y), line, font=quote_font, fill=self.text_color)
            y += line_height
        
        # Draw author
        author_text = f"— {author}"
        bbox = author_font.getbbox(author_text)
        author_width = bbox[2] - bbox[0]
        author_x = (self.image_size[0] - author_width) // 2
        author_y = y + spacing
        
        draw.text((author_x, author_y), author_text, font=author_font, fill=self.text_color)
        
        # Save image with optimization for file size
        # Twitter limit is 5 MB, so we optimize quality to stay under limit
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Try saving with quality 95 first, then reduce if needed
        quality = 95
        img.save(output_path, 'JPEG', quality=quality, optimize=True)
        
        # Check file size and reduce quality if needed (Twitter limit: 5 MB)
        file_size = os.path.getsize(output_path)
        max_size = 5 * 1024 * 1024  # 5 MB
        
        if file_size > max_size:
            # Reduce quality until under limit
            for q in [85, 75, 65, 55]:
                img.save(output_path, 'JPEG', quality=q, optimize=True)
                if os.path.getsize(output_path) <= max_size:
                    break
        
        return output_path
