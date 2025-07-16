# WebRTC Camera Stream - Raspberry Pi Edition 🍓📹

Versión mejorada con soporte modular para múltiples tipos de cámaras, optimizada para Raspberry Pi con PiCamera2.

## ✨ Nuevas Características

- 🔄 **Soporte modular**: Detecta automáticamente el mejor tipo de cámara
- 🍓 **PiCamera2**: Soporte nativo para Raspberry Pi Camera Module
- 🖥️ **OpenCV**: Compatibilidad con webcams estándar
- ⚙️ **Argumentos CLI**: Control total desde línea de comandos
- 📊 **Información del sistema**: Endpoint para diagnosticar cámaras
- 🎯 **Auto-detección**: Selección automática de la cámara óptima

## 🎯 Compatibilidad

| Plataforma | Cámara Recomendada | Estado |
|------------|-------------------|---------|
| **Raspberry Pi** | PiCamera2 | ✅ Optimizado |
| **Linux/macOS/Windows** | OpenCV (WebCam) | ✅ Compatible |
| **Raspberry Pi + USB** | OpenCV | ✅ Fallback |

## 🚀 Instalación

### Para Computadora (Windows/macOS/Linux)
```bash
# Clonar la rama
git clone -b feature/raspberry https://github.com/Mozta/WebRTC-Camera-Stream.git
cd WebRTC-Camera-Stream

# Instalar dependencias
pip install -r requirements.txt
```

### Para Raspberry Pi
```bash
# Clonar la rama
git clone -b feature/raspberry https://github.com/Mozta/WebRTC-Camera-Stream.git
cd WebRTC-Camera-Stream

# Setup automático para Raspberry Pi
python setup_raspberry.py

# O instalación manual
pip install -r requirements-raspberry.txt
pip install picamera2 --break-system-packages
```

## 📋 Uso

### Comandos Básicos

```bash
# Auto-detectar y usar la mejor cámara
python app.py

# Información del sistema y cámaras
python app.py --info

# Forzar uso de PiCamera2 (Raspberry Pi)
python app.py --camera-type picamera2

# Forzar uso de OpenCV (WebCam)
python app.py --camera-type opencv --camera-id 0

# Configurar resolución y FPS
python app.py --width 1280 --height 720 --fps 30

# Servidor público (accesible desde red)
python app.py --host 0.0.0.0 --port 8080
```

### Ejemplos Específicos

```bash
# Raspberry Pi con máxima calidad
python app.py --camera-type picamera2 --width 1920 --height 1080 --fps 30

# Computadora con webcam específica
python app.py --camera-type opencv --camera-id 1 --width 640 --height 480

# Modo de baja latencia
python app.py --fps 60 --width 480 --height 360
```

## 🏗️ Arquitectura Modular

```
📁 camera_module.py          # Sistema modular de cámaras
├── 🎯 CameraDetector        # Auto-detección de plataforma
├── 🏭 CameraFactory         # Factory para crear VideoTracks
├── 📹 OpenCVVideoTrack      # Implementación OpenCV
└── 🍓 PiCamera2VideoTrack   # Implementación PiCamera2

📁 app.py                    # Servidor principal mejorado
├── ⚙️ Argumentos CLI        # Control desde línea de comandos
├── 📊 /camera-info          # Endpoint de información
└── 🔄 Auto-fallback         # Fallback automático entre cámaras
```

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
export CAMERA_TYPE=picamera2
export CAMERA_WIDTH=1280
export CAMERA_HEIGHT=720
export CAMERA_FPS=30
```

### Raspberry Pi - Configuración de Cámara
```bash
# Habilitar cámara
sudo raspi-config
# → Interfacing Options → Camera → Enable

# Verificar detección
vcgencmd get_camera

# Probar PiCamera2
python -c "from picamera2 import Picamera2; print('PiCamera2 OK')"
```

## 📊 Endpoints de API

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Interface web principal |
| `/offer` | POST | Negociación WebRTC |
| `/camera-info` | GET | Información del sistema |

### Ejemplo de `/camera-info`:
```json
{
  "platform": "raspberry_pi",
  "picamera_available": true,
  "recommended_camera": "picamera2",
  "available_cameras": ["PiCamera2", "OpenCV Camera 0"],
  "current_config": {
    "type": "picamera2",
    "width": 640,
    "height": 480,
    "fps": 30
  }
}
```

## 🐛 Solución de Problemas

### Raspberry Pi

**Error: PiCamera2 no disponible**
```bash
# Instalar dependencias del sistema
sudo apt update
sudo apt install -y python3-picamera2

# O usar el script de setup
python setup_raspberry.py
```

**Error: Cámara no detectada**
```bash
# Verificar hardware
vcgencmd get_camera
# Debería mostrar: supported=1 detected=1

# Habilitar en raspi-config
sudo raspi-config
```

**Error: Permisos**
```bash
# Añadir usuario al grupo video
sudo usermod -a -G video $USER
# Reiniciar sesión
```

### General

**Sin cámaras detectadas**
```bash
# Verificar cámaras disponibles
python app.py --info

# Probar diferentes IDs
python app.py --camera-type opencv --camera-id 1
```

**Problemas de rendimiento**
```bash
# Reducir resolución
python app.py --width 320 --height 240 --fps 15

# Verificar recursos
htop
```

## 🎨 Personalización

### Crear VideoTrack Personalizado
```python
from camera_module import VideoStreamTrack

class MyCustomVideoTrack(VideoStreamTrack):
    async def recv(self):
        # Tu implementación personalizada
        pass

# Registrar en CameraFactory
CameraFactory.register_track_type("custom", MyCustomVideoTrack)
```

### Filtros de Video en Tiempo Real
```python
# En camera_module.py, método recv()
# Añadir filtros OpenCV:
frame = cv2.GaussianBlur(frame, (15, 15), 0)  # Blur
frame = cv2.Canny(frame, 100, 200)            # Edge detection
```

## 📈 Rendimiento

### Benchmarks Típicos

| Plataforma | Resolución | FPS | CPU | Calidad |
|------------|------------|-----|-----|---------|
| **RPi 4** | 640x480 | 30 | ~25% | ⭐⭐⭐⭐ |
| **RPi 4** | 1280x720 | 30 | ~40% | ⭐⭐⭐⭐⭐ |
| **RPi 4** | 1920x1080 | 15 | ~60% | ⭐⭐⭐⭐⭐ |
| **Laptop** | 1280x720 | 60 | ~15% | ⭐⭐⭐⭐⭐ |

### Optimizaciones
- **PiCamera2**: Hardware encoding en Raspberry Pi
- **Auto-detección**: Selección automática del mejor método
- **Fallback**: Degradación elegante si hay problemas
- **Configuración dinámica**: Ajuste de parámetros sin reiniciar

## 🚀 Próximas Características

- [ ] Soporte para múltiples streams simultáneos
- [ ] Grabación automática en el servidor
- [ ] Filtros de video en tiempo real (blur, edges, etc.)
- [ ] Dashboard web para configuración
- [ ] Streaming a múltiples clientes
- [ ] Soporte para audio (micrófono)
- [ ] Integración con servicios de streaming (YouTube, Twitch)

## 🤝 Contribuir

1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-caracteristica`
3. Commit cambios: `git commit -m 'Añadir nueva característica'`
4. Push a la rama: `git push origin feature/nueva-caracteristica`
5. Crear Pull Request

## 📝 Notas de Desarrollo

- El módulo `camera_module.py` es completamente independiente
- Fácil añadir nuevos tipos de cámara implementando `VideoStreamTrack`
- Auto-detección basada en plataforma y hardware disponible
- Fallback automático garantiza que siempre funcione algo

---

**Desarrollado con ❤️ para la comunidad Raspberry Pi y WebRTC**
