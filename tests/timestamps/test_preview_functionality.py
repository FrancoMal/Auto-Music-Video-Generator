#!/usr/bin/env python3
"""
Test script for video metadata preview functionality
Tests the complete flow: YouTube config → Preview → Individual metadata
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules import correctly"""
    print("=== Testing Imports ===")
    
    try:
        from gui_components.youtube_config_dialog import YouTubeConfigDialog
        print("✅ YouTubeConfigDialog imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import YouTubeConfigDialog: {e}")
        return False
    
    try:
        from gui_components.video_metadata_preview_dialog import VideoMetadataPreviewDialog, VideoMetadataWidget
        print("✅ VideoMetadataPreviewDialog imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import VideoMetadataPreviewDialog: {e}")
        return False
    
    try:
        from multiple_videos_generator import MultipleVideosGenerator
        print("✅ MultipleVideosGenerator imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import MultipleVideosGenerator: {e}")
        return False
    
    try:
        from multiple_videos_gui import VideoGenerationThread, MultipleVideosMainWindow
        print("✅ Multiple videos GUI components imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import GUI components: {e}")
        return False
    
    try:
        from audio_processor import AudioProcessor
        print("✅ AudioProcessor imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AudioProcessor: {e}")
        return False
    
    return True

def test_audio_processor_timestamps():
    """Test that AudioProcessor generates clean timestamps"""
    print("\n=== Testing Audio Processor Timestamps ===")
    
    try:
        from audio_processor import AudioProcessor
        
        # Create a test instance
        ap = AudioProcessor()
        print("✅ AudioProcessor created successfully")
        
        # Test the timestamp generation (we can't easily test full functionality without audio files)
        # But we can verify the class exists and has expected methods
        expected_methods = ['generate_description_file', 'process_audio']
        for method in expected_methods:
            if hasattr(ap, method):
                print(f"✅ AudioProcessor has method: {method}")
            else:
                print(f"❌ AudioProcessor missing method: {method}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ AudioProcessor test failed: {e}")
        return False

def test_metadata_widget():
    """Test VideoMetadataWidget functionality"""
    print("\n=== Testing VideoMetadataWidget ===")
    
    try:
        from PySide6.QtWidgets import QApplication
        from gui_components.video_metadata_preview_dialog import VideoMetadataWidget
        
        # Create minimal QApplication for testing
        if not QApplication.instance():
            app = QApplication([])
        
        # Test widget creation
        widget = VideoMetadataWidget(
            video_number=1,
            title="Test Video 1",
            description="Test description\n\n[timestamps]\n00:00 - song1\n02:30 - song2",
            category="Música",
            tags="test, video, music"
        )
        print("✅ VideoMetadataWidget created successfully")
        
        # Test metadata extraction
        metadata = widget.get_metadata()
        expected_keys = ['title', 'description', 'category_id', 'tags']
        for key in expected_keys:
            if key in metadata:
                print(f"✅ Metadata contains key: {key}")
            else:
                print(f"❌ Metadata missing key: {key}")
                return False
        
        # Verify values
        if metadata['title'] == "Test Video 1":
            print("✅ Title metadata correct")
        else:
            print(f"❌ Title metadata incorrect: {metadata['title']}")
            return False
        
        if metadata['category_id'] == "10":  # Música = 10
            print("✅ Category mapping correct")
        else:
            print(f"❌ Category mapping incorrect: {metadata['category_id']}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ VideoMetadataWidget test failed: {e}")
        return False

def test_generator_metadata_method():
    """Test MultipleVideosGenerator metadata handling"""
    print("\n=== Testing MultipleVideosGenerator Metadata Handling ===")
    
    try:
        from multiple_videos_generator import MultipleVideosGenerator
        
        # Test with no individual metadata
        generator = MultipleVideosGenerator()
        print("✅ Generator created without individual metadata")
        
        # Test global metadata fallback
        metadata = generator._get_video_metadata(1)
        if metadata['title'] == 'Video 1':
            print("✅ Global metadata fallback works")
        else:
            print(f"❌ Global metadata fallback failed: {metadata['title']}")
            return False
        
        # Test with individual metadata
        individual_metadata = [
            {
                'title': 'Custom Video 1',
                'description': 'Custom description for video 1',
                'tags': 'custom, video1',
                'category_id': '24'
            },
            {
                'title': 'Custom Video 2', 
                'description': 'Custom description for video 2',
                'tags': 'custom, video2',
                'category_id': '20'
            }
        ]
        
        generator2 = MultipleVideosGenerator(
            youtube_config={
                'title_base': 'Test Video {}',
                'description': 'Test description',
                'tags': 'test, tags',
                'category_id': '10'
            },
            individual_metadata=individual_metadata
        )
        print("✅ Generator created with individual metadata")
        
        # Test individual metadata usage
        metadata1 = generator2._get_video_metadata(1)
        if metadata1['title'] == 'Custom Video 1':
            print("✅ Individual metadata for video 1 works")
        else:
            print(f"❌ Individual metadata failed: {metadata1['title']}")
            return False
        
        metadata2 = generator2._get_video_metadata(2)
        if metadata2['title'] == 'Custom Video 2':
            print("✅ Individual metadata for video 2 works")
        else:
            print(f"❌ Individual metadata failed: {metadata2['title']}")
            return False
        
        # Test fallback when individual metadata is incomplete
        metadata3 = generator2._get_video_metadata(3)  # No metadata for video 3
        if metadata3['title'] == 'Test Video 3':
            print("✅ Fallback to global metadata for video 3 works")
        else:
            print(f"❌ Fallback failed: {metadata3['title']}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Generator metadata test failed: {e}")
        return False

def create_test_description_files():
    """Create test description files for testing"""
    print("\n=== Creating Test Description Files ===")
    
    try:
        from config import OUTPUT_DIR
        
        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Create test description files
        for i in range(1, 4):
            desc_content = f"""=== DESCRIPCIÓN DEL VIDEO MUSICAL ===

Total de canciones: 3
Repeticiones: 1

=== TIEMPOS DE REPRODUCCIÓN ===

00:00 - cancion{i}_1
02:25 - cancion{i}_2
04:51 - cancion{i}_3

=== DURACIÓN TOTAL ===
Tiempo total: 07:16"""
            
            desc_path = os.path.join(OUTPUT_DIR, f"video_{i}_descripcion.txt")
            with open(desc_path, 'w', encoding='utf-8') as f:
                f.write(desc_content)
            
            print(f"✅ Created test description file: {desc_path}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create test description files: {e}")
        return False

def test_preview_dialog():
    """Test VideoMetadataPreviewDialog functionality"""
    print("\n=== Testing VideoMetadataPreviewDialog ===")
    
    try:
        from PySide6.QtWidgets import QApplication
        from gui_components.video_metadata_preview_dialog import VideoMetadataPreviewDialog
        
        # Create minimal QApplication for testing
        if not QApplication.instance():
            app = QApplication([])
        
        # Test dialog creation
        youtube_config = {
            'title_base': 'Test Video {}',
            'description': 'Base description for all videos',
            'tags': 'test, video, music',
            'category_id': '10'
        }
        
        dialog = VideoMetadataPreviewDialog(
            video_count=3,
            youtube_config=youtube_config
        )
        print("✅ VideoMetadataPreviewDialog created successfully")
        
        # Test that video widgets were created
        if len(dialog.video_widgets) == 3:
            print("✅ Correct number of video widgets created")
        else:
            print(f"❌ Wrong number of video widgets: {len(dialog.video_widgets)}")
            return False
        
        # Test metadata generation
        for i, widget in enumerate(dialog.video_widgets, 1):
            if widget.video_number == i:
                print(f"✅ Video widget {i} has correct video number")
            else:
                print(f"❌ Video widget {i} has wrong video number: {widget.video_number}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Preview dialog test failed: {e}")
        return False

def cleanup_test_files():
    """Clean up test files"""
    print("\n=== Cleaning Up Test Files ===")
    
    try:
        from config import OUTPUT_DIR
        
        for i in range(1, 4):
            desc_path = os.path.join(OUTPUT_DIR, f"video_{i}_descripcion.txt")
            if os.path.exists(desc_path):
                os.remove(desc_path)
                print(f"✅ Removed test file: {desc_path}")
        
        return True
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Video Metadata Preview Functionality")
    print("=" * 50)
    
    test_results = []
    
    # Run all tests
    test_results.append(("Imports", test_imports()))
    test_results.append(("Audio Processor", test_audio_processor_timestamps()))
    test_results.append(("Create Test Files", create_test_description_files()))
    test_results.append(("Metadata Widget", test_metadata_widget()))
    test_results.append(("Generator Metadata", test_generator_metadata_method()))
    test_results.append(("Preview Dialog", test_preview_dialog()))
    test_results.append(("Cleanup", cleanup_test_files()))
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed + failed}, Passed: {passed}, Failed: {failed}")
    
    if failed == 0:
        print("🎉 All tests passed! Preview functionality is working correctly.")
        return True
    else:
        print(f"❌ {failed} test(s) failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)