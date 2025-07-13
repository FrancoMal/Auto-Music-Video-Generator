import os
import logging
import subprocess
import json
import numpy as np
from config import VIDEO_CONFIG, FILES_CONFIG, CHROMA_CONFIG, VISUALIZER_OPTIMIZED_CONFIG, GREENSCREEN_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedVideoGenerator:
    def __init__(self):
        self.width = VIDEO_CONFIG['width']
        self.height = VIDEO_CONFIG['height']
        self.fps = VIDEO_CONFIG['fps']
        self.video_codec = 'h264_nvenc'  # GPU encoding / Codificación GPU
        self.audio_codec = VIDEO_CONFIG['audio_codec']
        self.bitrate = '15M'  # Higher bitrate for better quality / Mayor bitrate para mejor calidad
        self.audio_bitrate = VIDEO_CONFIG['audio_bitrate']
        
        # Optimized visualizer configurations / Configuraciones del visualizador optimizado
        self.viz_width = VISUALIZER_OPTIMIZED_CONFIG['width']
        self.viz_height = VISUALIZER_OPTIMIZED_CONFIG['height']
        self.viz_position_from_bottom = VISUALIZER_OPTIMIZED_CONFIG['position_from_bottom']
        self.viz_color = VISUALIZER_OPTIMIZED_CONFIG['color']
        self.viz_mode = VISUALIZER_OPTIMIZED_CONFIG['mode']
        self.viz_mirror_effect = VISUALIZER_OPTIMIZED_CONFIG['mirror_effect']
        self.viz_opacity = VISUALIZER_OPTIMIZED_CONFIG['opacity']
        self.viz_scale = VISUALIZER_OPTIMIZED_CONFIG['scale']
        
        # Check if GPU is available / Verificar si GPU está disponible
        self.gpu_available = self.check_gpu_support()
        if not self.gpu_available:
            logger.warning("GPU not available, using CPU / GPU no disponible, usando CPU")
            self.video_codec = 'libx264'
            self.bitrate = VIDEO_CONFIG['bitrate']
    
    def check_gpu_support(self):
        """Check if FFmpeg supports GPU acceleration / Verificar si FFmpeg soporta aceleración GPU"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-encoders'], 
                capture_output=True, 
                text=True
            )
            return 'h264_nvenc' in result.stdout
        except:
            return False
    
    def create_audio_waveform_video(self, audio_path, output_path):
        """Crear video con forma de onda usando FFmpeg"""
        try:
            logger.info(f"Creando video con waveform: {output_path}")
            
            cmd = [
                'ffmpeg', '-y',
                '-i', audio_path,
                '-filter_complex', 
                f'[0:a]showwaves=s={self.width}x{self.height}:mode=cline:colors=white:rate={self.fps}[v]',
                '-map', '[v]',
                '-map', '0:a',
                '-c:v', self.video_codec,
                '-c:a', self.audio_codec,
                '-b:v', self.bitrate,
                '-b:a', self.audio_bitrate,
                '-r', str(self.fps),
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            if self.gpu_available:
                cmd.extend(['-gpu', '0'])
            
            logger.info("Ejecutando FFmpeg con aceleración GPU...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Video con waveform creado: {output_path}")
                return True
            else:
                logger.error(f"Error en FFmpeg: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error al crear video con waveform: {e}")
            return False
    
    def create_spectrum_video(self, audio_path, output_path):
        """Crear video con espectro de frecuencias usando FFmpeg"""
        try:
            logger.info(f"Creando video con espectro: {output_path}")
            
            cmd = [
                'ffmpeg', '-y',
                '-i', audio_path,
                '-filter_complex', 
                f'[0:a]showfreqs=s={self.width}x{self.height}:mode=bar:colors=fire:rate={self.fps}[v]',
                '-map', '[v]',
                '-map', '0:a',
                '-c:v', self.video_codec,
                '-c:a', self.audio_codec,
                '-b:v', self.bitrate,
                '-b:a', self.audio_bitrate,
                '-r', str(self.fps),
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            if self.gpu_available:
                cmd.extend(['-gpu', '0'])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Video con espectro creado: {output_path}")
                return True
            else:
                logger.error(f"Error en FFmpeg: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error al crear video con espectro: {e}")
            return False
    
    def create_background_video(self, background_image_path, audio_path, output_path):
        """Crear video de fondo con imagen y audio"""
        try:
            logger.info(f"Creando video de fondo: {output_path}")
            
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', background_image_path,
                '-i', audio_path,
                '-c:v', self.video_codec,
                '-c:a', self.audio_codec,
                '-b:v', self.bitrate,
                '-b:a', self.audio_bitrate,
                '-r', str(self.fps),
                '-shortest',
                '-vf', f'scale={self.width}:{self.height}',
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            if self.gpu_available:
                cmd.extend(['-gpu', '0'])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Video de fondo creado: {output_path}")
                return True
            else:
                logger.error(f"Error en FFmpeg: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error al crear video de fondo: {e}")
            return False
    
    def overlay_videos(self, background_video, overlay_video, output_path, overlay_opacity=0.7):
        """Superponer videos usando FFmpeg"""
        try:
            logger.info(f"Superponiendo videos: {output_path}")
            
            cmd = [
                'ffmpeg', '-y',
                '-i', background_video,
                '-i', overlay_video,
                '-filter_complex', 
                f'[1:v]format=yuva420p,colorchannelmixer=aa={overlay_opacity}[overlay];[0:v][overlay]overlay[v]',
                '-map', '[v]',
                '-map', '0:a',
                '-c:v', self.video_codec,
                '-c:a', 'copy',
                '-shortest',
                output_path
            ]
            
            if self.gpu_available:
                cmd.extend(['-gpu', '0'])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Videos superpuestos: {output_path}")
                return True
            else:
                logger.error(f"Error en FFmpeg: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error al superponer videos: {e}")
            return False
    
    def generate_final_video_optimized(self, audio_path, background_image_path, output_path):
        """Generar video final optimizado usando solo FFmpeg"""
        try:
            logger.info("=== GENERANDO VIDEO FINAL OPTIMIZADO ===")
            
            # Crear directorio de salida
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Archivos temporales
            temp_dir = os.path.dirname(output_path)
            background_video = os.path.join(temp_dir, 'temp_background.mp4')
            spectrum_video = os.path.join(temp_dir, 'temp_spectrum.mp4')
            
            # 1. Crear video de fondo
            logger.info("Paso 1/3: Creando video de fondo...")
            if not self.create_background_video(background_image_path, audio_path, background_video):
                return False
            
            # 2. Crear video con espectro
            logger.info("Paso 2/3: Creando visualización de espectro...")
            if not self.create_spectrum_video(audio_path, spectrum_video):
                return False
            
            # 3. Superponer videos
            logger.info("Paso 3/3: Superponiendo videos...")
            if not self.overlay_videos(background_video, spectrum_video, output_path):
                return False
            
            # Limpiar archivos temporales
            for temp_file in [background_video, spectrum_video]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            logger.info(f"Video final generado exitosamente: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error al generar video final optimizado: {e}")
            return False
    
    def get_available_greenscreen_effects(self):
        """Get list of available greenscreen effects"""
        effects = []
        if not os.path.exists(GREENSCREEN_CONFIG['directory']):
            return effects
        
        for file in os.listdir(GREENSCREEN_CONFIG['directory']):
            file_ext = os.path.splitext(file.lower())[1]
            if file_ext in GREENSCREEN_CONFIG['supported_formats']:
                effect_path = os.path.join(GREENSCREEN_CONFIG['directory'], file)
                effects.append({
                    'name': os.path.splitext(file)[0],
                    'path': effect_path,
                    'type': 'video' if file_ext == '.mp4' else 'image'
                })
        
        return effects
    
    def build_greenscreen_filter(self, greenscreen_effects, base_input_count=2):
        """Build FFmpeg filter for greenscreen effects with priority order"""
        if not greenscreen_effects:
            logger.debug("No greenscreen effects to process")
            return "", []
        
        filter_parts = []
        additional_inputs = []
        input_index = base_input_count
        
        # Sort effects by priority (higher priority = rendered on top)
        sorted_effects = sorted(greenscreen_effects, key=lambda x: x.get('priority', 0))
        logger.info(f"Processing {len(sorted_effects)} greenscreen effects")
        
        for i, effect in enumerate(sorted_effects):
            effect_path = effect['path']
            effect_type = effect['type']
            effect_name = effect.get('name', f'effect_{i}')
            
            # Verify effect file exists
            if not os.path.exists(effect_path):
                logger.warning(f"Effect file not found: {effect_path}")
                continue
                
            additional_inputs.append(effect_path)
            logger.info(f"Adding effect {i+1}: {effect_name} ({effect_type}) - Input index {input_index}")
            
            if effect_type == 'video':
                # For MP4 videos with greenscreen - apply colorkey and scale
                filter_parts.append(
                    f'[{input_index}:v]colorkey=green:'
                    f'{GREENSCREEN_CONFIG["similarity"]}:'
                    f'{GREENSCREEN_CONFIG["tolerance"]},'
                    f'scale={self.width}:{self.height}[effect_{i}]'
                )
                logger.debug(f"Video effect filter: colorkey=green:{GREENSCREEN_CONFIG['similarity']}:{GREENSCREEN_CONFIG['tolerance']}")
            else:
                # For PNG images - just scale (transparency is preserved)
                filter_parts.append(
                    f'[{input_index}:v]scale={self.width}:{self.height}[effect_{i}]'
                )
                logger.debug(f"Image effect filter: scale={self.width}:{self.height}")
            
            input_index += 1
        
        filter_string = ';'.join(filter_parts)
        logger.debug(f"Complete greenscreen filter: {filter_string}")
        return filter_string, additional_inputs
    
    def build_overlay_chain(self, base_label, greenscreen_effects):
        """Build overlay chain for greenscreen effects"""
        if not greenscreen_effects:
            return base_label
        
        # Sort effects by priority
        sorted_effects = sorted(greenscreen_effects, key=lambda x: x.get('priority', 0))
        
        current_label = base_label
        for i, effect in enumerate(sorted_effects):
            next_label = f'overlay_{i}' if i < len(sorted_effects) - 1 else 'final'
            overlay_filter = f'[{current_label}][effect_{i}]overlay[{next_label}]'
            current_label = next_label
        
        return current_label, [f'[{current_label}][effect_{i}]overlay[{"overlay_" + str(i) if i < len(sorted_effects) - 1 else "final"}]' for i, effect in enumerate(sorted_effects)]
    
    def create_simple_music_video(self, audio_path, background_image_path, output_path, greenscreen_effects=None):
        """Create simple and fast music video / Crear video musical simple y rápido"""
        try:
            logger.info("=== CREATING SIMPLE MUSIC VIDEO / CREANDO VIDEO MUSICAL SIMPLE ===")
            
            # Initialize greenscreen effects
            if greenscreen_effects is None:
                greenscreen_effects = []
            
            logger.info(f"Greenscreen effects provided: {len(greenscreen_effects)}")
            for i, effect in enumerate(greenscreen_effects):
                logger.info(f"  Effect {i+1}: {effect.get('name', 'unnamed')} ({effect.get('type', 'unknown')})")
            
            # Update visualizer color from current configuration
            self.viz_color = VISUALIZER_OPTIMIZED_CONFIG['color']
            logger.info(f"Visualizer color: {self.viz_color}")
            
            # Build FFmpeg command inputs
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1', '-i', background_image_path,  # Input 0: background
                '-i', audio_path                            # Input 1: audio
            ]
            
            input_count = 2  # We have background + audio
            
            # Add greenscreen effect inputs and build their filters
            greenscreen_filter = ""
            if greenscreen_effects:
                logger.info("Building greenscreen effects...")
                greenscreen_filter_parts = []
                
                # Sort effects by priority (lower number = applied first, higher number = on top)
                sorted_effects = sorted(greenscreen_effects, key=lambda x: x.get('priority', 0))
                
                for i, effect in enumerate(sorted_effects):
                    effect_path = effect['path']
                    effect_type = effect['type']
                    effect_name = effect.get('name', f'effect_{i}')
                    
                    if not os.path.exists(effect_path):
                        logger.warning(f"Effect file not found: {effect_path}")
                        continue
                    
                    # Add input to command
                    if effect_type == 'video':
                        cmd.extend(['-stream_loop', '-1', '-i', effect_path])
                        # For MP4 videos with greenscreen - use custom parameters if available
                        similarity = effect.get('custom_similarity', GREENSCREEN_CONFIG["similarity"])
                        tolerance = effect.get('custom_tolerance', GREENSCREEN_CONFIG["tolerance"])
                        
                        greenscreen_filter_parts.append(
                            f'[{input_count}:v]colorkey=green:'
                            f'{similarity}:'
                            f'{tolerance},'
                            f'scale={self.width}:{self.height}[effect_{i}]'
                        )
                        
                        if 'custom_similarity' in effect or 'custom_tolerance' in effect:
                            logger.info(f"Added video effect: {effect_name} with custom chroma (sim:{similarity:.2f}, tol:{tolerance:.2f}) as input {input_count}")
                        else:
                            logger.info(f"Added video effect: {effect_name} with default chroma as input {input_count}")
                    else:
                        cmd.extend(['-loop', '1', '-i', effect_path])
                        # For PNG images (preserve transparency)
                        greenscreen_filter_parts.append(
                            f'[{input_count}:v]scale={self.width}:{self.height}[effect_{i}]'
                        )
                        logger.info(f"Added image effect: {effect_name} as input {input_count}")
                    
                    input_count += 1
                
                greenscreen_filter = ';'.join(greenscreen_filter_parts)
                logger.debug(f"Greenscreen filter: {greenscreen_filter}")
            
            # Build base video with visualizer
            logger.info("Building base video with visualizer...")
            if self.viz_mirror_effect:
                # With horizontal mirror effect
                base_filter = (
                    f'[0:v]scale={self.width}:{self.height}[bg];'
                    f'[1:a]showwaves=s={self.viz_width//2}x{self.viz_height}:mode={self.viz_mode}:colors={self.viz_color}:rate={self.fps}[wave_half];'
                    f'[wave_half]split[wave_orig][wave_copy];'
                    f'[wave_copy]hflip[wave_mirror];'
                    f'[wave_orig][wave_mirror]hstack[wave_symmetric];'
                    f'[bg][wave_symmetric]overlay=x=0:y=H-h-{self.viz_position_from_bottom}[base_with_viz]'
                )
            else:
                # Without mirror effect
                base_filter = (
                    f'[0:v]scale={self.width}:{self.height}[bg];'
                    f'[1:a]showwaves=s={self.viz_width}x{self.viz_height}:mode={self.viz_mode}:colors={self.viz_color}:rate={self.fps}[wave];'
                    f'[bg][wave]overlay=x=0:y=H-h-{self.viz_position_from_bottom}[base_with_viz]'
                )
            
            # Combine everything
            if greenscreen_effects and greenscreen_filter:
                logger.info("Combining base video with greenscreen effects...")
                
                # Build overlay chain: base -> effect1 -> effect2 -> ... -> final
                current_input = 'base_with_viz'
                overlay_chain = []
                
                sorted_effects = sorted(greenscreen_effects, key=lambda x: x.get('priority', 0))
                valid_effects = [i for i, effect in enumerate(sorted_effects) if os.path.exists(effect['path'])]
                
                for idx, effect_idx in enumerate(valid_effects):
                    if idx == len(valid_effects) - 1:
                        # Last effect outputs to final 'v'
                        overlay_chain.append(f'[{current_input}][effect_{effect_idx}]overlay[v]')
                    else:
                        # Intermediate effects
                        next_label = f'overlay_{idx}'
                        overlay_chain.append(f'[{current_input}][effect_{effect_idx}]overlay[{next_label}]')
                        current_input = next_label
                
                # Complete filter chain
                if overlay_chain:
                    filter_complex = base_filter + ';' + greenscreen_filter + ';' + ';'.join(overlay_chain)
                    logger.info(f"Applied {len(overlay_chain)} overlay operations")
                else:
                    filter_complex = base_filter.replace('[base_with_viz]', '[v]')
                    logger.warning("No valid effects found, using base filter only")
            else:
                # No greenscreen effects
                filter_complex = base_filter.replace('[base_with_viz]', '[v]')
                logger.info("No greenscreen effects, using base filter only")
            
            # Complete FFmpeg command
            cmd.extend([
                '-filter_complex', filter_complex,
                '-map', '[v]',
                '-map', '1:a',
                '-c:v', self.video_codec,
                '-c:a', self.audio_codec,
                '-b:v', self.bitrate,
                '-b:a', self.audio_bitrate,
                '-r', str(self.fps),
                '-shortest',
                '-pix_fmt', 'yuv420p',
                output_path
            ])
            
            if self.gpu_available:
                cmd.extend(['-gpu', '0'])
            
            # Log complete command for debugging
            logger.info("Executing FFmpeg command...")
            logger.debug(f"Complete filter: {filter_complex}")
            cmd_str = ' '.join([f'"{arg}"' if ' ' in str(arg) else str(arg) for arg in cmd])
            logger.debug(f"Command: {cmd_str}")
            
            # Execute FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Music video created successfully: {output_path}")
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path) / (1024 * 1024)
                    logger.info(f"Output file size: {file_size:.1f} MB")
                return True
            else:
                logger.error(f"❌ FFmpeg failed with return code {result.returncode}")
                logger.error(f"FFmpeg stderr: {result.stderr}")
                if result.stdout:
                    logger.debug(f"FFmpeg stdout: {result.stdout}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Exception in create_simple_music_video: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

if __name__ == "__main__":
    generator = OptimizedVideoGenerator()
    
    # Configuración de prueba
    audio_path = FILES_CONFIG['combined_audio']
    background_path = FILES_CONFIG['background_image']
    output_path = FILES_CONFIG['final_video']
    
    # Generar video final optimizado
    success = generator.create_simple_music_video(
        audio_path, background_path, output_path
    )
    
    if success:
        print(f"Video final generado: {output_path}")
    else:
        print("Error al generar video final")