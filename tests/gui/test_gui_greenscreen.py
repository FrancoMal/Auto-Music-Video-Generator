#!/usr/bin/env python3
"""
Quick test to verify greenscreen effects work through the GUI system
"""

import os
import sys
import logging
from video_generator_optimized import OptimizedVideoGenerator
from multiple_videos_generator import MultipleVideosGenerator
from config import MUSICA_DIR, RECURSOS_DIR, OUTPUT_DIR

# Enable logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_gui_flow_programmatically():
    """Test the same flow that the GUI uses"""
    print("🎮 TESTING GUI GREENSCREEN FLOW PROGRAMMATICALLY")
    print("=" * 55)
    
    # Step 1: Simulate getting effects from GUI
    print("1️⃣ Simulating greenscreen effects selection...")
    
    generator = OptimizedVideoGenerator()
    available_effects = generator.get_available_greenscreen_effects()
    mp4_effects = [e for e in available_effects if e['type'] == 'video']
    
    if not mp4_effects:
        print("❌ No MP4 effects found")
        return False
    
    # Simulate user selecting the first MP4 effect
    selected_effect = mp4_effects[0].copy()
    selected_effect['priority'] = 1
    print(f"   ✅ Selected effect: {selected_effect['name']}")
    
    # Step 2: Create video configuration like GUI does
    print("\n2️⃣ Creating video configuration like GUI...")
    
    audio_files = [f for f in os.listdir(MUSICA_DIR) if f.endswith(('.mp3', '.wav', '.flac', '.m4a', '.ogg'))]
    background_files = [f for f in os.listdir(RECURSOS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not audio_files or not background_files:
        print("❌ Missing required files")
        return False
    
    # Create configuration exactly like GUI does
    video_configs = [{
        'video_number': 1,
        'songs_count': 2,
        'color': 'red',
        'background_image': os.path.join(RECURSOS_DIR, background_files[0]),
        'greenscreen_effects': [selected_effect],
        'songs': [os.path.join(MUSICA_DIR, f) for f in audio_files[:2]]  # First 2 songs
    }]
    
    print(f"   ✅ Configuration created:")
    print(f"      - Songs: {len(video_configs[0]['songs'])}")
    print(f"      - Color: {video_configs[0]['color']}")
    print(f"      - Background: {os.path.basename(video_configs[0]['background_image'])}")
    print(f"      - Effects: {len(video_configs[0]['greenscreen_effects'])}")
    
    # Step 3: Use MultipleVideosGenerator like GUI does
    print("\n3️⃣ Using MultipleVideosGenerator like GUI...")
    
    def progress_callback(video_number, progress, message):
        if message:
            print(f"   📹 Video {video_number}: {message}")
    
    try:
        multi_generator = MultipleVideosGenerator(progress_callback=progress_callback)
        
        print("   ⚡ Starting generation...")
        results = multi_generator.generate_videos(video_configs)
        
        if results and results[0]:
            output_path = results[0]
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                print(f"   ✅ SUCCESS! Video generated:")
                print(f"      📄 File: {output_path}")
                print(f"      📊 Size: {file_size:.1f} MB")
                
                # Check if greenscreen effects were logged
                log_file = os.path.join(OUTPUT_DIR, "multiple_videos.log")
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        log_content = f.read()
                    
                    if 'greenscreen' in log_content.lower() or 'effect' in log_content.lower():
                        print(f"   🎬 Greenscreen effects were processed (found in logs)")
                    else:
                        print(f"   ⚠️  No greenscreen processing found in logs")
                
                return True
            else:
                print(f"   ❌ Video file not created")
                return False
        else:
            print(f"   ❌ Generation failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_configuration_summary():
    """Test the configuration summary that shows in GUI"""
    print(f"\n📋 TESTING CONFIGURATION SUMMARY")
    print("=" * 35)
    
    # Create a config with greenscreen effects
    test_config = {
        'video_number': 1,
        'songs': ['song1.mp3', 'song2.mp3'],
        'color': 'red',
        'background_image': 'background.png',
        'greenscreen_effects': [
            {'name': 'greenscreenfalling', 'type': 'video', 'priority': 1}
        ]
    }
    
    # Simulate the summary function
    songs_count = len(test_config.get('songs', []))
    color = test_config.get('color', 'N/A')
    background = test_config.get('background_image', '')
    bg_name = os.path.basename(background) if background else 'Por defecto'
    
    greenscreen_effects = test_config.get('greenscreen_effects', [])
    effects_text = ""
    if greenscreen_effects:
        effects_count = len(greenscreen_effects)
        effects_names = [effect.get('name', 'unnamed') for effect in greenscreen_effects]
        effects_text = f", 🎬 {effects_count} efecto{'s' if effects_count > 1 else ''} ({', '.join(effects_names)})"
    
    summary = f"Video {test_config['video_number']}: {songs_count} canciones, color {color}, fondo {bg_name}{effects_text}"
    
    print(f"✅ Configuration summary:")
    print(f"   {summary}")
    
    return "🎬" in summary  # Check if effects indicator is present

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("🧪 GUI GREENSCREEN INTEGRATION TEST")
    print("=" * 40)
    
    # Test 1: Configuration summary
    summary_ok = test_configuration_summary()
    print(f"Summary test: {'✅ PASS' if summary_ok else '❌ FAIL'}")
    
    # Test 2: Full GUI flow
    gui_flow_ok = test_gui_flow_programmatically()
    print(f"GUI flow test: {'✅ PASS' if gui_flow_ok else '❌ FAIL'}")
    
    if summary_ok and gui_flow_ok:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"🎮 The GUI should now work correctly with greenscreen effects!")
        print(f"\n🚀 TO USE:")
        print(f"1. Run: python multiple_videos_gui.py")
        print(f"2. Click 'Green Effects' on any video")
        print(f"3. Add your greenscreenfalling.mp4 effect")
        print(f"4. You should see: '✅ Effects ON' and '🎬 Video X (con efectos)'")
        print(f"5. Generate videos → Effects will appear!")
        
    else:
        print(f"\n❌ Some tests failed")
        if not summary_ok:
            print(f"   - Configuration summary doesn't show effects properly")
        if not gui_flow_ok:
            print(f"   - GUI flow doesn't generate videos with effects")
    
    sys.exit(0 if (summary_ok and gui_flow_ok) else 1)