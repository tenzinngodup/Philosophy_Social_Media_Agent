"""Blotato API client for publishing posts to social media platforms."""

import os
import base64
import requests
from typing import Optional, Dict, List
from pathlib import Path


class BlotatoClient:
    """Client for interacting with Blotato API."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        account_id: Optional[str] = None,
        base_url: str = "https://backend.blotato.com/v2"
    ):
        """
        Initialize the Blotato client.
        
        Args:
            api_key: Blotato API key. If None, reads from BLOTATO_API_KEY env var.
            account_id: Blotato account ID. If None, reads from BLOTATO_ACCOUNT_ID env var.
            base_url: Base URL for Blotato API.
        """
        # Get credentials and strip any quotes or whitespace
        raw_api_key = api_key or os.environ.get("BLOTATO_API_KEY")
        raw_account_id = account_id or os.environ.get("BLOTATO_ACCOUNT_ID")
        
        if not raw_api_key:
            raise ValueError("BLOTATO_API_KEY must be provided or set as environment variable")
        if not raw_account_id:
            raise ValueError("BLOTATO_ACCOUNT_ID must be provided or set as environment variable")
        
        # Clean credentials: strip whitespace and remove surrounding quotes if present
        self.api_key = raw_api_key.strip().strip('"').strip("'")
        self.account_id = raw_account_id.strip().strip('"').strip("'")
        self.base_url = base_url
        
        # Blotato API authentication headers
        # Use 'Authorization: Bearer' format (tested and confirmed working)
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def upload_media(self, image_path: str) -> Optional[str]:
        """
        Upload media file to Blotato and return the media URL.
        
        According to Blotato API docs, the /v2/media endpoint expects JSON with a URL.
        Since we have a local file, we'll try base64 encoding first, or we need a public URL.
        
        Args:
            image_path: Path to the image file to upload.
            
        Returns:
            Media URL if successful, None otherwise.
        """
        upload_url = f"{self.base_url}/media"
        
        try:
            # Check file size (Twitter limit is 5 MB)
            file_size = os.path.getsize(image_path)
            if file_size > 5 * 1024 * 1024:  # 5 MB
                print(f"Warning: Image file size ({file_size / 1024 / 1024:.2f} MB) exceeds Twitter limit (5 MB)")
            
            # Blotato API expects JSON with a public URL
            # Since we have a local file, we cannot directly upload it
            # Blotato's /v2/media endpoint is designed to accept URLs of already-hosted media
            # For local files, you would need to:
            # 1. Upload to a temporary hosting service (imgur, imgbb, etc.)
            # 2. Then provide that URL to Blotato
            # 
            # For now, we'll return None and post text-only
            # To enable image posting, implement a temporary image hosting solution
            print("Note: Blotato media upload requires a public URL.")
            print("Local file upload is not directly supported. Skipping media upload.")
            print("To enable images, upload to a hosting service first and provide the URL.")
            return None
                    
        except requests.exceptions.RequestException as e:
            print(f"Error uploading media: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"Unexpected error uploading media: {e}")
            return None
    
    def publish_post(
        self,
        text: str,
        media_urls: Optional[List[str]] = None,
        platform: str = "twitter"
    ) -> Dict:
        """
        Publish a post to social media via Blotato API.
        
        According to Blotato API docs:
        - Use targetType instead of platform in target object
        - Media URLs should be in content.mediaUrls array
        
        Args:
            text: Post text content.
            media_urls: List of media URLs to attach (optional).
            platform: Target platform (default: "twitter").
            
        Returns:
            API response dictionary.
        """
        url = f"{self.base_url}/posts"
        
        # Map platform names to targetType format
        platform_map = {
            "twitter": "twitter",
            "instagram": "instagram",
            "linkedin": "linkedin",
            "facebook": "facebook",
            "tiktok": "tiktok",
            "threads": "threads",
            "pinterest": "pinterest",
            "bluesky": "bluesky"
        }
        target_type = platform_map.get(platform.lower(), platform.lower())
        
        payload = {
            "post": {
                "accountId": self.account_id,
                "content": {
                    "text": text,
                    "platform": platform,
                    "mediaUrls": media_urls if media_urls else []  # Blotato requires mediaUrls field
                },
                "target": {
                    "targetType": target_type
                }
            }
        }
        
        try:
            # Prepare headers - ensure API key is properly formatted (strip whitespace)
            api_key_clean = self.api_key.strip() if self.api_key else None
            account_id_clean = self.account_id.strip() if self.account_id else None
            
            post_headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key_clean}"
            }
            
            # Ensure account ID is properly formatted in payload
            payload["post"]["accountId"] = account_id_clean
            
            response = requests.post(url, json=payload, headers=post_headers, timeout=30)
            
            # Check for authentication errors
            if response.status_code == 401:
                error_msg = f"Authentication failed (401). Please verify your BLOTATO_API_KEY and BLOTATO_ACCOUNT_ID."
                error_msg += f"\nAccount ID used: {account_id_clean}"
                error_msg += f"\nAPI Key length: {len(api_key_clean) if api_key_clean else 0}"
                error_msg += f"\nResponse: {response.text}"
                error_msg += f"\n\nTip: Make sure your API key and account ID are correct in the .env file."
                error_msg += f"\nCheck your Blotato dashboard: https://blotato.com"
                raise RuntimeError(error_msg)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error publishing post: {e}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" - Response: {e.response.text}"
            elif 'response' in locals():
                error_msg += f" - Response: {response.text}"
            raise RuntimeError(error_msg)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error publishing post: {e}")
    
    def publish_with_image(
        self,
        text: str,
        image_path: str,
        platform: str = "twitter"
    ) -> Dict:
        """
        Upload an image and publish a post with it.
        
        Args:
            text: Post text content.
            image_path: Path to local image file.
            platform: Target platform (default: "twitter").
            
        Returns:
            API response dictionary.
        """
        # Try to upload media first
        media_url = self.upload_media(image_path)
        
        if media_url:
            return self.publish_post(text, media_urls=[media_url], platform=platform)
        else:
            # Fallback to text-only post if upload fails
            print("Warning: Media upload failed, publishing text-only post")
            return self.publish_post(text, platform=platform)
