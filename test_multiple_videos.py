#!/usr/bin/env python3
"""
Test script for multiple videos generation
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multiple_videos_generator import MultipleVideosGenerator
from config import MUSICA_DIR, RECURSOS_DIR, OUTPUT_DIR


def test_configuration():
    """Test the basic configuration and song assignment"""
    print("=== TESTING MULTIPLE VIDEOS CONFIGURATION ===\n")
    
    # Check available songs
    available_songs = []
    if os.path.exists(MUSICA_DIR):
        for filename in os.listdir(MUSICA_DIR):
            if filename.endswith(('.mp3', '.wav', '.flac', '.m4a', '.ogg')):
                available_songs.append(os.path.join(MUSICA_DIR, filename))
    
    available_songs.sort()
    print(f"Available songs ({len(available_songs)}):")
    for i, song in enumerate(available_songs, 1):
        print(f"  {i}. {os.path.basename(song)}")
    
    if len(available_songs) < 4:
        print(f"\n❌ ERROR: Need at least 4 songs for testing, found {len(available_songs)}")
        return False
        
    # Check available images
    available_images = []
    if os.path.exists(RECURSOS_DIR):
        for filename in os.listdir(RECURSOS_DIR):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                available_images.append(os.path.join(RECURSOS_DIR, filename))
                
    available_images.sort()
    print(f"\nAvailable images ({len(available_images)}):")
    for i, image in enumerate(available_images, 1):
        print(f"  {i}. {os.path.basename(image)}")
        
    # Create test configuration: 2 videos, 2 songs each, 1 repetition
    # This means each video will play its songs twice total (original + 1 repetition)
    repetitions = 1
    
    # Video 1: cancion1, cancion2 (repeated once = cancion1, cancion2, cancion1, cancion2)
    video1_songs = available_songs[:2]
    video1_repeated = video1_songs * (repetitions + 1)
    
    # Video 2: cancion3, cancion4 (repeated once = cancion3, cancion4, cancion3, cancion4)  
    video2_songs = available_songs[2:4]
    video2_repeated = video2_songs * (repetitions + 1)
    
    test_configs = [
        {
            'video_number': 1,
            'songs': video1_repeated,
            'color': 'red',
            'background_image': available_images[0] if available_images else ''
        },
        {
            'video_number': 2,
            'songs': video2_repeated,
            'color': 'blue', 
            'background_image': available_images[1] if len(available_images) > 1 else available_images[0] if available_images else ''
        }
    ]
    
    print(f"\n=== TEST CONFIGURATION (with {repetitions} repetition) ===")
    for i, config in enumerate(test_configs):
        print(f"\nVideo {config['video_number']}:")
        if i == 0:
            unique_songs = video1_songs
        else:
            unique_songs = video2_songs
        print(f"  Unique songs: {[os.path.basename(s) for s in unique_songs]}")
        print(f"  Repeated sequence: {[os.path.basename(s) for s in config['songs']]}")
        print(f"  Total plays: {len(config['songs'])} ({len(unique_songs)} songs × {repetitions + 1} times)")
        print(f"  Color: {config['color']}")
        print(f"  Background: {os.path.basename(config['background_image']) if config['background_image'] else 'Default'}")
        
    return test_configs


def progress_callback(video_number, progress, message):
    """Progress callback for testing"""
    print(f"[Video {video_number}] {progress:3d}% - {message}")


def test_generation(test_configs):
    """Test the actual video generation"""
    print(f"\n=== STARTING VIDEO GENERATION TEST ===\n")
    
    try:
        # Create generator
        generator = MultipleVideosGenerator(progress_callback=progress_callback)
        
        # Validate configurations
        print("Validating configurations...")
        is_valid, error_msg = generator.validate_configurations(test_configs)
        if not is_valid:
            print(f"❌ Configuration validation failed: {error_msg}")
            return False
            
        print("✅ Configuration validation passed")
        
        # Generate videos
        print("\nStarting video generation...")
        results = generator.generate_videos(test_configs)
        
        print(f"\n=== GENERATION RESULTS ===")
        success_count = 0
        for i, result in enumerate(results):
            config = test_configs[i]
            if result:
                print(f"✅ Video {config['video_number']}: {result}")
                success_count += 1
            else:
                print(f"❌ Video {config['video_number']}: FAILED")
                
        print(f"\nSummary: {success_count}/{len(test_configs)} videos generated successfully")
        
        if success_count == len(test_configs):
            print("🎉 ALL VIDEOS GENERATED SUCCESSFULLY!")
            return True
        else:
            print("⚠️  Some videos failed to generate")
            return False
            
    except Exception as e:
        print(f"❌ Generation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("ACE Music Video Generator - Multiple Videos Test")
    print("=" * 60)
    
    # Test configuration
    test_configs = test_configuration()
    if not test_configs:
        return False
        
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Test generation
    success = test_generation(test_configs)
    
    if success:
        print(f"\n✅ Test completed successfully!")
        print(f"Check the 'output/' directory for generated videos.")
    else:
        print(f"\n❌ Test failed!")
        print(f"Check the logs in 'output/multiple_videos.log' for details.")
        
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)