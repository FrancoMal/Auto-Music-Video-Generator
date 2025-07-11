# Guía de Configuración del Visualizador Optimizado

## 📍 Ubicación
Las configuraciones se encuentran en `config.py` en la sección `VISUALIZER_OPTIMIZED_CONFIG`.

## 🎛️ Opciones Disponibles

### Dimensiones
```python
"width": 1920,     # Ancho del visualizador en pixels
"height": 200,     # Alto del visualizador en pixels
```

### Posición
```python
"position_from_bottom": 300,  # Distancia desde la parte inferior del video
```

### Colores Disponibles
```python
"color": "red",    # Color del visualizador
```

**Colores soportados:**
- `"red"` - Rojo
- `"cyan"` - Cian
- `"white"` - Blanco
- `"yellow"` - Amarillo
- `"green"` - Verde
- `"blue"` - Azul
- `"magenta"` - Magenta
- `"orange"` - Naranja
- `"pink"` - Rosa

### Modos de Visualización
```python
"mode": "cline",   # Estilo de la visualización
```

**Modos disponibles:**
- `"cline"` - Línea continua (recomendado)
- `"line"` - Línea simple
- `"point"` - Puntos

### Efectos
```python
"mirror_effect": True,  # Efecto espejo horizontal
"opacity": 1.0,        # Opacidad (0.0 a 1.0)
"scale": 1.0           # Escala del visualizador
```

## 🎨 Ejemplos de Configuración

### Visualizador Rojo Centrado
```python
VISUALIZER_OPTIMIZED_CONFIG = {
    "width": 1920,
    "height": 200,
    "position_from_bottom": 300,
    "color": "red",
    "mode": "cline",
    "mirror_effect": True,
    "opacity": 1.0,
    "scale": 1.0
}
```

### Visualizador Azul Más Pequeño
```python
VISUALIZER_OPTIMIZED_CONFIG = {
    "width": 1920,
    "height": 150,
    "position_from_bottom": 250,
    "color": "blue",
    "mode": "cline",
    "mirror_effect": True,
    "opacity": 0.8,
    "scale": 0.8
}
```

### Visualizador Verde Sin Espejo
```python
VISUALIZER_OPTIMIZED_CONFIG = {
    "width": 1920,
    "height": 180,
    "position_from_bottom": 400,
    "color": "green",
    "mode": "line",
    "mirror_effect": False,
    "opacity": 1.0,
    "scale": 1.0
}
```

## 🔧 Cómo Aplicar Cambios

1. **Editar** `config.py`
2. **Cambiar** los valores en `VISUALIZER_OPTIMIZED_CONFIG`
3. **Ejecutar** `python main_optimized.py`
4. **Verificar** el resultado en `output/video_final.mp4`

## 📋 Configuración Actual
```python
VISUALIZER_OPTIMIZED_CONFIG = {
    "width": 1920,
    "height": 200,
    "position_from_bottom": 300,
    "color": "red",
    "mode": "cline",
    "mirror_effect": True,
    "opacity": 1.0,
    "scale": 1.0
}
```

¡Ahora puedes personalizar fácilmente el visualizador cambiando solo los valores en `config.py`!