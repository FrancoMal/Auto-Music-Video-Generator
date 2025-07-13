#!/usr/bin/env python3
"""
Generate multiple test videos with different chroma combinations for your MP4
"""

import os
import sys
import logging
from video_generator_optimized import OptimizedVideoGenerator
from config import MUSICA_DIR, RECURSOS_DIR, OUTPUT_DIR, GREENSCREEN_CONFIG

# Enable logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def generate_test_combinations():
    """Generate test videos with different parameter combinations"""
    print("🎬 GENERATING CHROMA TEST COMBINATIONS")
    print("=" * 50)
    
    generator = OptimizedVideoGenerator()
    
    # Find your MP4 greenscreen effect
    available_effects = generator.get_available_greenscreen_effects()
    mp4_effects = [e for e in available_effects if e['type'] == 'video']
    
    if not mp4_effects:
        print("❌ No MP4 greenscreen effects found")
        return False
    
    # Use your MP4 file
    mp4_effect = mp4_effects[0]  # Assuming greenscreenfalling.mp4
    print(f"🎥 Using MP4: {mp4_effect['name']}")
    
    # Get test files
    audio_files = [f for f in os.listdir(MUSICA_DIR) if f.endswith(('.mp3', '.wav', '.flac', '.m4a', '.ogg'))]
    background_files = [f for f in os.listdir(RECURSOS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not audio_files or not background_files:
        print("❌ Missing audio or background files")
        return False
    
    # Use shorter audio for faster testing
    test_audio = os.path.join(MUSICA_DIR, audio_files[0])
    test_background = os.path.join(RECURSOS_DIR, background_files[0])
    
    print(f"🎵 Audio: {audio_files[0]}")
    print(f"🖼️  Background: {background_files[0]}")
    
    # Different parameter combinations to test
    test_combinations = [
        # Format: (name, similarity, tolerance, description)
        ("combo_01", 0.1, 0.01, "Very strict - minimal green removal"),
        ("combo_02", 0.15, 0.03, "Strict - conservative green removal"),
        ("combo_03", 0.2, 0.05, "Moderate strict"),
        ("combo_04", 0.25, 0.07, "Balanced approach"),
        ("combo_05", 0.3, 0.1, "Default settings"),
        ("combo_06", 0.35, 0.12, "Slightly loose"),
        ("combo_07", 0.4, 0.15, "Loose - more green removal"),
        ("combo_08", 0.45, 0.2, "Very loose"),
        ("combo_09", 0.5, 0.25, "Maximum removal"),
        ("combo_10", 0.6, 0.3, "Extreme - may remove too much"),
    ]
    
    print(f"\n🧪 Generating {len(test_combinations)} test videos...")
    print("This will take a few minutes. Each video will be ~30-60 seconds for quick testing.")
    
    successful_tests = []
    
    for i, (name, similarity, tolerance, description) in enumerate(test_combinations, 1):
        print(f"\n📹 Test {i:2d}/{len(test_combinations)}: {name}")
        print(f"    Similarity: {similarity:.2f}, Tolerance: {tolerance:.2f}")
        print(f"    {description}")
        
        # Create effect with specific parameters
        test_effect = mp4_effect.copy()
        test_effect['priority'] = 1
        test_effect['custom_similarity'] = similarity
        test_effect['custom_tolerance'] = tolerance
        
        # Output path
        test_output = os.path.join(OUTPUT_DIR, f'chroma_test_{name}.mp4')
        
        try:
            print(f"    ⚡ Generating...")
            
            # Use a modified version that creates shorter videos for testing
            success = generate_short_test_video(
                generator,
                test_audio, 
                test_background, 
                test_output, 
                [test_effect],
                duration_seconds=30  # Short videos for quick testing
            )
            
            if success and os.path.exists(test_output):
                file_size = os.path.getsize(test_output) / (1024 * 1024)
                print(f"    ✅ Success! Size: {file_size:.1f} MB")
                successful_tests.append((name, similarity, tolerance, description, test_output))
            else:
                print(f"    ❌ Failed")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    # Results summary
    print(f"\n📊 RESULTS SUMMARY")
    print("=" * 70)
    print(f"{'Test':<10} {'Similarity':<10} {'Tolerance':<10} {'Description':<20} {'File'}")
    print("-" * 70)
    
    for name, similarity, tolerance, description, file_path in successful_tests:
        file_name = os.path.basename(file_path)
        print(f"{name:<10} {similarity:<10.2f} {tolerance:<10.2f} {description:<20} {file_name}")
    
    if successful_tests:
        print(f"\n🎯 NEXT STEPS:")
        print(f"1. Open and compare the generated videos:")
        for name, _, _, _, file_path in successful_tests:
            print(f"   - {name}: {file_path}")
        
        print(f"\n2. Find the one where your MP4 greenscreen effect looks best")
        print(f"3. Tell me which combination works (e.g., 'combo_05 looks perfect')")
        print(f"4. I'll update the main program with those parameters")
        
        print(f"\n💡 WHAT TO LOOK FOR:")
        print(f"   ✅ Green background completely removed")
        print(f"   ✅ Clean edges on your effect")
        print(f"   ✅ No green 'halo' or bleeding")
        print(f"   ✅ Effect clearly visible over background")
        
        return True
    else:
        print(f"\n❌ No successful tests. Check your MP4 file format and green background.")
        return False

def generate_short_test_video(generator, audio_path, background_path, output_path, effects, duration_seconds=30):
    """Generate a shorter test video for quick evaluation"""
    import tempfile
    import subprocess
    
    # Create a short audio clip first
    temp_audio = os.path.join(tempfile.gettempdir(), 'short_audio.mp3')
    
    try:
        # Extract first N seconds of audio
        cmd = [
            'ffmpeg', '-y',
            '-i', audio_path,
            '-t', str(duration_seconds),
            '-c:a', 'copy',
            temp_audio
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return False
        
        # Generate video with short audio
        success = generator.create_simple_music_video(
            temp_audio,
            background_path,
            output_path,
            effects
        )
        
        # Clean up
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
        
        return success
        
    except Exception as e:
        print(f"Error creating short video: {e}")
        return False

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    success = generate_test_combinations()
    
    if not success:
        print(f"\n🔧 TROUBLESHOOTING:")
        print(f"1. Make sure your MP4 file is in: greenscreen effects/")
        print(f"2. Verify the MP4 has a green background")
        print(f"3. Check that audio and background files exist")
    
    sys.exit(0 if success else 1)