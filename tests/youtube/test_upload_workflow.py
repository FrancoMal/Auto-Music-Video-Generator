#!/usr/bin/env python3
"""
Test script for the improved YouTube upload workflow
"""

import os
import sys
import tempfile
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_youtube_upload_with_publish_at():
    """Test YouTube upload with publish_at parameter"""
    print("=== Testing YouTube Upload with publish_at ===")
    
    try:
        from youtube_uploader import YouTubeUploader
        
        # Create uploader in mock mode
        uploader = YouTubeUploader(mock_mode=True)
        
        # Test authentication
        success, channel_name = uploader.authenticate()
        assert success, "Mock authentication should succeed"
        print("✅ Authentication successful")
        
        # Create fake video file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
            tmp_file.write(b"fake video content")
            tmp_path = tmp_file.name
            
        try:
            # Test immediate upload (no publish_at)
            success, video_id, error = uploader.upload_video(
                video_path=tmp_path,
                title="Test Immediate Video",
                description="Test description",
                tags="test, immediate",
                category_id="10",
                privacy_status="public"
            )
            
            assert success, f"Immediate upload should succeed, got error: {error}"
            print("✅ Immediate upload works")
            
            # Test scheduled upload (with publish_at)
            future_time = datetime.now() + timedelta(hours=2)
            publish_at = future_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            
            success, video_id, error = uploader.upload_video(
                video_path=tmp_path,
                title="Test Scheduled Video",
                description="Test description",
                tags="test, scheduled",
                category_id="10",
                privacy_status="private",
                publish_at=publish_at
            )
            
            assert success, f"Scheduled upload should succeed, got error: {error}"
            print("✅ Scheduled upload works")
            print(f"✅ Video scheduled for: {publish_at}")
            
        finally:
            os.unlink(tmp_path)
            
        print("✅ YouTube upload with publish_at test passed!")
        return True
        
    except Exception as e:
        print(f"❌ YouTube upload test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_scheduled_mode_workflow():
    """Test the complete scheduled mode workflow"""
    print("\n=== Testing Scheduled Mode Workflow ===")
    
    try:
        from multiple_videos_generator import MultipleVideosGenerator
        from youtube_uploader import YouTubeUploader
        
        # Create mock YouTube config for scheduled mode
        mock_uploader = YouTubeUploader(mock_mode=True)
        mock_uploader.authenticate()
        
        # Create schedule with proper structure
        schedule = [
            {
                'video_number': 1,
                'title': 'Test Video #1',
                'date': '2025-07-14',
                'time': '10:00',
                'publish_at': '2025-07-14T13:00:00.000Z'  # UTC time
            },
            {
                'video_number': 2,
                'title': 'Test Video #2', 
                'date': '2025-07-14',
                'time': '14:00',
                'publish_at': '2025-07-14T17:00:00.000Z'  # UTC time
            }
        ]
        
        youtube_config = {
            'title_base': 'Test Video #{}',
            'description': 'Test video description',
            'tags': 'test, mock, scheduled',
            'category_id': '10',
            'privacy_status': 'private',
            'uploader': mock_uploader,
            'immediate_mode': False,  # Scheduled mode
            'scheduling': {
                'schedule': schedule,
                'videos_per_day': 2,
                'start_date': '14/07/2025',
                'end_date': '14/07/2025'
            }
        }
        
        # Test generator with scheduled config
        def progress_callback(video_number, progress, message):
            print(f"  Progress: Video {video_number}: {progress}% - {message}")
            
        generator = MultipleVideosGenerator(
            progress_callback=progress_callback,
            youtube_config=youtube_config
        )
        
        # Test getting schedule for specific video
        schedule_item = generator._get_schedule_for_video(1)
        assert schedule_item is not None, "Should find schedule for video 1"
        assert schedule_item['title'] == 'Test Video #1', "Should have correct title"
        print("✅ Schedule retrieval works")
        
        # Test schedule for non-existent video
        schedule_item = generator._get_schedule_for_video(99)
        assert schedule_item is None, "Should not find schedule for non-existent video"
        print("✅ Schedule retrieval handles missing videos")
        
        print("✅ Scheduled mode workflow test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Scheduled mode workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_upload_logging():
    """Test upload logging functionality"""
    print("\n=== Testing Upload Logging ===")
    
    try:
        from multiple_videos_generator import MultipleVideosGenerator
        from youtube_uploader import YouTubeUploader
        from config import OUTPUT_DIR
        import json
        
        # Create generator with mock YouTube config
        mock_uploader = YouTubeUploader(mock_mode=True)
        youtube_config = {
            'uploader': mock_uploader,
            'description': 'Test description',
            'tags': 'test, logging',
            'category_id': '10',
            'privacy_status': 'private'
        }
        
        generator = MultipleVideosGenerator(youtube_config=youtube_config)
        
        # Create test schedule item
        schedule_item = {
            'video_number': 1,
            'title': 'Test Log Video #1',
            'date': '2025-07-14',
            'time': '10:00',
            'publish_at': '2025-07-14T13:00:00.000Z'
        }
        
        # Create fake video file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
            tmp_file.write(b"fake video content for logging test")
            tmp_path = tmp_file.name
            
        try:
            # Test logging functionality
            generator._log_upload_details(1, tmp_path, 'mock_video_id_123', schedule_item)
            
            # Check if log files were created
            log_file = os.path.join(OUTPUT_DIR, "youtube_uploads.log")
            json_log_file = os.path.join(OUTPUT_DIR, "youtube_uploads_detailed.json")
            
            assert os.path.exists(log_file), "Text log file should be created"
            assert os.path.exists(json_log_file), "JSON log file should be created"
            print("✅ Log files created successfully")
            
            # Check log content
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
                assert 'Test Log Video #1' in log_content, "Log should contain video title"
                assert 'mock_video_id_123' in log_content, "Log should contain video ID"
                print("✅ Text log content is correct")
                
            with open(json_log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
                assert len(log_data) > 0, "JSON log should have entries"
                assert log_data[-1]['title'] == 'Test Log Video #1', "JSON log should have correct title"
                assert log_data[-1]['youtube_id'] == 'mock_video_id_123', "JSON log should have correct ID"
                print("✅ JSON log content is correct")
                
        finally:
            os.unlink(tmp_path)
            
        print("✅ Upload logging test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Upload logging test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all upload workflow tests"""
    print("🧪 YouTube Upload Workflow Test Suite")
    print("=" * 50)
    
    tests = [
        test_youtube_upload_with_publish_at,
        test_scheduled_mode_workflow,
        test_upload_logging
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
        print("🎉 All upload workflow tests passed!")
        return 0
    else:
        print("💥 Some upload workflow tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())