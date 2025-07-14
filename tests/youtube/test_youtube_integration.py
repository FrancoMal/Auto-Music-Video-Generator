#!/usr/bin/env python3
"""
Test script for YouTube integration with mock mode
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_youtube_uploader_mock():
    """Test YouTubeUploader in mock mode"""
    print("=== Testing YouTube Uploader (Mock Mode) ===")
    
    try:
        from youtube_uploader import YouTubeUploader
        
        # Create uploader in mock mode
        uploader = YouTubeUploader(mock_mode=True)
        
        # Test authentication
        print("Testing authentication...")
        success, channel_name = uploader.authenticate()
        assert success, "Mock authentication should succeed"
        assert channel_name == "Mock Channel", f"Expected 'Mock Channel', got '{channel_name}'"
        print(f"✅ Authentication successful: {channel_name}")
        
        # Test quota status
        print("Testing quota status...")
        quota_status = uploader.get_quota_status()
        print(f"✅ Quota status: {quota_status}")
        
        # Test mock upload
        print("Testing video upload...")
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
            tmp_file.write(b"fake video content")
            tmp_path = tmp_file.name
            
        try:
            success, video_id, error = uploader.upload_video(
                video_path=tmp_path,
                title="Test Video #1",
                description="Test description",
                tags="test, mock, video",
                category_id="10"
            )
            
            assert success, f"Mock upload should succeed, got error: {error}"
            assert video_id is not None, "Should return a video ID"
            print(f"✅ Upload successful: Video ID = {video_id}")
            
        finally:
            os.unlink(tmp_path)
            
        # Test quota after upload
        quota_status = uploader.get_quota_status()
        assert quota_status['videos_uploaded_today'] == 1, "Should have uploaded 1 video"
        print(f"✅ Quota updated: {quota_status}")
        
        print("✅ YouTube Uploader mock test passed!")
        return True
        
    except Exception as e:
        print(f"❌ YouTube Uploader test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_youtube_config_dialog():
    """Test YouTube configuration dialog"""
    print("\n=== Testing YouTube Configuration Dialog ===")
    
    try:
        # Import Qt after adding to path
        from PySide6.QtWidgets import QApplication
        from gui_components.youtube_config_dialog import YouTubeConfigDialog
        
        # Create Qt application if one doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
            
        # Create dialog in mock mode
        dialog = YouTubeConfigDialog(video_count=3, mock_mode=True)
        
        # Test dialog creation
        assert dialog.video_count == 3, f"Expected 3 videos, got {dialog.video_count}"
        assert dialog.mock_mode == True, "Should be in mock mode"
        print("✅ Dialog created successfully")
        
        # Test default values
        assert "{}" in dialog.title_sequence_edit.text(), "Title should contain {} placeholder"
        assert len(dialog.description_edit.toPlainText()) > 0, "Should have default description"
        assert len(dialog.tags_edit.text()) > 0, "Should have default tags"
        print("✅ Default values set correctly")
        
        print("✅ YouTube Configuration Dialog test passed!")
        return True
        
    except Exception as e:
        print(f"❌ YouTube Configuration Dialog test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_quota_manager():
    """Test quota management functionality"""
    print("\n=== Testing Quota Manager ===")
    
    try:
        from youtube_uploader import YouTubeQuotaManager
        
        # Create quota manager
        quota_manager = YouTubeQuotaManager(daily_limit=6)
        
        # Test initial state
        assert quota_manager.can_upload(), "Should be able to upload initially"
        assert quota_manager.videos_uploaded_today == 0, "Should start with 0 uploads"
        print("✅ Initial state correct")
        
        # Test uploads up to limit
        for i in range(6):
            assert quota_manager.can_upload(), f"Should be able to upload video {i+1}"
            quota_manager.record_upload()
            
        print(f"✅ Uploaded {quota_manager.videos_uploaded_today} videos")
        
        # Test limit reached
        assert not quota_manager.can_upload(), "Should not be able to upload after limit"
        assert quota_manager.is_in_cooldown(), "Should be in cooldown"
        print("✅ Quota limit and cooldown working")
        
        # Test cooldown remaining
        remaining = quota_manager.get_cooldown_remaining()
        assert remaining is not None, "Should have cooldown time remaining"
        print(f"✅ Cooldown remaining: {remaining}")
        
        print("✅ Quota Manager test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Quota Manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_videos_generator_youtube():
    """Test MultipleVideosGenerator with YouTube config"""
    print("\n=== Testing Multiple Videos Generator with YouTube ===")
    
    try:
        from multiple_videos_generator import MultipleVideosGenerator
        from youtube_uploader import YouTubeUploader
        
        # Create mock YouTube config
        mock_uploader = YouTubeUploader(mock_mode=True)
        mock_uploader.authenticate()
        
        youtube_config = {
            'title_base': 'Test Series #{}',
            'description': 'Test video description',
            'tags': 'test, mock, series',
            'category_id': '10',
            'privacy_status': 'public',
            'uploader': mock_uploader
        }
        
        # Create generator with YouTube config
        def progress_callback(video_number, progress, message):
            print(f"Video {video_number}: {progress}% - {message}")
            
        generator = MultipleVideosGenerator(
            progress_callback=progress_callback,
            youtube_config=youtube_config
        )
        
        # Test generator creation
        assert generator.youtube_config is not None, "Should have YouTube config"
        assert generator.youtube_uploader is not None, "Should have YouTube uploader"
        print("✅ Generator created with YouTube config")
        
        # Note: We don't test actual video generation here as it requires
        # the full video generation pipeline and audio files
        
        print("✅ Multiple Videos Generator YouTube test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Multiple Videos Generator YouTube test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 YouTube Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_youtube_uploader_mock,
        test_quota_manager,
        test_youtube_config_dialog,
        test_multiple_videos_generator_youtube
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())