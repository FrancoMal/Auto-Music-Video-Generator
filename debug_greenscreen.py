#!/usr/bin/env python3
"""
Debug script for greenscreen effects - generates detailed FFmpeg command
"""

import os
from video_generator_optimized import OptimizedVideoGenerator
from config import MUSICA_DIR, RECURSOS_DIR, OUTPUT_DIR, GREENSCREEN_CONFIG

def debug_greenscreen_generation():
    """Debug the greenscreen video generation"""
    print("=== DEBUGGING GREENSCREEN EFFECTS ===\n")
    
    generator = OptimizedVideoGenerator()
    
    # Check for required files
    audio_files = [f for f in os.listdir(MUSICA_DIR) if f.endswith(('.mp3', '.wav', '.flac', '.m4a', '.ogg'))]
    background_files = [f for f in os.listdir(RECURSOS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not audio_files:
        print("❌ No audio files found")
        return
    
    if not background_files:
        print("❌ No background images found")
        return
    
    # Get effects
    available_effects = generator.get_available_greenscreen_effects()
    if not available_effects:
        print("❌ No greenscreen effects found")
        print(f"Add effects to: {GREENSCREEN_CONFIG['directory']}")
        return
    
    print(f"✅ Found {len(available_effects)} effects:")
    for effect in available_effects:
        print(f"   - {effect['name']} ({effect['type']})")
    
    # Create test configuration
    test_effects = []
    for i, effect in enumerate(available_effects[:2]):  # Use first 2 effects
        test_effect = effect.copy()
        test_effect['priority'] = i + 1
        test_effects.append(test_effect)
    
    print(f"\n📋 Using {len(test_effects)} effects for test:")
    for effect in test_effects:
        print(f"   Priority {effect['priority']}: {effect['name']}")
    
    # Build filter
    print("\n🔧 Building FFmpeg filter...")
    greenscreen_filter, additional_inputs = generator.build_greenscreen_filter(test_effects)
    
    print(f"Additional inputs: {len(additional_inputs)}")
    for i, input_path in enumerate(additional_inputs):
        print(f"   Input {i+2}: {os.path.basename(input_path)}")
    
    print(f"\nGreenscreen filter:")
    print(f"   {greenscreen_filter}")
    
    # Simulate the complete filter building process
    print("\n🎬 Simulating complete filter construction...")
    
    # Build base visualizer filter (mirror effect)
    viz_color = "red"  # Default color
    viz_width = 1920
    viz_height = 200
    viz_position_from_bottom = 50
    
    base_filter = (
        f'[0:v]scale=1920:1080[bg];'
        f'[1:a]showwaves=s={viz_width//2}x{viz_height}:mode=cline:colors={viz_color}:rate=30[wave_half];'
        f'[wave_half]split[wave_orig][wave_copy];'
        f'[wave_copy]hflip[wave_mirror];'
        f'[wave_orig][wave_mirror]hstack[wave_symmetric];'
        f'[bg][wave_symmetric]overlay=x=0:y=H-h-{viz_position_from_bottom}[base_with_viz]'
    )
    
    # Build overlay chain
    if test_effects:
        current_label = 'base_with_viz'
        overlay_filters = []
        
        sorted_effects = sorted(test_effects, key=lambda x: x.get('priority', 0))
        for i, effect in enumerate(sorted_effects):
            next_label = f'overlay_{i}' if i < len(sorted_effects) - 1 else 'v'
            overlay_filters.append(f'[{current_label}][effect_{i}]overlay[{next_label}]')
            current_label = next_label
        
        complete_filter = base_filter + ';' + greenscreen_filter + ';' + ';'.join(overlay_filters)
    else:
        complete_filter = base_filter.replace('[base_with_viz]', '[v]')
    
    print(f"\nComplete filter:")
    print(f"   {complete_filter}")
    
    # Build complete FFmpeg command
    print("\n🚀 Building complete FFmpeg command...")
    
    test_audio = os.path.join(MUSICA_DIR, audio_files[0])
    test_background = os.path.join(RECURSOS_DIR, background_files[0])
    test_output = os.path.join(OUTPUT_DIR, "debug_greenscreen.mp4")
    
    cmd = [
        'ffmpeg', '-y',
        '-loop', '1',
        '-i', test_background,
        '-i', test_audio
    ]
    
    # Add greenscreen effect inputs
    for effect_path in additional_inputs:
        if effect_path.endswith('.mp4'):
            cmd.extend(['-stream_loop', '-1', '-i', effect_path])
        else:
            cmd.extend(['-loop', '1', '-i', effect_path])
    
    cmd.extend([
        '-filter_complex', complete_filter,
        '-map', '[v]',
        '-map', '1:a',
        '-c:v', 'libx264',  # Use CPU encoding for debugging
        '-c:a', 'aac',
        '-b:v', '5000k',
        '-b:a', '320k',
        '-r', '30',
        '-shortest',
        '-pix_fmt', 'yuv420p',
        test_output
    ])
    
    print(f"\nFFmpeg command:")
    print(' '.join([f'"{arg}"' if ' ' in arg else arg for arg in cmd]))
    
    # Test generation
    print(f"\n⚡ Testing video generation...")
    try:
        success = generator.create_simple_music_video(
            test_audio, 
            test_background, 
            test_output, 
            test_effects
        )
        
        if success and os.path.exists(test_output):
            file_size = os.path.getsize(test_output) / (1024 * 1024)
            print(f"✅ Video generated successfully!")
            print(f"   Output: {test_output}")
            print(f"   Size: {file_size:.1f} MB")
            
            # Check video info
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
                        print(f"   Resolution: {video_stream.get('width', 'unknown')}x{video_stream.get('height', 'unknown')}")
                        print(f"   Duration: {float(video_stream.get('duration', 0)):.1f}s")
            except:
                pass
                
        else:
            print("❌ Video generation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_greenscreen_generation()