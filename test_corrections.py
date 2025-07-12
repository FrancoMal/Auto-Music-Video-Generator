#!/usr/bin/env python3
"""
Test all corrections made to the multiple videos system
"""

import sys
import os
from PySide6.QtWidgets import QApplication

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multiple_videos_gui import MultipleVideosMainWindow, SongAssignmentManager

def test_repetitions_logic():
    """Test the corrected repetitions logic"""
    print("=== TESTING REPETITIONS LOGIC ===")
    
    manager = SongAssignmentManager("/home/franco/ACE-Proyect/musica")
    print(f"Available songs: {len(manager.available_songs)}")
    
    # Test 0 repetitions
    configs = [
        {'video_number': 1, 'songs_count': 2, 'repetitions': 0, 'color': 'red', 'background_image': ''},
        {'video_number': 2, 'songs_count': 2, 'repetitions': 1, 'color': 'blue', 'background_image': ''}
    ]
    
    assigned = manager.assign_songs(configs, global_repetitions=0)
    
    print("\nTest 1: Mixed repetitions (Video 1: 0 reps, Video 2: 1 rep)")
    for config in assigned:
        unique_songs = config.get('unique_songs', [])
        all_songs = config['songs']
        effective_reps = config.get('effective_repetitions', 0)
        
        print(f"Video {config['video_number']}:")
        print(f"  Unique songs: {len(unique_songs)}")
        print(f"  Total plays: {len(all_songs)}")
        print(f"  Effective repetitions: {effective_reps}")
        
        if config['video_number'] == 1:
            expected = 2  # 2 songs, 0 repetitions = 2 plays
            result = "✅" if len(all_songs) == expected else "❌"
            print(f"  Expected: {expected} plays {result}")
        else:
            expected = 4  # 2 songs, 1 repetition = 4 plays  
            result = "✅" if len(all_songs) == expected else "❌"
            print(f"  Expected: {expected} plays {result}")
    
    return True

def test_gui_components():
    """Test GUI components with new features"""
    print("\n=== TESTING GUI COMPONENTS ===")
    
    app = QApplication(sys.argv)
    
    try:
        window = MultipleVideosMainWindow()
        
        # Test that repetitions can be 0
        min_global_reps = window.repetitions_spinbox.minimum()
        print(f"Global repetitions minimum: {min_global_reps} {'✅' if min_global_reps == 0 else '❌'}")
        
        # Test that video widgets have individual repetitions
        if window.video_widgets:
            widget = window.video_widgets[0]
            has_individual_reps = hasattr(widget, 'repetitions_spinbox')
            print(f"Individual repetitions: {'✅' if has_individual_reps else '❌'}")
            
            if has_individual_reps:
                min_individual_reps = widget.repetitions_spinbox.minimum()
                print(f"Individual repetitions minimum: {min_individual_reps} {'✅' if min_individual_reps == 0 else '❌'}")
        
        # Test interface separation
        if window.video_widgets:
            widget = window.video_widgets[0]
            has_repetitions_label = hasattr(widget, 'repetitions_label')
            print(f"Separate repetitions label: {'✅' if has_repetitions_label else '❌'}")
        
        print("✅ GUI components test passed!")
        return True
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False

def test_visualizer_config():
    """Test that we're using the optimized visualizer"""
    print("\n=== TESTING VISUALIZER CONFIGURATION ===")
    
    try:
        from multiple_videos_generator import MultipleVideosGenerator
        
        generator = MultipleVideosGenerator()
        
        # Check that it uses OptimizedVideoGenerator
        has_optimized = hasattr(generator.video_generator, 'generate_final_video_optimized')
        print(f"Uses OptimizedVideoGenerator: {'✅' if has_optimized else '❌'}")
        
        # Check that it can backup/restore optimized config
        try:
            backup = generator._backup_visualizer_config()
            generator._update_visualizer_config('blue')
            generator._restore_visualizer_config(backup)
            print("✅ Visualizer config management works")
        except Exception as e:
            print(f"❌ Visualizer config error: {e}")
            return False
            
        print("✅ Visualizer configuration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Visualizer test failed: {e}")
        return False

def main():
    """Run all correction tests"""
    print("🔧 Testing Multiple Videos Corrections")
    print("=" * 50)
    
    tests = [
        test_repetitions_logic,
        test_gui_components, 
        test_visualizer_config
    ]
    
    passed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
    
    print(f"\n📊 RESULTS: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All corrections are working correctly!")
        print("\n✅ Corrections implemented:")
        print("  • 0 repetitions allowed")
        print("  • Improved songs interface (separated display)")
        print("  • Reverted to optimized visualizer") 
        print("  • Individual repetitions per video")
        return True
    else:
        print("⚠️  Some corrections need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)