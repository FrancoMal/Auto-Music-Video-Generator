#!/usr/bin/env python3
"""
Test script for greenscreen effects functionality
"""

import os
import sys
from video_generator_optimized import OptimizedVideoGenerator
from config import MUSICA_DIR, RECURSOS_DIR, OUTPUT_DIR, GREENSCREEN_CONFIG

def test_greenscreen_system():
    """Test the greenscreen effects system"""
    print("=== TESTING GREENSCREEN EFFECTS SYSTEM ===")
    
    # Initialize video generator
    generator = OptimizedVideoGenerator()
    
    # Test 1: Check if greenscreen directory exists
    print(f"\n1. Checking greenscreen directory: {GREENSCREEN_CONFIG['directory']}")
    if os.path.exists(GREENSCREEN_CONFIG['directory']):
        print("✓ Greenscreen directory exists")
    else:
        print("! Greenscreen directory doesn't exist - creating it...")
        os.makedirs(GREENSCREEN_CONFIG['directory'], exist_ok=True)
        print("✓ Greenscreen directory created")
    
    # Test 2: Check available effects
    print("\n2. Scanning for available effects...")
    available_effects = generator.get_available_greenscreen_effects()
    
    if available_effects:
        print(f"✓ Found {len(available_effects)} effect(s):")
        for i, effect in enumerate(available_effects, 1):
            print(f"   {i}. {effect['name']} ({effect['type']})")
            print(f"      Path: {effect['path']}")
    else:
        print("! No effects found in greenscreen directory")
        print("  To test with effects, add MP4 or PNG files to:")
        print(f"  {GREENSCREEN_CONFIG['directory']}")
        return False
    
    # Test 3: Test filter building
    print("\n3. Testing filter building...")
    
    # Create test effects with priorities
    test_effects = []
    for i, effect in enumerate(available_effects[:3]):  # Use up to 3 effects
        test_effect = effect.copy()
        test_effect['priority'] = i + 1
        test_effects.append(test_effect)
    
    if test_effects:
        greenscreen_filter, additional_inputs = generator.build_greenscreen_filter(test_effects)
        
        print(f"✓ Filter built successfully")
        print(f"  Additional inputs: {len(additional_inputs)}")
        print(f"  Filter length: {len(greenscreen_filter)} characters")
        
        if len(greenscreen_filter) > 0:
            print("  Sample filter (first 100 chars):")
            print(f"  {greenscreen_filter[:100]}...")
    
    # Test 4: Test video generation (if we have audio and background)
    print("\n4. Testing video generation...")
    
    # Check for required files
    audio_files = [f for f in os.listdir(MUSICA_DIR) if f.endswith(('.mp3', '.wav', '.flac', '.m4a', '.ogg'))]
    background_files = [f for f in os.listdir(RECURSOS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not audio_files:
        print("! No audio files found in musica/ directory")
        return False
    
    if not background_files:
        print("! No background images found in recursos/ directory")
        return False
    
    # Use first available files
    test_audio = os.path.join(MUSICA_DIR, audio_files[0])
    test_background = os.path.join(RECURSOS_DIR, background_files[0])
    test_output = os.path.join(OUTPUT_DIR, "test_greenscreen.mp4")
    
    print(f"  Using audio: {audio_files[0]}")
    print(f"  Using background: {background_files[0]}")
    print(f"  Effects: {len(test_effects)}")
    
    # Generate test video
    try:
        print("  Generating test video...")
        success = generator.create_simple_music_video(
            test_audio, 
            test_background, 
            test_output, 
            test_effects
        )
        
        if success and os.path.exists(test_output):
            file_size = os.path.getsize(test_output) / (1024 * 1024)  # MB
            print(f"✓ Test video generated successfully!")
            print(f"  Output: {test_output}")
            print(f"  File size: {file_size:.1f} MB")
        else:
            print("✗ Video generation failed")
            return False
            
    except Exception as e:
        print(f"✗ Error during video generation: {e}")
        return False
    
    print("\n=== ALL TESTS PASSED ===")
    print("Greenscreen effects system is working correctly!")
    return True

def create_sample_effects():
    """Create some sample effects for testing"""
    print("\n=== CREATING SAMPLE EFFECTS ===")
    
    # Create a simple sample PNG effect using Python PIL if available
    try:
        from PIL import Image, ImageDraw
        
        # Create a sample transparent PNG
        img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))  # Transparent background
        draw = ImageDraw.Draw(img)
        
        # Draw a simple green circle (will be made transparent by greenscreen)
        draw.ellipse([860, 490, 1060, 690], fill=(0, 255, 0, 255))  # Green circle
        
        # Draw some text
        try:
            from PIL import ImageFont
            font = ImageFont.load_default()
            draw.text((960, 540), "SAMPLE EFFECT", fill=(255, 255, 255, 255), anchor="mm")
        except:
            pass
        
        sample_path = os.path.join(GREENSCREEN_CONFIG['directory'], 'sample_effect.png')
        img.save(sample_path)
        print(f"✓ Created sample PNG effect: {sample_path}")
        
    except ImportError:
        print("! PIL not available, cannot create sample PNG")
        print("  Install with: pip install Pillow")
    
    print("\nTo test with MP4 effects:")
    print(f"1. Add MP4 files with green background to: {GREENSCREEN_CONFIG['directory']}")
    print("2. Green background should be RGB(0, 255, 0)")
    print("3. Video resolution should be 1920x1080")

if __name__ == "__main__":
    print("Greenscreen Effects Test")
    print("========================")
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Ask user if they want to create sample effects
    response = input("\nCreate sample effects for testing? (y/n): ").lower().strip()
    if response == 'y':
        create_sample_effects()
    
    # Run tests
    success = test_greenscreen_system()
    
    if success:
        print(f"\nNext steps:")
        print(f"1. Open the GUI: python multiple_videos_gui.py")
        print(f"2. Click 'Green Effects' button on any video")
        print(f"3. Select and order your effects")
        print(f"4. Generate videos with greenscreen effects!")
    else:
        print(f"\nTo fix issues:")
        print(f"1. Add effect files to: {GREENSCREEN_CONFIG['directory']}")
        print(f"2. Ensure you have audio files in: {MUSICA_DIR}")
        print(f"3. Ensure you have background images in: {RECURSOS_DIR}")
    
    sys.exit(0 if success else 1)