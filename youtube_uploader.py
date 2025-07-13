"""
YouTube Uploader Module for Music Video Generator
Handles authentication, uploading, and quota management for YouTube API
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
import pytz
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from auth import obtener_credenciales, iniciar_sesion, cerrar_sesion

class YouTubeQuotaManager:
    """Manages YouTube API quota limits (6 videos per day for unverified apps)"""
    
    def __init__(self, daily_limit: int = 6):
        self.daily_limit = daily_limit
        self.videos_uploaded_today = 0
        self.last_reset_date = datetime.now().date()
        self.quota_exceeded_until = None
        
    def can_upload(self) -> bool:
        """Check if we can upload more videos today"""
        self._reset_if_new_day()
        return self.videos_uploaded_today < self.daily_limit and not self.is_in_cooldown()
    
    def is_in_cooldown(self) -> bool:
        """Check if we're in the 24.5h cooldown period"""
        if self.quota_exceeded_until is None:
            return False
        return datetime.now() < self.quota_exceeded_until
    
    def get_cooldown_remaining(self) -> Optional[timedelta]:
        """Get remaining cooldown time"""
        if not self.is_in_cooldown():
            return None
        return self.quota_exceeded_until - datetime.now()
    
    def record_upload(self):
        """Record a successful upload"""
        self._reset_if_new_day()
        self.videos_uploaded_today += 1
        
        if self.videos_uploaded_today >= self.daily_limit:
            # Set cooldown for 24.5 hours
            self.quota_exceeded_until = datetime.now() + timedelta(hours=24, minutes=30)
            
    def _reset_if_new_day(self):
        """Reset counter if it's a new day"""
        today = datetime.now().date()
        if today > self.last_reset_date:
            self.videos_uploaded_today = 0
            self.last_reset_date = today
            self.quota_exceeded_until = None

class YouTubeUploader:
    """Main YouTube uploader class with mock capability for testing"""
    
    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.quota_manager = YouTubeQuotaManager()
        self.credentials = None
        self.youtube_service = None
        self.logger = logging.getLogger(__name__)
        
    def authenticate(self) -> Tuple[bool, Optional[str]]:
        """
        Authenticate with YouTube API
        Returns: (success, channel_name)
        """
        if self.mock_mode:
            self.logger.info("Mock mode: Simulating authentication")
            return True, "Mock Channel"
            
        try:
            self.credentials, channel_name = iniciar_sesion()
            if self.credentials and channel_name:
                self.youtube_service = build('youtube', 'v3', credentials=self.credentials)
                self.logger.info(f"Successfully authenticated as: {channel_name}")
                return True, channel_name
            else:
                self.logger.error("Authentication failed")
                return False, None
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return False, None
    
    def logout(self):
        """Logout from YouTube"""
        if self.mock_mode:
            self.logger.info("Mock mode: Simulating logout")
            return
            
        cerrar_sesion()
        self.credentials = None
        self.youtube_service = None
        self.logger.info("Logged out successfully")
    
    def upload_video(self, 
                    video_path: str, 
                    title: str, 
                    description: str, 
                    tags: str, 
                    category_id: str = "10",  # Music category
                    privacy_status: str = "public",
                    publish_at: Optional[str] = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Upload a video to YouTube
        Returns: (success, video_id, error_message)
        """
        if not self.quota_manager.can_upload():
            if self.quota_manager.is_in_cooldown():
                remaining = self.quota_manager.get_cooldown_remaining()
                error_msg = f"Quota exceeded. Cooldown remaining: {remaining}"
                self.logger.warning(error_msg)
                return False, None, error_msg
            else:
                error_msg = f"Daily upload limit reached ({self.quota_manager.daily_limit} videos)"
                self.logger.warning(error_msg)
                return False, None, error_msg
        
        if self.mock_mode:
            return self._mock_upload(video_path, title)
            
        if not self.credentials or not self.youtube_service:
            return False, None, "Not authenticated"
            
        try:
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': [tag.strip() for tag in tags.split(',') if tag.strip()],
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'madeForKids': False
                }
            }
            
            # Add scheduled publish time if provided
            if publish_at and privacy_status == "private":
                body['status']['publishAt'] = publish_at
                self.logger.info(f"Video scheduled to publish at: {publish_at}")
            
            # Upload the video
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            insert_request = self.youtube_service.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )
            
            self.logger.info(f"Uploading video: {title}")
            response = insert_request.execute()
            video_id = response['id']
            
            # Record successful upload
            self.quota_manager.record_upload()
            
            self.logger.info(f"Upload successful! Video ID: {video_id}")
            return True, video_id, None
            
        except Exception as e:
            error_msg = f"Upload failed: {str(e)}"
            self.logger.error(error_msg)
            return False, None, error_msg
    
    def _mock_upload(self, video_path: str, title: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Mock upload for testing purposes"""
        import random
        import string
        
        # Simulate upload time
        time.sleep(2)
        
        # Generate mock video ID
        video_id = ''.join(random.choices(string.ascii_letters + string.digits, k=11))
        
        # Record the upload in quota manager
        self.quota_manager.record_upload()
        
        self.logger.info(f"Mock upload successful! Video: {title}, ID: {video_id}")
        return True, video_id, None
    
    def get_quota_status(self) -> Dict[str, Any]:
        """Get current quota status"""
        return {
            'videos_uploaded_today': self.quota_manager.videos_uploaded_today,
            'daily_limit': self.quota_manager.daily_limit,
            'can_upload': self.quota_manager.can_upload(),
            'is_in_cooldown': self.quota_manager.is_in_cooldown(),
            'cooldown_remaining': self.quota_manager.get_cooldown_remaining()
        }
    
    def wait_for_quota_reset(self, progress_callback=None):
        """
        Wait for quota reset with optional progress callback
        progress_callback should accept (remaining_seconds, total_seconds)
        """
        if not self.quota_manager.is_in_cooldown():
            return
            
        remaining = self.quota_manager.get_cooldown_remaining()
        if remaining is None:
            return
            
        total_seconds = int(remaining.total_seconds())
        self.logger.info(f"Waiting for quota reset. Time remaining: {remaining}")
        
        while self.quota_manager.is_in_cooldown():
            remaining = self.quota_manager.get_cooldown_remaining()
            if remaining is None:
                break
                
            remaining_seconds = int(remaining.total_seconds())
            
            if progress_callback:
                progress_callback(remaining_seconds, total_seconds)
                
            time.sleep(60)  # Check every minute
            
        self.logger.info("Quota reset complete, ready to upload more videos")

def format_time_remaining(seconds: int) -> str:
    """Format seconds into human readable time"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"