# 🎬 Guía de Efectos Greenscreen

## ✅ Sistema Completamente Funcional

Los efectos greenscreen están **funcionando correctamente** tanto para imágenes PNG como para videos MP4.

## 📁 Estructura de Archivos

```
greenscreen effects/    # Carpeta para tus efectos
├── effect1.png        # Imágenes PNG (con transparencia)
├── effect2.mp4        # Videos MP4 (con fondo verde)
└── effect3.png        # Más efectos...
```

## 🎯 Tipos de Efectos Soportados

### 📸 **PNG (Transparentes)**
- ✅ Funciona inmediatamente
- ✅ Respeta transparencias nativas
- ✅ Ideal para overlays simples

### 🎥 **MP4 (Con Greenscreen)**
- ✅ Funciona con ajuste de parámetros
- ⚙️ Requiere calibración de chroma
- 🎨 Fondo verde estándar (RGB 0,255,0)

## 🔧 Cómo Usar en la GUI

1. **Abrir GUI**: `python multiple_videos_gui.py`
2. **Configurar video**: Selecciona canciones, color, fondo
3. **Añadir efectos**: Click en **"Green Effects"**
4. **Seleccionar efectos**: Arrastra de disponibles a seleccionados
5. **Ordenar prioridades**: Usa las flechas o drag-and-drop
6. **Para MP4**: Click **"Preview Chroma"** para ajustar
7. **Generar**: Los efectos aparecerán automáticamente

## 🎨 Ajuste de Chroma para MP4

### Para videos MP4 con fondo verde:

1. **Click "Preview Chroma"** en el efecto MP4
2. **Ajusta parámetros**:
   - **Similarity**: Qué tan similar al verde detectar
   - **Tolerance**: Qué tan suave el borde
3. **Presets disponibles**:
   - **Strict**: similarity=0.2, tolerance=0.05
   - **Normal**: similarity=0.3, tolerance=0.1
   - **Loose**: similarity=0.4, tolerance=0.2
4. **Preview en tiempo real**: Ve los cambios inmediatamente
5. **Apply Settings**: Guarda los parámetros personalizados

## 🎯 Orden de Capas (Prioridades)

```
Video Final
    ↑
Efecto N (prioridad más alta)
    ↑
Efecto 2 (prioridad media)
    ↑
Efecto 1 (prioridad baja)
    ↑
Visualizador de audio (ondas)
    ↑
Imagen de fondo
```

## 🧪 Videos de Prueba Generados

Se han creado videos de ejemplo con diferentes parámetros:
- `test_chroma_strict.mp4` - Parámetros estrictos
- `test_chroma_normal.mp4` - Parámetros normales  
- `test_chroma_loose.mp4` - Parámetros permisivos

**Compara estos videos** para ver cómo afectan los parámetros de chroma.

## 💡 Consejos para Mejores Resultados

### Para MP4 con Greenscreen:
- 🎨 **Fondo verde uniforme** (sin sombras)
- 💡 **Iluminación pareja** en el fondo verde
- 📹 **Alta calidad** de video fuente
- ⚙️ **Ajusta parámetros** según tu video específico

### Para PNG Transparentes:
- ✅ **Funcionan automáticamente**
- 🎨 **Usa transparencias reales** (canal alfa)
- 📏 **Resolución 1920x1080** recomendada

## 🚀 Rendimiento

- **GPU Accelerated**: Usa NVENC si está disponible
- **Tiempo estimado**: 1-3 minutos por video (con GPU)
- **Múltiples efectos**: Sin impacto significativo en rendimiento

## ❓ Solución de Problemas

### "No veo mi efecto MP4"
1. ✅ Verifica que el fondo sea verde puro
2. 🔧 Usa "Preview Chroma" para ajustar parámetros
3. 📊 Prueba diferentes presets (Strict → Loose)

### "El efecto se ve mal en los bordes"
1. 🎯 Reduce la **tolerance** (bordes más limpios)
2. 🎨 Ajusta la **similarity** (mejor detección)

### "El verde no se quita completamente"
1. 📈 Aumenta la **similarity** (más permisivo)
2. 🔍 Verifica que el verde sea RGB(0,255,0)

## 🎉 ¡Todo Listo!

El sistema de efectos greenscreen está **completamente funcional**. Los efectos aparecerán superpuestos sobre tus videos musicales con las prioridades que configures.

**¡Disfruta creando videos con efectos increíbles!** 🌟