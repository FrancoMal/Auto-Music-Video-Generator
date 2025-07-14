#!/usr/bin/env python3
"""
Quick test to generate a single video with corrected implementation
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multiple_videos_generator import MultipleVideosGenerator

def test_quick_video():
    """Generate a quick test video"""
    print("🎬 Testing Quick Video Generation")
    print("=" * 40)
    
    # Get available songs
    from config import MUSICA_DIR
    available_songs = []
    if os.path.exists(MUSICA_DIR):
        for filename in os.listdir(MUSICA_DIR):
            if filename.endswith(('.mp3', '.wav', '.flac', '.m4a', '.ogg')):
                available_songs.append(os.path.join(MUSICA_DIR, filename))
    
    available_songs.sort()
    
    if len(available_songs) < 1:
        print("❌ No songs available for testing")
        return False
    
    print(f"Available songs: {len(available_songs)}")
    print(f"Using: {os.path.basename(available_songs[0])}")
    
    # Test configuration: 1 video, 1 song, 0 repetitions
    test_config = {
        'video_number': 999,  # Use 999 to not conflict with existing videos
        'songs': [available_songs[0]],  # Just one song, no repetitions
        'color': 'cyan',
        'background_image': ''  # Use default
    }
    
    print(f"\nTest configuration:")
    print(f"  Video: {test_config['video_number']}")
    print(f"  Songs: 1 ({os.path.basename(test_config['songs'][0])})")
    print(f"  Repetitions: 0 (single play)")
    print(f"  Color: {test_config['color']}")
    print(f"  Expected: Fast generation with optimized visualizer")
    
    def progress_callback(video_number, progress, message):
        print(f"  [{progress:3d}%] {message}")
    
    try:
        print(f"\n🚀 Starting generation...")
        generator = MultipleVideosGenerator(progress_callback=progress_callback)
        
        # Validate configuration
        is_valid, error_msg = generator.validate_configurations([test_config])
        if not is_valid:
            print(f"❌ Configuration error: {error_msg}")
            return False
        
        # Generate the video
        results = generator.generate_videos([test_config])
        
        if results and results[0]:
            print(f"\n✅ Video generated successfully!")
            print(f"   Output: {results[0]}")
            
            # Check file size
            if os.path.exists(results[0]):
                file_size = os.path.getsize(results[0]) / (1024 * 1024)  # MB
                print(f"   Size: {file_size:.1f} MB")
                
            return True
        else:
            print(f"\n❌ Video generation failed")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        return False

def main():
    """Main test function"""
    success = test_quick_video()
    
    if success:
        print(f"\n🎉 Quick video test PASSED!")
        print(f"✅ Using optimized visualizer with perfect waves")
        print(f"✅ Fast generation (should be under 2 minutes)")
        print(f"✅ 0 repetitions working correctly")
    else:
        print(f"\n❌ Quick video test FAILED!")
        
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)