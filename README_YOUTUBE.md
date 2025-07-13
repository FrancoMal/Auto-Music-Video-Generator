# YouTube Upload Integration

This guide explains how to use the YouTube upload functionality integrated into the ACE Music Video Generator.

## Overview

The YouTube integration allows you to automatically upload generated videos to your YouTube channel with two modes:
- **Immediate Upload**: Videos are uploaded immediately after generation as public videos
- **Scheduled Upload**: Videos are uploaded immediately as private videos but scheduled to publish at specific times using YouTube's scheduling system

## Prerequisites

### 1. YouTube API Credentials

You need to set up YouTube Data API v3 credentials:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the YouTube Data API v3
4. Create credentials (OAuth 2.0 Client ID)
5. Download the credentials as `client_secret.json`
6. Place `client_secret.json` in the project root directory

### 2. Required Dependencies

Install the additional dependencies for YouTube functionality:

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pytz
```

### 3. Quota Limitations

**Important**: Unverified YouTube API applications have a daily quota limit of 6 video uploads per day. After uploading 6 videos, the system will automatically enter a 24.5-hour cooldown period before allowing more uploads.

## Usage

### Access YouTube Upload

1. Run the multiple videos GUI: `python multiple_videos_gui.py`
2. Configure your videos as usual
3. Click **"Generar y Subir a YouTube"** instead of "Generar Videos"

### Authentication

1. The YouTube Configuration dialog will open
2. Click **"Iniciar Sesión en YouTube"**
3. Your browser will open for Google OAuth authentication
4. Grant the required permissions
5. Return to the application - you should see "Autenticado como: [Your Channel Name]"

### Configuration Options

#### Video Metadata
- **Título base**: Template for video titles (use `{}` for automatic numbering)
  - Example: `Mi Serie Musical #{}` → `Mi Serie Musical #1`, `Mi Serie Musical #2`, etc.
- **Descripción**: Description applied to all videos
- **Tags**: Comma-separated tags for videos
- **Categoría**: YouTube category (Music, Entertainment, Gaming, Education)
- **Privacidad**: Privacy setting (public, unlisted, private)

#### Upload Modes

##### Immediate Mode (Default)
- Videos are uploaded immediately after generation
- Published as public videos (or your selected privacy setting)
- No scheduling involved

##### Scheduled Mode
- Videos are uploaded immediately as **private** videos
- YouTube's `publish_at` parameter schedules them to go public automatically
- Configure:
  - **Videos por día**: How many videos to schedule per day (1-6)
  - **Horarios**: Specific times for each daily upload
  - **Fecha de inicio/fin**: Date range for scheduling
  - **Vista Previa**: See the complete schedule before confirming

### Workflow

1. **Video Generation**: Videos are generated normally using the optimized pipeline
2. **Upload Process**: Each video is uploaded immediately after generation
3. **Local Cleanup**: Video files are deleted locally after successful upload
4. **Detailed Logging**: All upload activities are logged comprehensively

### File Management

After successful upload:
- ✅ **Kept**: Video descriptions (`video_N_descripcion.txt`)
- ✅ **Kept**: Upload logs (`youtube_uploads.log`, `youtube_uploads_detailed.json`)
- ❌ **Deleted**: Local video files (`video_N.mp4`) to save disk space

## Logging and Monitoring

### Log Files

All upload activities are logged in the `output/` directory:

#### `youtube_uploads.log` (Human-readable)
```
2025-07-13 15:30:45 - Video 1: "Mi Serie Musical #1" uploaded successfully
YouTube ID: dQw4w9WgXcQ
Scheduled for: 2025-07-14T13:00:00.000Z
Local file: /path/to/video_1.mp4 (deleted after upload)
```

#### `youtube_uploads_detailed.json` (Machine-readable)
```json
[
  {
    "timestamp": "2025-07-13T15:30:45.123Z",
    "video_number": 1,
    "title": "Mi Serie Musical #1",
    "youtube_id": "dQw4w9WgXcQ",
    "local_file": "/path/to/video_1.mp4",
    "upload_mode": "scheduled",
    "scheduled_publish_at": "2025-07-14T13:00:00.000Z",
    "file_deleted": true
  }
]
```

### Progress Tracking

The progress dialog shows:
- Current video being processed
- Upload progress and status
- Real-time logs
- Time estimates
- Quota status warnings

## Quota Management

### Daily Limits
- **Unverified API**: 6 videos per day
- **Verified API**: Higher limits (requires Google verification process)

### Automatic Handling
- System tracks daily upload count
- Automatically prevents uploads when quota is exceeded
- Shows 24.5-hour cooldown timer
- Resumes automatically after cooldown period

### Manual Quota Check
The quota status is always visible in the upload dialog and logs.

## Error Handling

### Common Issues

#### Authentication Errors
- **Symptom**: "No se pudo autenticar con YouTube"
- **Solution**: Ensure `client_secret.json` is correct and placed in project root

#### Quota Exceeded
- **Symptom**: "Quota exceeded. Cooldown remaining: XX:XX:XX"
- **Solution**: Wait for the cooldown period to complete (24.5 hours)

#### Upload Failures
- **Symptom**: Individual video upload fails
- **Solution**: Check logs for specific error details, verify file integrity

### Mock Mode Testing

For testing without consuming API quota:

```python
from youtube_uploader import YouTubeUploader
uploader = YouTubeUploader(mock_mode=True)
```

Mock mode simulates all operations without actual YouTube API calls.

## Security Notes

### Sensitive Files (Never commit to git)
- `client_secret.json` - OAuth credentials
- `token.pickle` - Authentication tokens
- `youtube_uploads.log` - May contain sensitive information
- `youtube_uploads_detailed.json` - May contain file paths

These files are automatically excluded by `.gitignore`.

### Authentication Tokens
- Tokens are stored locally in `token.pickle`
- Delete this file to force re-authentication
- Tokens expire automatically and will require re-authentication

## Testing

Run the test suite to verify functionality:

```bash
# Test YouTube upload workflow
python test_upload_workflow.py

# Test scheduling functionality
python test_scheduling.py
```

Tests run in mock mode and don't consume API quota.

## Troubleshooting

### Permission Errors
If you get permission errors, ensure your Google Cloud project has the YouTube Data API v3 enabled and your OAuth credentials have the required scopes.

### Network Issues
The system handles network interruptions gracefully with retry logic for uploads.

### Large File Uploads
Videos are uploaded using resumable uploads to handle large files and network interruptions.

## Advanced Configuration

### Custom Timezone
The default timezone is `America/Argentina/Buenos_Aires`. To change it, modify the `convert_to_utc_rfc3339()` function in `gui_components/youtube_config_dialog.py`.

### Custom Upload Settings
Advanced users can modify upload parameters in `youtube_uploader.py`:
- Chunk size for resumable uploads
- Retry logic
- Timeout settings

---

For technical support or issues, refer to the main project documentation or create an issue in the repository.