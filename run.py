#!/usr/bin/env python3
"""Entry point script for the Philosophy Social Media Agent."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.main import main

if __name__ == "__main__":
    sys.exit(main())
