# ✨ Greenscreen Effects System

Complete guide for using the advanced greenscreen effects system in the Music Video Generator.

## 🎯 Overview

The greenscreen effects system allows you to add professional-quality overlays to your music videos, supporting both MP4 videos with green backgrounds and PNG images with transparency.

## 📁 Setup

### 1. Create Effects Directory

The system automatically creates the `greenscreen effects/` directory, or you can create it manually:

```bash
mkdir "greenscreen effects"
```

### 2. Add Your Effects

```bash
# Copy MP4 videos with green background
cp your_effects/*.mp4 "greenscreen effects/"

# Copy PNG images with transparency
cp your_overlays/*.png "greenscreen effects/"
```

## 🎬 Supported Formats

### MP4 Videos (with Greenscreen)
- **Background**: Must be pure green (RGB 0,255,0)
- **Resolution**: Any (automatically scaled to 1920x1080)
- **Playback**: Loops continuously during video
- **Chroma Keying**: Adjustable parameters for clean green removal

### PNG Images (with Transparency)
- **Transparency**: Full alpha channel support
- **Resolution**: Any (automatically scaled to 1920x1080)
- **Display**: Shown continuously during video
- **Overlay**: Direct overlay without chroma processing

## 🚀 Usage

### Basic Usage (Single Video)

1. **Add Effects**: Place files in `greenscreen effects/` directory
2. **Run Generator**: Effects are automatically applied
   ```bash
   python main_optimized.py
   ```

### Advanced Usage (GUI)

1. **Launch GUI**:
   ```bash
   python multiple_videos_gui.py
   ```

2. **Configure Video**: Set songs, color, background

3. **Add Effects**:
   - Click **"Green Effects"** button
   - Drag effects from Available to Selected
   - Order by priority (drag-and-drop or arrows)

4. **Adjust Chroma** (for MP4 videos):
   - Click **"Preview Chroma"** on MP4 effects
   - Use presets: Strict, Normal, Loose, **Optimal**
   - Fine-tune with sliders
   - Preview in real-time

5. **Visual Feedback**:
   - Button changes to **"✅ Effects ON"**
   - Title becomes **"🎬 Video X (con efectos)"**
   - Configuration summary shows **"🎬 N efectos (names)"**

6. **Generate**: Click "Generar Videos"

## ⚙️ Priority System

Effects are layered from bottom to top based on priority:

```
Final Video Output
       ↑
Effect 3 (Priority 3 - Top Layer)
       ↑  
Effect 2 (Priority 2 - Middle)
       ↑
Effect 1 (Priority 1 - Bottom)
       ↑
Audio Visualizer (Waves)
       ↑
Background Image
```

- **Lower numbers**: Rendered first (bottom layers)
- **Higher numbers**: Rendered last (top layers)
- **Reorder**: Drag-and-drop in GUI or use arrow buttons

## 🎨 Chroma Key Parameters

For MP4 videos with green backgrounds:

### Parameters

- **Similarity** (0.1 - 0.6): How similar colors to green are removed
  - Lower values: Only pure green removed
  - Higher values: More green variations removed

- **Tolerance** (0.01 - 0.3): Edge smoothness and blending
  - Lower values: Sharp edges
  - Higher values: Softer, smoother edges

### Presets

| Preset | Similarity | Tolerance | Best For |
|--------|------------|-----------|----------|
| **Strict** | 0.2 | 0.05 | High-quality studio lighting |
| **Normal** | 0.3 | 0.1 | Standard green screens |
| **Loose** | 0.4 | 0.2 | Uneven lighting |
| **Optimal** | 0.5 | 0.25 | Most MP4 videos (recommended) |

### Tips for Best Results

- **Uniform lighting**: Even green background without shadows
- **Pure green**: RGB(0, 255, 0) works best
- **High quality**: Better source videos produce cleaner results
- **Test presets**: Start with "Optimal", adjust if needed

## 🔧 Troubleshooting

### Problem: Green background not removed
**Solution**: 
- Try "Loose" or "Optimal" preset
- Increase Similarity value
- Check if green is pure RGB(0,255,0)

### Problem: Effect has green halo/edges
**Solution**:
- Decrease Tolerance value
- Try "Strict" preset
- Improve source video lighting

### Problem: Effect not visible
**Solution**:
- Check effect is in Selected list
- Verify file format is supported
- Check priority order (higher = more visible)

### Problem: Preview works but final video doesn't
**Solution**:
- Ensure GUI shows "✅ Effects ON"
- Check configuration summary shows effects
- Verify logs show "Applied N overlay operations"

## 📝 Example Workflow

### Complete Greenscreen Video Creation

1. **Prepare Effects**:
   ```bash
   # Copy your greenscreen video
   cp falling_particles.mp4 "greenscreen effects/"
   
   # Copy PNG logo
   cp logo.png "greenscreen effects/"
   ```

2. **Launch GUI**:
   ```bash
   python multiple_videos_gui.py
   ```

3. **Configure**:
   - Set up your video (songs, color, background)
   - Click "Green Effects"
   - Add both effects
   - Set logo as Priority 2 (top)
   - Set particles as Priority 1 (bottom)

4. **Adjust Chroma**:
   - Click "Preview Chroma" on particles MP4
   - Try "Optimal" preset
   - Fine-tune if needed

5. **Generate**:
   - Confirm configuration shows effects
   - Generate video with effects applied

## 🎯 Best Practices

- **Start simple**: Use one effect first, then add more
- **Test parameters**: Use Preview Chroma for MP4 videos
- **Organize files**: Use descriptive names for effects
- **Check quality**: Higher quality source = better results
- **Use presets**: "Optimal" works for most cases
- **Visual feedback**: Always check for "✅ Effects ON" indicator

## 📊 Performance Notes

- **GPU Accelerated**: Effects processing uses hardware acceleration
- **Minimal Impact**: Multiple effects have negligible performance cost
- **Memory Usage**: ~1-2GB additional RAM per video effect
- **Processing Time**: Adds ~10-30 seconds per effect

---

🎉 **Your music videos are now ready for professional greenscreen effects!**