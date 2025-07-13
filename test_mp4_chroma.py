#!/usr/bin/env python3
"""
Test script for MP4 greenscreen effects with different chroma parameters
"""

import os
import sys
import logging
from video_generator_optimized import OptimizedVideoGenerator
from config import MUSICA_DIR, RECURSOS_DIR, OUTPUT_DIR, GREENSCREEN_CONFIG

# Enable detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_mp4_chroma_variations():
    """Test MP4 video with different chroma key parameters"""
    print("=== TESTING MP4 CHROMA KEY VARIATIONS ===\n")
    
    generator = OptimizedVideoGenerator()
    
    # Find MP4 greenscreen effects
    available_effects = generator.get_available_greenscreen_effects()
    mp4_effects = [e for e in available_effects if e['type'] == 'video']
    
    if not mp4_effects:
        print("❌ No MP4 greenscreen effects found")
        print(f"Add MP4 files with green background to: {GREENSCREEN_CONFIG['directory']}")
        return False
    
    print(f"📹 Found {len(mp4_effects)} MP4 effect(s):")
    for effect in mp4_effects:
        print(f"   - {effect['name']}")
    
    # Get audio and background files
    audio_files = [f for f in os.listdir(MUSICA_DIR) if f.endswith(('.mp3', '.wav', '.flac', '.m4a', '.ogg'))]
    background_files = [f for f in os.listdir(RECURSOS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not audio_files or not background_files:
        print("❌ Missing audio or background files")
        return False
    
    test_audio = os.path.join(MUSICA_DIR, audio_files[0])
    test_background = os.path.join(RECURSOS_DIR, background_files[0])
    
    # Use first MP4 effect
    mp4_effect = mp4_effects[0]
    print(f"\n🎬 Testing with: {mp4_effect['name']}")
    
    # Test different parameter combinations
    test_cases = [
        {"name": "strict", "similarity": 0.2, "tolerance": 0.05},
        {"name": "normal", "similarity": 0.3, "tolerance": 0.1},
        {"name": "loose", "similarity": 0.4, "tolerance": 0.2},
        {"name": "very_loose", "similarity": 0.5, "tolerance": 0.3},
    ]
    
    results = []
    
    for i, params in enumerate(test_cases):
        test_name = params['name']
        similarity = params['similarity']
        tolerance = params['tolerance']
        
        print(f"\n🔧 Test {i+1}/4: {test_name.upper()} (sim:{similarity}, tol:{tolerance})")
        
        # Create effect with custom parameters
        test_effect = mp4_effect.copy()
        test_effect['priority'] = 1
        test_effect['custom_similarity'] = similarity
        test_effect['custom_tolerance'] = tolerance
        
        # Output path
        test_output = os.path.join(OUTPUT_DIR, f'test_chroma_{test_name}.mp4')
        
        try:
            print(f"   ⚡ Generating video...")
            success = generator.create_simple_music_video(
                test_audio, 
                test_background, 
                test_output, 
                [test_effect]
            )
            
            if success and os.path.exists(test_output):
                file_size = os.path.getsize(test_output) / (1024 * 1024)
                print(f"   ✅ Generated: {test_output}")
                print(f"   📊 Size: {file_size:.1f} MB")
                results.append((test_name, True, file_size, test_output))
            else:
                print(f"   ❌ Failed to generate")
                results.append((test_name, False, 0, None))
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append((test_name, False, 0, None))
    
    # Summary
    print(f"\n📊 RESULTS SUMMARY:")
    print(f"{'Test':<12} {'Status':<8} {'Size (MB)':<10} {'File'}")
    print(f"{'-'*60}")
    
    success_count = 0
    for test_name, success, size, file_path in results:
        status = "✅ PASS" if success else "❌ FAIL"
        size_str = f"{size:.1f}" if success else "N/A"
        file_name = os.path.basename(file_path) if file_path else "N/A"
        print(f"{test_name:<12} {status:<8} {size_str:<10} {file_name}")
        if success:
            success_count += 1
    
    print(f"\n🏁 {success_count}/{len(test_cases)} tests passed")
    
    if success_count > 0:
        print(f"\n🎯 COMPARE THE VIDEOS:")
        print(f"   Open the generated videos to see how different chroma parameters affect greenscreen removal:")
        for test_name, success, size, file_path in results:
            if success:
                print(f"   - {test_name}: {file_path}")
        
        print(f"\n💡 TIPS:")
        print(f"   • Lower similarity = more strict green detection")
        print(f"   • Lower tolerance = less bleeding/edge artifacts")
        print(f"   • If green screen is too transparent, reduce similarity")
        print(f"   • If edges look rough, adjust tolerance")
        print(f"   • Use the Preview Chroma button in the GUI for fine-tuning")
    
    return success_count > 0

def generate_chroma_info():
    """Generate information about your MP4 greenscreen video"""
    print("\n=== MP4 GREENSCREEN VIDEO ANALYSIS ===")
    
    generator = OptimizedVideoGenerator()
    available_effects = generator.get_available_greenscreen_effects()
    mp4_effects = [e for e in available_effects if e['type'] == 'video']
    
    if not mp4_effects:
        print("❌ No MP4 effects found")
        return
    
    for effect in mp4_effects:
        print(f"\n📹 Video: {effect['name']}")
        print(f"   Path: {effect['path']}")
        
        # Try to get video info using ffprobe
        try:
            import subprocess
            import json
            
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                '-show_streams', effect['path']
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                video_stream = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
                
                if video_stream:
                    print(f"   Resolution: {video_stream.get('width')}x{video_stream.get('height')}")
                    print(f"   Duration: {float(video_stream.get('duration', 0)):.1f}s")
                    print(f"   Codec: {video_stream.get('codec_name', 'unknown')}")
                    
                    # Try to detect if it might have greenscreen
                    pixel_format = video_stream.get('pix_fmt', 'unknown')
                    print(f"   Pixel format: {pixel_format}")
                    
                    if 'yuv' in pixel_format.lower():
                        print(f"   ✅ Compatible format for chroma keying")
                    else:
                        print(f"   ⚠️  May need format conversion for optimal chroma keying")
        except:
            print(f"   ❌ Could not analyze video file")

if __name__ == "__main__":
    print("🎬 MP4 CHROMA KEY TESTING TOOL")
    print("=" * 50)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # First show video analysis
    generate_chroma_info()
    
    # Then run tests
    success = test_mp4_chroma_variations()
    
    if success:
        print(f"\n🎉 MP4 CHROMA KEY SYSTEM IS WORKING!")
        print(f"   Use the 'Preview Chroma' button in the GUI to fine-tune parameters.")
    else:
        print(f"\n🔧 TROUBLESHOOTING:")
        print(f"   1. Ensure your MP4 has a pure green background (RGB 0,255,0)")
        print(f"   2. Check that the green is evenly lit (no shadows/gradients)")
        print(f"   3. Higher quality source video works better")
        print(f"   4. Try the different parameter presets")
    
    sys.exit(0 if success else 1)