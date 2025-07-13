#!/usr/bin/env python3
"""
Test script for FIXED greenscreen effects functionality
"""

import os
import sys
import logging
from video_generator_optimized import OptimizedVideoGenerator
from config import MUSICA_DIR, RECURSOS_DIR, OUTPUT_DIR, GREENSCREEN_CONFIG

# Enable detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_single_effect():
    """Test with a single, simple PNG effect"""
    print("=== TESTING SINGLE PNG EFFECT ===\n")
    
    generator = OptimizedVideoGenerator()
    
    # Get first available files
    audio_files = [f for f in os.listdir(MUSICA_DIR) if f.endswith(('.mp3', '.wav', '.flac', '.m4a', '.ogg'))]
    background_files = [f for f in os.listdir(RECURSOS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not audio_files:
        print("❌ No audio files found")
        return False
    
    if not background_files:
        print("❌ No background images found")
        return False
    
    # Use simple files
    test_audio = os.path.join(MUSICA_DIR, audio_files[0])
    test_background = os.path.join(RECURSOS_DIR, background_files[0])
    test_output = os.path.join(OUTPUT_DIR, 'test_single_effect.mp4')
    
    print(f"🎵 Audio: {audio_files[0]}")
    print(f"🖼️  Background: {background_files[0]}")
    
    # Create ONE simple effect
    visible_effect_path = os.path.join(GREENSCREEN_CONFIG['directory'], 'visible_effect.png')
    if not os.path.exists(visible_effect_path):
        print("❌ visible_effect.png not found")
        return False
    
    # Single effect configuration
    test_effects = [{
        'name': 'visible_effect',
        'path': visible_effect_path,
        'type': 'image',
        'priority': 1
    }]
    
    print(f"🎬 Using effect: {test_effects[0]['name']}")
    print(f"📁 Output: {test_output}")
    
    # Generate video
    print("\n⚡ Generating video with corrected greenscreen system...")
    try:
        success = generator.create_simple_music_video(
            test_audio, 
            test_background, 
            test_output, 
            test_effects
        )
        
        if success and os.path.exists(test_output):
            file_size = os.path.getsize(test_output) / (1024 * 1024)
            print(f"\n✅ SUCCESS! Video generated:")
            print(f"   📄 File: {test_output}")
            print(f"   📊 Size: {file_size:.1f} MB")
            
            # Analyze the video
            import subprocess
            try:
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                    '-show_streams', test_output
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    import json
                    info = json.loads(result.stdout)
                    video_stream = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
                    if video_stream:
                        duration = float(video_stream.get('duration', 0))
                        print(f"   ⏱️  Duration: {duration:.1f} seconds")
                        print(f"   🎯 Resolution: {video_stream.get('width')}x{video_stream.get('height')}")
            except:
                pass
            
            print(f"\n🔍 Expected visual elements:")
            print(f"   • Background image from recursos/")
            print(f"   • Audio visualizer waves (red) at bottom")
            print(f"   • RED BANNER at top with 'GREENSCREEN EFFECT WORKING!' text")
            print(f"   • CYAN CIRCLE in bottom-right corner with 'EFFECT' text")
            
            return True
        else:
            print("❌ Video generation failed or file not created")
            return False
            
    except Exception as e:
        print(f"❌ Exception during generation: {e}")
        return False

def test_multiple_effects():
    """Test with multiple effects to verify priority system"""
    print("\n=== TESTING MULTIPLE EFFECTS WITH PRIORITIES ===\n")
    
    generator = OptimizedVideoGenerator()
    
    # Get available effects
    available_effects = generator.get_available_greenscreen_effects()
    if len(available_effects) < 2:
        print("❌ Need at least 2 effects for priority testing")
        return False
    
    # Get files
    audio_files = [f for f in os.listdir(MUSICA_DIR) if f.endswith(('.mp3', '.wav', '.flac', '.m4a', '.ogg'))]
    background_files = [f for f in os.listdir(RECURSOS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    test_audio = os.path.join(MUSICA_DIR, audio_files[0])
    test_background = os.path.join(RECURSOS_DIR, background_files[0])
    test_output = os.path.join(OUTPUT_DIR, 'test_multiple_effects.mp4')
    
    # Use first 2 effects with different priorities
    test_effects = []
    for i, effect in enumerate(available_effects[:2]):
        effect_config = effect.copy()
        effect_config['priority'] = i + 1  # Priority 1, 2
        test_effects.append(effect_config)
    
    print(f"🎬 Using {len(test_effects)} effects:")
    for effect in test_effects:
        print(f"   Priority {effect['priority']}: {effect['name']} ({effect['type']})")
    
    # Generate video
    print("\n⚡ Generating video with multiple effects...")
    try:
        success = generator.create_simple_music_video(
            test_audio, 
            test_background, 
            test_output, 
            test_effects
        )
        
        if success and os.path.exists(test_output):
            file_size = os.path.getsize(test_output) / (1024 * 1024)
            print(f"\n✅ SUCCESS! Multiple effects video generated:")
            print(f"   📄 File: {test_output}")
            print(f"   📊 Size: {file_size:.1f} MB")
            return True
        else:
            print("❌ Multiple effects video generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Exception during multiple effects generation: {e}")
        return False

if __name__ == "__main__":
    print("🎬 FIXED GREENSCREEN EFFECTS TEST")
    print("=" * 40)
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Test 1: Single effect (most important)
    success1 = test_single_effect()
    
    # Test 2: Multiple effects (if first succeeds)
    success2 = False
    if success1:
        success2 = test_multiple_effects()
    
    # Summary
    print(f"\n🏁 TEST RESULTS:")
    print(f"   Single effect: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"   Multiple effects: {'✅ PASSED' if success2 else '❌ FAILED' if success1 else '⏭️  SKIPPED'}")
    
    if success1:
        print(f"\n🎉 GREENSCREEN EFFECTS ARE NOW WORKING!")
        print(f"   Open the video file to see the effects overlaid on your video.")
        print(f"   The red banner and cyan circle should be clearly visible.")
    else:
        print(f"\n🔧 TROUBLESHOOTING:")
        print(f"   1. Check that visible_effect.png exists in 'greenscreen effects/'")
        print(f"   2. Verify audio files exist in 'musica/'")
        print(f"   3. Verify background images exist in 'recursos/'")
        print(f"   4. Check the logs above for specific errors")
    
    sys.exit(0 if success1 else 1)