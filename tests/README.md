# Test Suite Organization

This directory contains all tests for the ACE Music Video Generator project, organized by functionality.

## Directory Structure

### `/timestamps/`
Tests related to timestamp generation and description functionality:
- `test_preview_functionality.py` - Comprehensive tests for video metadata preview functionality

### `/repetitions/`
Tests related to repetitions functionality:
- Currently empty - repetitions tests were integrated into main development workflow

### `/youtube/`
Tests related to YouTube upload and scheduling functionality:
- `test_youtube_integration.py` - YouTube API integration tests with mock mode
- `test_scheduling.py` - YouTube scheduling functionality tests
- `test_upload_workflow.py` - Complete upload workflow tests

### `/gui/`
Tests related to GUI components and user interface:
- `test_gui_greenscreen.py` - GUI greenscreen effects integration tests
- `test_gui_quick.py` - Quick GUI functionality tests

### `/integration/`
Integration tests and end-to-end functionality tests:
- `test_complete_fix.py` - Complete multiple videos workflow tests
- `test_corrections.py` - System corrections and fixes tests
- `test_multiple_videos.py` - Multiple videos system tests
- `test_quick_video.py` - Quick single video generation tests
- `test_chroma_combinations.py` - Chroma key parameter combination tests
- `test_final_greenscreen.py` - Final greenscreen functionality tests
- `test_fixed_greenscreen.py` - Fixed greenscreen implementation tests
- `test_greenscreen_effects.py` - Greenscreen effects system tests
- `test_mp4_chroma.py` - MP4 chroma key parameter tests

## Running Tests

Each test can be run individually:
```bash
python tests/timestamps/test_preview_functionality.py
python tests/youtube/test_youtube_integration.py
python tests/integration/test_complete_fix.py
```

Most tests include comprehensive logging and detailed status reports to help with debugging and validation.

## Test Categories

- **Unit Tests**: Individual component functionality
- **Integration Tests**: Component interaction and workflow tests  
- **GUI Tests**: User interface and interaction tests
- **API Tests**: External service integration (YouTube API)
- **End-to-End Tests**: Complete workflow validation

## Notes

- Tests use mock data and fake files when appropriate to avoid dependencies on real audio/video files
- YouTube tests include mock mode to avoid actual API calls during development
- All tests include cleanup procedures to maintain system cleanliness