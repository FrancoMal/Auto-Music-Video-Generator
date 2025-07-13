#!/usr/bin/env python3
"""
YouTube Scheduled Uploader
Executes scheduled uploads from youtube_upload_schedule.json
"""

import os
import json
import time
import logging
from datetime import datetime
from youtube_uploader import YouTubeUploader
from config import OUTPUT_DIR

class ScheduledUploader:
    """Handles scheduled YouTube uploads"""
    
    def __init__(self, mock_mode=False):
        self.mock_mode = mock_mode
        self.uploader = YouTubeUploader(mock_mode=mock_mode)
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging for scheduled uploads"""
        logger = logging.getLogger("ScheduledUploader")
        
        # Create log file
        log_file = os.path.join(OUTPUT_DIR, "scheduled_uploads.log")
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(logging.DEBUG)
        
        return logger
        
    def load_schedule(self):
        """Load upload schedule from JSON file"""
        schedule_file = os.path.join(OUTPUT_DIR, "youtube_upload_schedule.json")
        
        if not os.path.exists(schedule_file):
            raise FileNotFoundError(f"Schedule file not found: {schedule_file}")
            
        try:
            with open(schedule_file, 'r', encoding='utf-8') as f:
                schedule = json.load(f)
            
            self.logger.info(f"Loaded schedule with {len(schedule)} videos")
            return schedule
            
        except Exception as e:
            raise Exception(f"Error loading schedule: {e}")
            
    def authenticate(self):
        """Authenticate with YouTube"""
        success, channel_name = self.uploader.authenticate()
        if success:
            self.logger.info(f"Authenticated as: {channel_name}")
            return True
        else:
            self.logger.error("Authentication failed")
            return False
            
    def run_scheduled_uploads(self, check_interval=60):
        """
        Run scheduled uploads, checking every check_interval seconds
        
        Args:
            check_interval: How often to check for uploads (seconds)
        """
        try:
            # Load schedule
            schedule = self.load_schedule()
            
            # Authenticate
            if not self.authenticate():
                return False
                
            self.logger.info("Starting scheduled upload monitoring...")
            self.logger.info(f"Checking every {check_interval} seconds")
            
            # Track completed uploads
            completed_uploads = set()
            
            while True:
                current_time = datetime.now()
                
                for i, item in enumerate(schedule):
                    # Skip if already uploaded
                    if i in completed_uploads:
                        continue
                        
                    # Parse scheduled time
                    publish_at = datetime.fromisoformat(
                        item['publish_at'].replace('Z', '+00:00')
                    )
                    
                    # Convert to local time for comparison
                    local_publish_time = publish_at.replace(tzinfo=None)
                    
                    # Check if it's time to upload (with 1 minute tolerance)
                    time_diff = (local_publish_time - current_time).total_seconds()
                    
                    if -60 <= time_diff <= 60:  # Within 1 minute window
                        self.logger.info(f"Uploading video {item['video_number']}: {item['title']}")
                        
                        success = self._upload_video(item)
                        
                        if success:
                            completed_uploads.add(i)
                            self.logger.info(f"Successfully uploaded video {item['video_number']}")
                        else:
                            self.logger.error(f"Failed to upload video {item['video_number']}")
                            
                # Check if all uploads are complete
                if len(completed_uploads) >= len(schedule):
                    self.logger.info("All scheduled uploads completed!")
                    break
                    
                # Show next upload info
                next_upload = self._get_next_upload(schedule, completed_uploads, current_time)
                if next_upload:
                    self.logger.info(f"Next upload: {next_upload['title']} at {next_upload['date']} {next_upload['time']}")
                    
                # Wait before next check
                time.sleep(check_interval)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error in scheduled uploads: {e}")
            return False
            
    def _upload_video(self, item):
        """Upload a single video"""
        try:
            # Check if video file exists
            if not os.path.exists(item['video_path']):
                self.logger.error(f"Video file not found: {item['video_path']}")
                return False
                
            # Upload with scheduled publish time
            success, video_id, error_msg = self.uploader.upload_video(
                video_path=item['video_path'],
                title=item['title'],
                description=item['description'],
                tags=item['tags'],
                category_id=item['category_id'],
                privacy_status="private",  # Use private with scheduled publish
                publish_at=item['publish_at']
            )
            
            if success:
                self.logger.info(f"Video uploaded with ID: {video_id}")
                
                # Delete local file after successful upload
                try:
                    os.remove(item['video_path'])
                    self.logger.info(f"Deleted local file: {item['video_path']}")
                except Exception as e:
                    self.logger.warning(f"Could not delete local file: {e}")
                    
                return True
            else:
                self.logger.error(f"Upload failed: {error_msg}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error uploading video: {e}")
            return False
            
    def _get_next_upload(self, schedule, completed_uploads, current_time):
        """Get info about the next scheduled upload"""
        next_upload = None
        next_time = None
        
        for i, item in enumerate(schedule):
            if i in completed_uploads:
                continue
                
            publish_at = datetime.fromisoformat(
                item['publish_at'].replace('Z', '+00:00')
            ).replace(tzinfo=None)
            
            if publish_at > current_time:
                if next_time is None or publish_at < next_time:
                    next_time = publish_at
                    next_upload = item
                    
        return next_upload
        
    def list_schedule(self):
        """List the current upload schedule"""
        try:
            schedule = self.load_schedule()
            
            print("📅 Scheduled Uploads:")
            print("=" * 50)
            
            for item in schedule:
                publish_at = datetime.fromisoformat(
                    item['publish_at'].replace('Z', '+00:00')
                )
                local_time = publish_at.replace(tzinfo=None)
                
                print(f"🎬 Video {item['video_number']}: {item['title']}")
                print(f"   📅 {item['date']} {item['time']} (local time)")
                print(f"   📁 {os.path.basename(item['video_path'])}")
                print()
                
        except Exception as e:
            print(f"Error loading schedule: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="YouTube Scheduled Uploader")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode (no actual uploads)")
    parser.add_argument("--list", action="store_true", help="List scheduled uploads and exit")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds (default: 60)")
    
    args = parser.parse_args()
    
    uploader = ScheduledUploader(mock_mode=args.mock)
    
    if args.list:
        uploader.list_schedule()
        return
        
    print("🚀 YouTube Scheduled Uploader")
    if args.mock:
        print("⚠️  Running in MOCK mode - no actual uploads will be performed")
    print()
    
    success = uploader.run_scheduled_uploads(check_interval=args.interval)
    
    if success:
        print("✅ Scheduled uploads completed successfully!")
    else:
        print("❌ Scheduled uploads failed!")

if __name__ == "__main__":
    main()